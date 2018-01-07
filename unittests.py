import unittest
from dataCreator import DataScraper

class TestDataCreation(unittest.TestCase):
	"""Tests scrapping of EDGAR website"""
	def setUp(self):
		testScraper = DataScraper('https://www.sec.gov/Archives/edgar/data/'
			+ '1564408/000156459017022434/R4.htm') # Snapchat Sept 30 2017 10-Q

	def test_can_pull_data_from_link(self):
		self.assertTrue(testScrapper.line_items)
		self.assertTrue(testScrapper.values)
		self.assertContains(testScrapper.line_items[-1],'earnings')