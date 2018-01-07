from unittest import TestCase, skip
from dataCreator import DataScraper

class TestDataCreation(TestCase):
	"""Tests scrapping of EDGAR website"""

	def setUp(self):
		self.testScraper = DataScraper('https://www.sec.gov/Archives/edgar/data/'
			+ '1564408/000156459017022434/R4.htm') # Snapchat Sept 30 2017 10-Q

	def test_can_pull_data_from_link(self):
		self.assertTrue(self.testScraper.line_items)
		self.assertTrue(self.testScraper.values)
		self.assertIn(self.testScraper.line_items[-1],'Diluted')

	@skip
	def test_maps_data_correctly(self):
		correct_mapped_data = {
		'Revenue': '2'

		}

		self.mappedData = self.testScraper.mappedData()

	def test_output_data(self):
		self.fail(self.testScraper.line_items)