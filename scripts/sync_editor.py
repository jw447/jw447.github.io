"""Load local-design safely; synchronize clean checkouts without merging main."""
from pathlib import Path
import subprocess
import re

BRANCH = 'local-design'

def synchronize(root):
    def git(*args, check=True):
        result = subprocess.run(['git', '-C', str(root), *args], capture_output=True, text=True, timeout=20)
        if check and result.returncode:
            raise RuntimeError('Git sync failed: ' + result.stderr.strip())
        return result
    if Path(git('rev-parse', '--show-toplevel').stdout.strip()).resolve() != root.resolve():
        raise RuntimeError('Run the editor from the website repository.')
    if git('ls-files', '--unmerged').stdout.strip() or git('rev-parse', '--verify', 'MERGE_HEAD', check=False).returncode == 0:
        raise RuntimeError('Finish or abort your existing Git merge before opening the editor.')
    branch = git('branch', '--show-current').stdout.strip()
    dirty = bool(git('status', '--porcelain').stdout.strip())
    if dirty and branch != BRANCH:
        raise RuntimeError('Save or commit changes on your current branch, then switch to local-design. Nothing was overwritten.')
    remote = git('remote', 'get-url', 'origin', check=False).stdout.strip()
    warning = ''
    if re.fullmatch(r'(?:https://github\.com/|git@github\.com:)[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:\.git)?', remote):
        try:
            result = git('fetch', 'origin', '--prune', check=False)
            if result.returncode:
                warning = 'GitHub fetch failed; opening local files. Check authentication/network before publishing.'
        except subprocess.TimeoutExpired:
            warning = 'GitHub fetch timed out; opening local files.'
    else:
        warning = 'Set a GitHub origin remote to synchronize and publish. Opening local files.'
    if branch != BRANCH:
        if git('show-ref', '--verify', '--quiet', 'refs/heads/' + BRANCH, check=False).returncode == 0:
            git('switch', BRANCH)
        elif git('show-ref', '--verify', '--quiet', 'refs/remotes/origin/' + BRANCH, check=False).returncode == 0:
            git('switch', '--track', '-c', BRANCH, 'origin/' + BRANCH)
        else:
            raise RuntimeError('No local-design branch is available. Fetch or create it before opening the editor.')
    if dirty:
        return 'Opening saved local edits; automatic pull skipped. ' + warning
    if warning:
        return warning
    if git('show-ref', '--verify', '--quiet', 'refs/remotes/origin/' + BRANCH, check=False).returncode == 0:
        result = git('merge', '--ff-only', 'origin/' + BRANCH, check=False)
        if result.returncode:
            return 'Local and GitHub updates need reconciliation; opening local files. Resolve branch differences before publishing.'
    return 'Local-design loaded. Publish pushes local-design; merge into main yourself when ready.'

if __name__ == '__main__':
    import sys
    try: print(synchronize(Path(__file__).resolve().parents[1]), flush=True)
    except (RuntimeError, subprocess.TimeoutExpired) as error:
        print(str(error), file=sys.stderr); raise SystemExit(1)
