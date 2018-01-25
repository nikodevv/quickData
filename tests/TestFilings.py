from unittest import TestCase, skip
import sys
import os
sys.path.insert(0, sys.path.insert(0, os.path.abspath('..')))
from dataCreator import DataScraper, Filings


class TestFilings(TestCase):
	"""
	Due to the messiness of data involved the
	"semantics" of the data generated is not tested.
	"""
	def setUp(self):
		self.testFilings = Filings('1564408') # Snapchat cik


	def test_run_compile_income_statement(self):
		"""
		regression test--checks to see whether the program
		returns the right kind of data
		"""
		self.testFilings.save_data_cols()
		self.assertIsInstance(self.testFilings.full_dict, dict)
		for timeperiod in self.testFilings.full_dict:
			self.assertIsInstance(timeperiod, str)
			self.assertIsInstance(
				self.testFilings.full_dict[timeperiod], dict)
			for statement in self.testFilings.full_dict[timeperiod]:
				self.assertIsInstance(statement, str)
				self.assertIsInstance(
					self.testFilings.full_dict[timeperiod][statement], list)
				for data in self.testFilings.full_dict[timeperiod][statement]:
					self.assertIsInstance(float(data), float)

	def test_Q4_generation(self):
		"""unit test"""
		pass