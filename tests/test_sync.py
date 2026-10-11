import subprocess
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
from scripts.sync_editor import synchronize

class SyncTests(unittest.TestCase):
    def test_reopen_saved_content_and_sync_only_review_branch(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / 'site'; root.mkdir()
            remote = Path(folder) / 'remote.git'
            def git(*args):
                return subprocess.run(['git', '-C', str(root), *args], check=True, capture_output=True, text=True).stdout.strip()
            subprocess.run(['git', 'init', '--bare', str(remote)], check=True, capture_output=True)
            git('init', '-b', 'main'); git('config', 'user.name', 'Test'); git('config', 'user.email', 'test@example.org')
            (root / 'content.txt').write_text('initial'); git('add', '.'); git('commit', '-m', 'initial')
            git('remote', 'add', 'origin', str(remote)); git('push', '-u', 'origin', 'main')
            git('switch', '-c', 'local-design'); git('push', '-u', 'origin', 'local-design')
            git('switch', 'main'); (root / 'content.txt').write_text('new main'); git('commit', '-am', 'main update'); git('push')
            main_head = git('rev-parse', 'main')
            with patch('scripts.sync_editor.re.fullmatch', return_value=True):
                synchronize(root)
                self.assertEqual(git('branch', '--show-current'), 'local-design')
                self.assertEqual((root / 'content.txt').read_text(), 'initial')
                # A second checkout publishes updates while this editor has saved edits.
                peer = Path(folder) / 'peer'
                subprocess.run(['git', 'clone', '-b', 'local-design', str(remote), str(peer)], check=True, capture_output=True)
                def pg(*args):
                    subprocess.run(['git', '-C', str(peer), *args], check=True, capture_output=True)
                pg('config', 'user.name', 'Peer'); pg('config', 'user.email', 'peer@example.org')
                (peer / 'content.txt').write_text('remote update'); pg('commit', '-am', 'remote update'); pg('push')
                (root / 'content.txt').write_text('saved local')
                self.assertIn('automatic pull skipped', synchronize(root))
                self.assertEqual((root / 'content.txt').read_text(), 'saved local')
                git('restore', 'content.txt')
                synchronize(root)
                self.assertEqual((root / 'content.txt').read_text(), 'remote update')
                # Divergence permits local editing, without merging or discarding commits.
                (root / 'content.txt').write_text('local commit'); git('commit', '-am', 'local edit')
                (peer / 'content.txt').write_text('another remote'); pg('commit', '-am', 'remote edit'); pg('push')
                self.assertIn('reconciliation', synchronize(root))
                self.assertEqual((root / 'content.txt').read_text(), 'local commit')
                self.assertEqual(git('status', '--porcelain'), '')
                # Offline editing remains available.
                git('remote', 'set-url', 'origin', str(Path(folder) / 'missing.git'))
                self.assertIn('fetch failed', synchronize(root))
                self.assertEqual(git('rev-parse', 'main'), main_head)
                git('switch', 'main'); (root / 'content.txt').write_text('other branch edit')
                with self.assertRaisesRegex(RuntimeError, 'current branch'):
                    synchronize(root)
                self.assertEqual((root / 'content.txt').read_text(), 'other branch edit')
