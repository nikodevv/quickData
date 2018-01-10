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