from unittest import TestCase, skip
from dataCreator import DataScraper, Filings

class TestDataCreation(TestCase):
	"""Tests scrapping of EDGAR website"""

	def setUp(self):
		self.testScraper = DataScraper()

	@skip
	def test_maps_data_correctly(self):
		data_dict = self.testScraper.get_data_from_table_link('1564408',
			'https://www.sec.gov/Archives/edgar/data'
			+ '/1564408/000156459017022434/R4.htm')
		#. currently invalid test; needs some additional data added
		
		
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
		self.assertDictEqual(data_dict, correct_mapped_data)

	def test_values_correctly_formated(self):
		# tests the format_values function indirectly
		data_dict = self.testScraper.get_data_from_table_link( '1564408',
			'https://www.sec.gov/Archives/edgar/data'
			+ '/1564408/000156459017022434/R4.htm')
		for x in data_dict:
			self.assertIsInstance(data_dict[x][0],float)
			self.assertIsInstance(data_dict[x][1],float)

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

	def test_returns_correct_accession_number_from_filings_link(self):
		self.assertEqual(
			self.testScraper.extract_accession_number_from_filings_link(
			"https://www.sec.gov/cgi-bin/viewer?action=view&cik=1564408&"
			+ "accession_number=0001564590-17-022434&xbrl_type=v", 
			unformatted=True), '0001564590-17-022434')
		self.assertEqual(
			self.testScraper.extract_accession_number_from_filings_link(
			"https://www.sec.gov/cgi-bin/viewer?action=view&cik=1564408&"
			+"accession_number=0001564590-17-022434&xbrl_type=v"),
			'000156459017022434')

	def test_returns_correct_accession_number_from_table_link(self):
		self.assertEqual(
			self.testScraper.extract_accession_number_from_table_link(
				"https://www.sec.gov/Archives/edgar/data/1564408/" +
				"000156459017022434/R4.htm"),
			'000156459017022434')

	@skip
	def test_gets_tables_for_one_filing(self):
		link_to_filing = ("https://www.sec.gov/cgi-bin/viewer?action=view&" + 
			"cik=1564408&accession_number=0001564590-17-022434&xbrl_type=v")
		list_of_filings = self.testScraper.get_tables_for_one_filing(
			'1564408', link_to_filing)
		self.assertEqual("https://www.sec.gov/Archives/edgar/data/1564408/"
			+ "000156459017022434/R4.htm",list_of_filings['income'])
		self.assertEqual("https://www.sec.gov/Archives/edgar/data/1564408/"
			+ "000156459017022434/R2.htm",list_of_filings['balance'])
		self.assertEqual("https://www.sec.gov/Archives/edgar/data/1564408/"
			+ "000156459017022434/R6.htm",list_of_filings['cfs'])

	def test_gets_correct_time_period(self):
		f_q = self.testScraper.get_fiscal_year_and_quarter('1564408',
			"https://www.sec.gov/cgi-bin/viewer?action=view&cik=1564408"
			+ "&accession_number=0001564590-17-022434&xbrl_type=v#")
		self.assertEqual(f_q['year'], '2017')
		self.assertEqual(f_q['period_ended'], 'Q3')

class TestFilings(TestCase):

	def setUp(self):
		self.testFilings = Filings('1564408') # Snapchat cik

	def test_returns_dict(self):
		self.assertIsInstance(self.testFilings.raw_data, dict)
		print(self.testFilings.raw_data['2017Q1'])

	def test_set_latest_period(self):
		self.testFilings.set_latest_period({'period1' :{'some':'object', 
			'period2' : {'another': 'object'}}})
		self.assertEqual(self.testFilings.latest_period, 'period1')

	def test_returns_row_labels(self):
		self.testFilings.set_latest_period(self.testFilings.raw_data)
		self.assertIsInstance(
			self.testFilings.get_row_labels(self.testFilings.raw_data,
				self.testFilings.statement_keys[0]),
			list)
		self.assertIsInstance(
			self.testFilings.get_row_labels(self.testFilings.raw_data,
				self.testFilings.statement_keys[1])[0],
			str)

	@skip
	def test_picks_correct_compilation_function(self):
		self.fail("incomplete test")
		# tests select_data_creation_function()