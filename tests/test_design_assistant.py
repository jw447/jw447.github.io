import copy
import io
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from editor.content import bundle, read_content
from editor.design_assistant import CSS_PATH, validate_css, DesignAssistant
from scripts.editor_server import Editor, EditorError

ROOT = Path(__file__).resolve().parents[1]

class DesignAssistantTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / 'site'
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns('.git', 'dist', '.editor-state', '__pycache__', '.openai'))
        subprocess.run(['python3', 'build.py'], cwd=self.root, check=True, capture_output=True)
        self.editor = Editor(self.root)
        self.editor.assistant.key = ''

    def test_remember_key_restart_and_remove(self):
        with patch.dict('os.environ', {}, clear=True):
            assistant = DesignAssistant(self.root)
            result = assistant.configure(dict(key='test-secret', model='gpt-5.4', remember=True))
            self.assertTrue(result['remembered'])
            self.assertNotIn('test-secret', json.dumps(result))
            self.assertEqual(assistant.credentials_path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(DesignAssistant(self.root).key, 'test-secret')
            assistant.configure(dict(key='session-secret', remember=False))
            self.assertFalse(assistant.credentials_path.exists())
            self.assertFalse(DesignAssistant(self.root).key)

    def tearDown(self):
        if self.editor.preview: self.editor.preview.cleanup()
        self.temp.cleanup()

    def propose(self):
        design = copy.deepcopy(read_content(self.root)['design'])
        design['spacing']['section_gap'] = 32
        reply = dict(answer='Reduce section spacing and soften the header border.', design_json=json.dumps(design), css='.site-header{border-bottom-width:2px}\n')
        raw = dict(status='completed', output=[dict(type='message', content=[dict(type='output_text', text=json.dumps(reply))])])
        self.editor.design_configure(dict(key='test-secret-key', model='gpt-5.4'))
        (self.root / '.env').write_text('PRIVATE_SECRET=never-send-this')
        with patch('editor.design_assistant.urlopen', return_value=io.BytesIO(json.dumps(raw).encode())) as called:
            result = self.editor.design_chat(dict(message='Tighten the page spacing.'))
            request = called.call_args.args[0]
            sent = json.loads(request.data)
            self.assertFalse(sent['store'])
            self.assertEqual(sent['text']['format']['type'], 'json_schema')
            self.assertNotIn('test-secret-key', request.data.decode())
            self.assertNotIn('PRIVATE_SECRET', request.data.decode())
            self.assertIn('current_pages_html', sent['instructions'])
        return result['proposal']['id']

    def test_connect_preview_apply_and_stale_source_protection(self):
        with self.assertRaisesRegex(ValueError, 'API key'): self.editor.design_chat(dict(message='Change colors'))
        before = read_content(self.root)
        id = self.propose()
        self.assertNotIn('test-secret-key', json.dumps(self.editor.assistant.status()))
        self.editor.design_preview(dict(proposal_id=id))
        self.assertEqual(read_content(self.root), before)
        self.assertFalse((self.root / CSS_PATH).exists())
        preview = Path(self.editor.preview.name) / 'dist'
        self.assertIn('assistant-design.css', (preview / 'index.html').read_text())
        self.assertIn('border-bottom-width:2px', (preview / CSS_PATH).read_text())
        applied = self.editor.design_apply(dict(proposal_id=id))
        self.assertEqual(applied['bundle']['content']['news'], before['news'])
        self.assertEqual(read_content(self.root)['design']['spacing']['section_gap'], 32)
        self.assertTrue(list((self.root / '.editor-state/backups').glob('*/design.json')))
        id = self.propose()
        (self.root / 'assets/style.css').write_text('/* source changed */')
        with self.assertRaisesRegex(ValueError, 'website changed'):
            self.editor.design_apply(dict(proposal_id=id))

    def test_model_styles_are_bounded_and_failed_build_does_not_apply(self):
        for css in ['@import "https://example.org/a.css";', 'body{background:url(https://example.org)}', r'body{background:u\rl(x)}', 'body{']:
            with self.assertRaises(ValueError): validate_css(css)
        id = self.propose(); before = read_content(self.root)
        with patch.object(self.editor, 'build_preview', side_effect=EditorError('failed build')):
            with self.assertRaises(EditorError): self.editor.design_apply(dict(proposal_id=id))
        self.assertEqual(read_content(self.root), before)
        self.assertFalse((self.root / CSS_PATH).exists())

    def test_design_publish_targets_review_and_keeps_main(self):
        remote = Path(self.temp.name) / 'remote.git'
        subprocess.run(['git','init','--bare',str(remote)],check=True,capture_output=True)
        def git(*args):
            return subprocess.run(['git','-C',str(self.root),*args],check=True,capture_output=True,text=True).stdout.strip()
        git('init','-b','local-design'); git('config','user.name','Test');git('config','user.email','test@example.org')
        git('add','.');git('commit','-m','initial');git('branch','main')
        main = git('rev-parse','main');git('remote','add','origin',str(remote));git('push','origin','local-design','main')
        id = self.propose(); self.editor.design_apply(dict(proposal_id=id))
        # A content publish cannot accidentally include applied design changes.
        with patch.object(self.editor,'github_remote',return_value=True):
            with self.assertRaises(EditorError):self.editor.publish(bundle(self.root))
            result = self.editor.design_publish({})
        self.assertTrue(result['push_status']['confirmed'])
        self.assertEqual(git('rev-parse','origin/local-design'), result['commit'])
        self.assertEqual(git('rev-parse','origin/main'), main)
        self.assertIn('Update website design',git('log','-1','--format=%B'))
