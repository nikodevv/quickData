from unittest import TestCase, skip
import sys
import os
sys.path.insert(0, sys.path.insert(0, os.path.abspath('..')))
from dataCreator import DataScraper

class TestDataCreation(TestCase):
	"""Tests scrapping of EDGAR website"""

	def setUp(self):
		self.testScraper = DataScraper()

	def test_line_items_are_unique(self):
		line_items = self.testScraper.make_line_items_unique(['one', 'one', 'three', 'samsung', 'three'])
		for item in line_items:
			self.assertEqual(line_items.count(item), 1)

	def test_tree_data_is_valid(self):
		"""
		Integration test; checks whether
		the data is scrapped and formatted
		correctly
		"""
		data_dict = self.testScraper.get_data_from_table_link('1564408',
			'https://www.sec.gov/Archives/edgar/data'
			+ '/1564408/000156459017022434/R4.htm')
		self.assertIsInstance(data_dict, dict)
		for key in data_dict:
			self.assertIsInstance(data_dict[key], list)
			self.assertIsInstance(data_dict[key][0], float)
			self.assertIsInstance(data_dict[key][1], float)
			self.assertIsInstance(key, str)

	def test_values_correctly_formated(self):
		"""
		unit test; checks that number strings are cast to floats
		""" 
		values = ['$4000','(300,00)', '$(1,0)']
		for value in self.testScraper.format_values(values):
			self.assertIsInstance(value, float)

	def test_can_find_company_documents_from_cik(self):
		"""unit test"""
		cik = '1564408' # snapchat cik
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

	def test_can_find_accession_number_from_filing_link(self):
		"""unit test"""
		self.assertEqual(
			self.testScraper.extract_accession_number_from_filings_link(
				"https://www.sec.gov/cgi-bin/" + 
				"viewer?action=view&cik=1564408&accession_number=" + 
				"0001564590-17-010357&xbrl_type=v"),
			'000156459017010357')

	def test_can_find_accession_number_from_table_link(self):
		"""unit test"""
		self.assertEqual(
			self.testScraper.extract_accession_number_from_table_link(
				'https://www.sec.gov/Archives/edgar/data/1564408/000156459017010357/R2.htm'),
			'000156459017010357')


	def test_returns_the_right_filings(self):
		"""
		unit test; checks wheteher scrapper returns all 10-K or 10-Q filings
		exclusively
		"""
		
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

	def test_gets_table_links_for_one_filing(self):
		"""unit test"""
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
