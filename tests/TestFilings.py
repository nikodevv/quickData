from unittest import TestCase, skip
import sys
import os
sys.path.insert(0, sys.path.insert(0, os.path.abspath('..')))
from dataCreator import DataScraper, Filings


class TestFilings(TestCase):
	"""
	Due to the messiness of data involved these tests
	are purely for debuging purposes. They take long to
	execute, and most are incomplete as preparing
	a static dataset for testing purposes is a LABOROUS
	enadvour that I will not attempt.
	"""
	def setUp(self):
		self.testFilings = Filings('1564408') # Snapchat cik

	# @skip
	# def test_returns_dict(self):

	# 	self.assertIsInstance(self.testFilings.raw_data, dict)
	# 	print(self.testFilings.raw_data['2017Q1']['income'])

	# def test_set_latest_period(self):
	# 	self.testFilings.set_latest_period({'period1' :{'some':'object', 
	# 		'period2' : {'another': 'object'}}})
	# 	self.assertEqual(self.testFilings.latest_period, 'period1')
	# 	# print(self.testFilings.raw_data['2017Q3']['income'])
	# @skip
	# def test_returns_row_labels(self):
	# 	self.testFilings.set_latest_period(self.testFilings.raw_data)
	# 	self.assertIsInstance(
	# 		self.testFilings.get_row_labels(self.testFilings.raw_data,
	# 			'income'),
	# 		list)
	# 	self.assertIsInstance(
	# 		self.testFilings.get_row_labels(self.testFilings.raw_data,
	# 			'balance')[0],
	# 		str)

	# 	@skip
	# def test_picks_correct_compilation_function(self):
	# 	self.fail("incomplete test")
	# 	# tests select_data_creation_function()


	def test_run_compile_income_statement(self):
		# print(
		# 	self.testFilings.compile_income_statement(self.testFilings.raw_data['2017Q1']
		# 		['income'])
		# 	)
		self.testFilings.prepare_row_labels('income', ['operati', 'taxes'], 
			['other operating income', 'other IS items'])
		data_col = self.testFilings.compile_income_statement(self.testFilings.raw_data['2017Q1']['income'], 'income')
		print(data_col)
		print("^ that was data_col, now we print labels")
		print(self.testFilings.income_row_labels)