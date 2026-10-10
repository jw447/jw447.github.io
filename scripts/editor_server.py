#!/usr/bin/env python3
"""Run the optional loopback-only editor: python3 scripts/editor_server.py."""
import argparse
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
import threading
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from editor.content import bundle, read_content, revision, validate
from editor.schema import CONTENT_NAMES


class EditorError(Exception):
    def __init__(self, message, status=400, **extra):
        super().__init__(message)
        self.status, self.extra = status, extra


class Editor:
    def __init__(self, root):
        self.root = root.resolve()
        self.preview = None
        self.lock = threading.Lock()
        self.token = secrets.token_urlsafe(32)
        self.state = self.root / '.editor-state'
        self.pending_path = self.state / 'pending-publish.json'

    def git(self, *args, timeout=30):
        result = subprocess.run(['git', '-C', str(self.root), *args], capture_output=True, text=True, timeout=timeout)
        if result.returncode:
            raise EditorError('Git could not complete this step. Check the local repository, GitHub authentication, and network, then try again.', 409)
        return result.stdout.strip()

    @staticmethod
    def github_remote(url):
        return bool(re.fullmatch(r'(?:https://github\.com/|git@github\.com:)[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:\.git)?', url))

    def publishing_status(self):
        try:
            if Path(self.git('rev-parse', '--show-toplevel')).resolve() != self.root:
                return dict(ready=False, reason='Open the editor from the website repository root.')
            remote = self.git('remote', 'get-url', '--push', 'origin')
            if not self.github_remote(remote):
                return dict(ready=False, reason='Publishing needs a GitHub origin remote. Preview and saving are available.')
            branch = self.git('branch', '--show-current')
            if branch != 'main':
                return dict(ready=False, reason='Switch to the main branch to publish; other branches support preview and saving.')
            return dict(ready=True, repository=remote, branch=branch)
        except (EditorError, subprocess.TimeoutExpired, FileNotFoundError):
            return dict(ready=False, reason='Publishing needs Git and a local checkout of the GitHub website repository.')

    def candidate(self, payload):
        if not isinstance(payload, dict) or payload.get('schema_version') != 1:
            raise EditorError('Import an editor content package, version 1.')
        baseline = read_content(self.root)
        if payload.get('base_revision') != revision(baseline):
            raise EditorError('The source content changed since this draft was loaded. Download your draft, then load the current content before applying it.', 409)
        errors = validate(payload.get('content'), baseline)
        if errors:
            raise EditorError('Please fix the highlighted content fields.', errors=errors)
        return payload['content']

    def build_preview(self, data):
        temporary = tempfile.TemporaryDirectory(prefix='hpdi-editor-')
        folder = Path(temporary.name)
        try:
            shutil.copytree(self.root / 'content', folder / 'content')
            legacy_path=self.root / 'content/legacy.json'
            if legacy_path.exists():
                legacy=json.loads(legacy_path.read_text())
                for name in legacy['files']:
                    target=folder/name
                    target.parent.mkdir(parents=True,exist_ok=True)
                    shutil.copy2(self.root/name,target)
                for name in legacy['directories']:
                    shutil.copytree(self.root/name,folder/name,ignore=shutil.ignore_patterns('.DS_Store'))
            for name in CONTENT_NAMES:
                (folder / 'content' / f'{name}.json').write_text(json.dumps(data[name], ensure_ascii=False, indent=2) + '\n')
            for source in ('build.py', 'simple_layout.py', 'publication_format.py'):
                shutil.copy2(self.root / source, folder / source)
            shutil.copytree(self.root / 'editor', folder / 'editor', ignore=shutil.ignore_patterns('__pycache__'))
            shutil.copytree(self.root / 'assets', folder / 'assets', dirs_exist_ok=True)
            (folder / 'scripts').mkdir()
            shutil.copy2(self.root / 'scripts/check_site.py', folder / 'scripts/check_site.py')
            for script in ('build.py', 'scripts/check_site.py'):
                result = subprocess.run([sys.executable, script], cwd=folder, capture_output=True, text=True, timeout=45)
                if result.returncode:
                    raise EditorError('The generated site did not pass its checks. ' + (result.stdout + result.stderr)[-2000:])
            return temporary
        except Exception:
            temporary.cleanup()
            raise

    def preview_content(self, payload):
        temporary = self.build_preview(self.candidate(payload))
        previous = self.preview
        self.preview = temporary
        if previous: previous.cleanup()
        return dict(ok=True, preview_url='/preview/compact/index.html')

    def save(self, payload):
        data = self.candidate(payload)
        temporary = self.build_preview(data)
        current = read_content(self.root)
        # Recheck after the build in case an assistant or another editor changed files.
        if payload['base_revision'] != revision(current):
            temporary.cleanup()
            raise EditorError('The content changed during validation. Download your draft and reload current content.', 409)
        changed = [name for name in CONTENT_NAMES if data[name] != current[name]]
        if changed:
            backup = self.state / 'backups' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
            backup.mkdir(parents=True)
            for name in changed: shutil.copy2(self.root / 'content' / f'{name}.json', backup / f'{name}.json')
            try:
                for name in changed:
                    target = self.root / 'content' / f'{name}.json'
                    stage = target.with_suffix('.json.editor-tmp')
                    stage.write_text(json.dumps(data[name], ensure_ascii=False, indent=2) + '\n')
                    stage.replace(target)
                shutil.copytree(Path(temporary.name) / 'dist', self.root / 'dist', dirs_exist_ok=True)
            except Exception:
                for name in changed: shutil.copy2(backup / f'{name}.json', self.root / 'content' / f'{name}.json')
                raise
        temporary.cleanup()
        return dict(ok=True, bundle=bundle(self.root), changed=changed)

    def publish(self, payload):
        status = self.publishing_status()
        if not status['ready']: raise EditorError(status['reason'], 409)
        outside = self.git('diff', '--name-only', 'HEAD').splitlines()
        allowed = {f'content/{name}.json' for name in CONTENT_NAMES}
        if any(path not in allowed and not path.startswith('dist/') for path in outside):
            raise EditorError('There are code or layout changes outside the editor. Commit or discard them separately before publishing content.', 409)
        if self.pending_path.exists():
            pending = json.loads(self.pending_path.read_text())
            if self.git('rev-parse', 'HEAD') != pending['commit'] or outside:
                raise EditorError('A previous publish needs attention. Finish pushing its commit before making another content publish.', 409)
            if revision(self.candidate(payload)) != revision(read_content(self.root)):
                raise EditorError('Push the previous saved commit before publishing this new draft.', 409)
        else:
            self.git('fetch', 'origin', 'main', timeout=45)
            if self.git('rev-parse', 'HEAD') != self.git('rev-parse', 'origin/main'):
                raise EditorError('Local and GitHub history differ. Synchronize the main branch before publishing.', 409)
            saved = self.save(payload)
            paths = [f'content/{name}.json' for name in CONTENT_NAMES] + ['dist']
            if not self.git('ls-files', '--', 'dist'):
                paths.remove('dist')  # GitHub Actions rebuilds ignored output from source.
            self.git('add', '--', *paths)
            if not self.git('diff', '--cached', '--name-only'):
                return dict(ok=True, message='No content changes to publish.', bundle=saved['bundle'])
            try:
                self.git('commit', '-m', 'Update website content through browser editor')
            except EditorError:
                raise EditorError('Content is saved locally, but Git could not create the commit. Check your Git name/email configuration.', 409, saved=True)
            pending = dict(commit=self.git('rev-parse', 'HEAD'))
            self.state.mkdir(exist_ok=True)
            self.pending_path.write_text(json.dumps(pending))
        try:
            self.git('push', 'origin', 'HEAD:main', timeout=45)
        except (EditorError, subprocess.TimeoutExpired):
            raise EditorError('The content commit is saved locally, but GitHub did not confirm the push. Check authentication/network and click Publish again to retry this commit.', 409, saved=True, committed=True, commit=pending['commit'], bundle=bundle(self.root))
        self.pending_path.unlink(missing_ok=True)
        return dict(ok=True, commit=pending['commit'], bundle=bundle(self.root), message='Pushed to GitHub. The Pages workflow will build and deploy the update.')


def make_handler(editor):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args): pass

        def trusted_host(self):
            return self.headers.get('Host') == f'127.0.0.1:{self.server.server_port}'

        def reply(self, value, status=200):
            raw = json.dumps(value, ensure_ascii=False).encode()
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.end_headers()
            self.wfile.write(raw)

        def do_GET(self):
            if not self.trusted_host(): return self.reply(dict(error='Invalid host.'), 403)
            path = unquote(urlparse(self.path).path)
            if path == '/api/status':
                return self.reply(dict(mode='local', token=editor.token, bundle=bundle(editor.root), publishing=editor.publishing_status()))
            if path.startswith('/api/'): return self.reply(dict(error='Unknown endpoint.'), 404)
            root = editor.root / 'dist'
            if path.startswith('/preview/'):
                if not editor.preview: return self.reply(dict(error='Generate a preview first.'), 404)
                root = Path(editor.preview.name) / 'dist'
                path = path[len('/preview'):]
            target = (root / path.lstrip('/')).resolve()
            if target.is_dir(): target /= 'index.html'
            if not target.is_relative_to(root.resolve()) or not target.is_file() or any(p.startswith('.') for p in target.relative_to(root.resolve()).parts):
                return self.reply(dict(error='File not found.'), 404)
            raw = target.read_bytes()
            self.send_response(200)
            self.send_header('Content-Type', mimetypes.guess_type(target)[0] or 'application/octet-stream')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.end_headers()
            self.wfile.write(raw)

        def do_POST(self):
            origin = f'http://127.0.0.1:{self.server.server_port}'
            if not self.trusted_host() or self.headers.get('Origin') != origin or not secrets.compare_digest(self.headers.get('X-Editor-Token', ''), editor.token):
                return self.reply(dict(error='Open the editor on this computer to make changes.'), 403)
            if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
                return self.reply(dict(error='JSON content is required.'), 415)
            try: length = int(self.headers.get('Content-Length', '0'))
            except ValueError: return self.reply(dict(error='Invalid request size.'), 400)
            if not 0 < length <= 1000000: return self.reply(dict(error='Content package is too large or empty.'), 413)
            if not editor.lock.acquire(blocking=False): return self.reply(dict(error='Another editor operation is running. Try again when it finishes.'), 409)
            try:
                payload = json.loads(self.rfile.read(length))
                action = {'/api/preview': editor.preview_content, '/api/save': editor.save, '/api/publish': editor.publish}.get(urlparse(self.path).path)
                if not action: raise EditorError('Unknown editor action.', 404)
                self.reply(action(payload))
            except EditorError as error: self.reply(dict(error=str(error), **error.extra), error.status)
            except (ValueError, TypeError): self.reply(dict(error='The content package could not be read.'), 400)
            except subprocess.TimeoutExpired: self.reply(dict(error='The operation timed out. Check the repository state before retrying.'), 504)
            except Exception: self.reply(dict(error='The operation failed. Your draft remains in the browser; download it before restarting.'), 500)
            finally: editor.lock.release()
    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    if not (ROOT / 'dist/admin/index.html').exists():
        subprocess.run([sys.executable, str(ROOT / 'build.py')], check=True)
    editor = Editor(ROOT)
    server = ThreadingHTTPServer(('127.0.0.1', args.port), make_handler(editor))
    print(f'Open http://127.0.0.1:{server.server_port}/admin/ in your browser. Ctrl+C stops the editor.', flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally:
        server.server_close()
        if editor.preview: editor.preview.cleanup()


if __name__ == '__main__': main()
