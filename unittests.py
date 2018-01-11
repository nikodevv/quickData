from unittest import TestCase, skip
from dataCreator import DataScraper

class TestDataCreation(TestCase):
	"""Tests scrapping of EDGAR website"""

	def setUp(self):
		self.testScraper = DataScraper('https://www.sec.gov/Archives/edgar/data'
			+ '/1564408/000156459017022434/R4.htm') # Snapchat Sept 30 2017 10-Q

	def test_can_pull_data_from_link(self):
		self.assertTrue(self.testScraper.line_items)
		self.assertTrue(self.testScraper.values)
		self.assertIn(self.testScraper.line_items[-1],'Diluted')

	def test_maps_data_correctly(self):
		self.maxDiff = None
		correct_mapped_data = {
		'Revenue': [128204,207937],
		'Cost of revenue': [127780, 210710],
		'Research and development': [54562, 239442],
		'Sales and marketing': [34658, 101511],
		'General and administrative': [42172, 118101],
		'Total costs and expenses': [259172, 669764],
		'Loss from operations': [-130968, -461827],
		'Interest income': [1938, 6253],
		'Interest expense': [-648,-887],
		'Other income (expense), net': [-1421, 1002],
		'Loss before income taxes': [-131099, -455459],
		'Income tax benefit (expense)': [6871, 12300],
		'Net loss': [-124228, -443159],
		'Basic': [float(-0.15),float(-0.36)],
		'Diluted': [float(-0.15), float(-0.36)]
		}
		self.assertDictEqual(self.testScraper.mappedData, correct_mapped_data)

	@skip
	def test_output_data(self):
		self.fail(self.testScraper.line_items)

	def test_values_correctly_formated(self):
		for x in self.testScraper.values:
			self.assertIsInstance(x,float)

	def test_can_find_company_documents_from_cik(self):
		cik = '1564408'
		links_to_filings = self.testScraper.find_filings(cik)
		self.assertEqual(links_to_filings[0], "https://www.sec.gov/cgi-bin/" +
			"viewer?action=view&cik=1564408&accession_number=" + 
			"0001564590-17-022434&xbrl_type=v")
		self.assertEqual(links_to_filings[1], "https://www.sec.gov/cgi-bin/" +
			"viewer?action=view&cik=1564408&accession_number=" +
			"0001564590-17-017303&xbrl_type=v")
		self.assertEqual(links_to_filings[2], "https://www.sec.gov/cgi-bin/" + 
			"viewer?action=view&cik=1564408&accession_number=" + 
			"0001564590-17-010357&xbrl_type=v")

	@skip
	def test_can_categorize_filings(self):
		# currently invalid test
		link_to_10Q = ("https://www.sec.gov/cgi-bin/viewer?action=view&" + 
			"cik=1564408&accession_number=0001564590-17-022434&xbrl_type=v")
		# wtf
		# techinically this is a link to a 10-K/A, but the two should work 
		# the same.
		link_to_10K = ("https://www.sec.gov/cgi-bin/viewer?action=view&cik" + 
			"=814586&accession_number=0001683168-17-000858&xbrl_type=v")
		self.assertEqual(self.testScraper.categorize_filing(link_to_10Q),'10-Q')
		self.assertEqual(self.testScraper.categorize_filing(link_to_10K),'10-K')

	def test_returns_the_right_filings(self):
		# checks wheteher scrapper returns all 10-K or 10-Q filings
		# exclusively..
		
		list_of_10ks = ["https://www.sec.gov/cgi-bin/viewer?action=view" +
		 "&cik=814586&accession_number=0001683168-17-000864&xbrl_type=v",
		 "https://www.sec.gov/cgi-bin/viewer?action=view&cik=814586&" +
		 "accession_number=0001683168-17-000858&xbrl_type=v",
		 "https://www.sec.gov/cgi-bin/viewer?action=view&cik=814586&" + 
		 "accession_number=0001072613-16-000724&xbrl_type=v",
		 "https://www.sec.gov/cgi-bin/viewer?action=view&cik=814586&" + 
		 "accession_number=0001072613-15-000376&xbrl_type=v",
		 "https://www.sec.gov/cgi-bin/viewer?action=view&cik=814586&" + 
		 "accession_number=0001072613-14-000203&xbrl_type=v",
		 "https://www.sec.gov/cgi-bin/viewer?action=view&cik=814586&" + 
		 "accession_number=0001072613-13-000192&xbrl_type=v",
		 "https://www.sec.gov/cgi-bin/viewer?action=view&cik=814586&" +
		 "accession_number=0001072613-12-000279&xbrl_type=v"
		]

		self.assertEqual(list_of_10ks, 
			self.testScraper.find_filings('0000814586', filing_type='10-K',))

	def test_can_create_filings(self):
		self.maxDiff = None
		correct_mapped_data = {
		'Revenue': [128204,207937],
		'Cost of revenue': [127780, 210710],
		'Research and development': [54562, 239442],
		'Sales and marketing': [34658, 101511],
		'General and administrative': [42172, 118101],
		'Total costs and expenses': [259172, 669764],
		'Loss from operations': [-130968, -461827],
		'Interest income': [1938, 6253],
		'Interest expense': [-648,-887],
		'Other income (expense), net': [-1421, 1002],
		'Loss before income taxes': [-131099, -455459],
		'Income tax benefit (expense)': [6871, 12300],
		'Net loss': [-124228, -443159],
		'Basic': [float(-0.15),float(-0.36)],
		'Diluted': [float(-0.15), float(-0.36)]
		}
		self.assertDictEqual(self.testScraper.mappedData
			, correct_mapped_data)

	def returns_correct_accession_numbers(self):
		self.assertEqual(self.testScraper.returns_correct_accession_numbers(
			"https://www.sec.gov/cgi-bin/viewer?action=view&cik=1564408&"
			+ "accession_number=0001564590-17-022434&xbrl_type=v", 
			unformatted=True), '0001564590-17-022434')
		self.assertEqual(self.testScraper.returns_correct_accession_numbers(
			"https://www.sec.gov/cgi-bin/viewer?action=view&cik=1564408&"
			+"accession_number=0001564590-17-022434&xbrl_type=v"),
			'000156459017022434')