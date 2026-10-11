import subprocess
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
from scripts.sync_editor import synchronize

class SyncTests(unittest.TestCase):
    def test_main_updates_merge_into_review_and_dirty_changes_are_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / 'site'; root.mkdir()
            remote = Path(folder) / 'remote.git'
            def git(*args):
                return subprocess.run(['git', '-C', str(root), *args], check=True, capture_output=True, text=True).stdout.strip()
            subprocess.run(['git', 'init', '--bare', str(remote)], check=True, capture_output=True)
            git('init', '-b', 'main'); git('config', 'user.name', 'Test'); git('config', 'user.email', 'test@example.org')
            (root / 'content.txt').write_text('initial'); git('add', '.'); git('commit', '-m', 'initial')
            git('remote', 'add', 'origin', str(remote)); git('push', '-u', 'origin', 'main')
            git('switch', '-c', 'local-design'); (root / 'review.txt').write_text('review'); git('add', '.'); git('commit', '-m', 'review'); git('push', '-u', 'origin', 'local-design')
            git('switch', 'main'); (root / 'content.txt').write_text('new main'); git('commit', '-am', 'main update'); git('push')
            with patch('scripts.sync_editor.re.fullmatch', return_value=True):
                synchronize(root)
                self.assertEqual(git('branch', '--show-current'), 'local-design')
                self.assertEqual((root / 'content.txt').read_text(), 'new main')
                self.assertTrue((root / 'review.txt').exists())
                (root / 'content.txt').write_text('unsaved')
                with self.assertRaisesRegex(RuntimeError, 'local changes'): synchronize(root)
                self.assertEqual((root / 'content.txt').read_text(), 'unsaved')
