import unittest
from bibliography import citation, from_metadata

class BibliographyTests(unittest.TestCase):
    def test_publisher_dates_author_names_and_pagination(self):
        meta = dict(type='journal-article', title=['An HPC & AI Study'], author=[dict(given='Jinzhen',family='Wang')],
                    **{'container-title':['IEEE Transactions on Big Data'], 'published-print':{'date-parts':[[2023]]}},
                    DOI='10.1109/example', volume='9', issue='1', page='22-36', publisher='IEEE')
        data = from_metadata(meta)
        result = citation(dict(id='paper',title='Local title',authors='Local Author',venue='Local venue',year=2021,citation=data))
        self.assertIn('@article{paper', result)
        self.assertIn('author = {Wang, Jinzhen}', result)
        self.assertIn('year = {2023}', result)
        self.assertIn('pages = {22--36}', result)
        self.assertIn(r'HPC \& AI', result)
        self.assertEqual(citation(dict(bibtex='@misc{exported}')), '@misc{exported}')
