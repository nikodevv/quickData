from unittest import TestCase, skip
import sys
import os
sys.path.insert(0, sys.path.insert(0, os.path.abspath('..')))
from dataCreator import DataScraper, Filings

class TestFilings(TestCase):

	def setUp(self):
		self.testFilings = Filings('1564408') # Snapchat cik

	@skip
	def test_returns_dict(self):
		self.assertIsInstance(self.testFilings.raw_data, dict)
		print(self.testFilings.raw_data['2017Q1']['income'])

	@skip
	def test_set_latest_period(self):
		self.testFilings.set_latest_period({'period1' :{'some':'object', 
			'period2' : {'another': 'object'}}})
		self.assertEqual(self.testFilings.latest_period, 'period1')

	@skip
	def test_returns_row_labels(self):
		self.testFilings.set_latest_period(self.testFilings.raw_data)
		self.assertIsInstance(
			self.testFilings.get_row_labels(self.testFilings.raw_data,
				'income'),
			list)
		self.assertIsInstance(
			self.testFilings.get_row_labels(self.testFilings.raw_data,
				'balance')[0],
			str)

	def test_run_compile_income_statement(self):
		print(
			self.testFilings.compile_income_statement(self.testFilings.raw_data['2017Q1'],
				['income'])
			)
	
	@skip
	def test_picks_correct_compilation_function(self):
		self.fail("incomplete test")
		# tests select_data_creation_function()
