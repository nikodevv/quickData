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
		self.testFilings = Filings('0000814586') # LWAY cik 0000814586 
		# Snapchat cik 1564408


	def test_run_compile_income_statement(self):
		"""
		regression test--checks to see whether the program
		returns the right kind of data
		"""
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
		print(self.testFilings.full_dict)
		# print([period for period in self.testFilings.raw_data])
		# print(self.testFilings.raw_data['2015FY'])
	# def test_Q4_generation(self):
	# 	"""unit test"""
	# 	fy = {
	# 		'income': [4,3,2,1],
	# 		'balance': [1,2,3,4],
	# 		'cfs': [-1,2,4],
	# 	}
	# 	q1 = {
	# 		'income': [1,1,1,1],
	# 		'balance': [1,2,3,4],
	# 		'cfs': [1,1,1],
	# 	}
	# 	q2 = {
	# 		'income': [1,1,1,1],
	# 		'balance': [1,2,3,4],
	# 		'cfs': [2,2,2],
	# 	}
	# 	q3 = {
	# 		'income': [1,1,1,1],
	# 		'balance': [1,2,3,4],
	# 		'cfs': [-3,-3,-3] ,
	# 	}
	# 	q4 = {
	# 		'income': [1,0,-1,-2],
	# 		'balance': [-2,-4,-6,-8],
	# 		'cfs': [-1,2,4] ,
	# 	}

	# 	self.assertEqual(self.testFilings.generate_Q4_cols(fy, q1, q2, q3), q4)
	# 	