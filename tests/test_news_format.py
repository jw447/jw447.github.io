import unittest
from news_format import render_news_text
from project_portfolio import project_detail, project_cards

class NewsFormattingTests(unittest.TestCase):
    def test_formatting_and_balancing(self):
        self.assertEqual(render_news_text('A <b>bold <i>word</i></b><br><u>line</u>'), 'A <strong>bold <em>word</em></strong><br><u>line</u>')
        self.assertEqual(render_news_text('<strong>open'), '<strong>open</strong>')

    def test_arbitrary_html_cannot_execute(self):
        result = render_news_text('<img src=x onerror=alert(1)><strong onclick="evil()">safe</strong><script>evil()</script>')
        self.assertNotIn('<img', result)
        self.assertNotIn('<script', result)
        self.assertIn('<strong>safe</strong>', result)
        self.assertNotIn('<strong onclick', result)

    def test_project_card_summary_and_single_paper_link(self):
        project = dict(id='example', name='Project', subtitle='paper-id', description='Full overview', summary='Compact introduction', publication_ids=['paper'])
        self.assertIn('Compact introduction', project_cards([project]))
        self.assertNotIn('paper-id', project_cards([project]))
        paper = dict(id='paper', title='Title', authors='Authors', short='Venue', year=2024, links=[dict(label='Paper', url='https://example.org/paper'), dict(label='DOI', url='https://doi.org/example')])
        self.assertEqual(project_detail(project, [paper]).count('Paper →'), 1)
