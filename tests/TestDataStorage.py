from unittest import TestCase, skip
import sys
import os
from time import time, sleep
sys.path.insert(0, sys.path.insert(0, os.path.abspath('..')))
from dataCreator import DataScraper, Filings, CreateFiles


class TestDataStorage(TestCase):
	"""
	When testing remove cik's from __init__ in CreateFiles to 
	speed up execution time
	"""
	def setUp(self):
		self.Creator = CreateFiles(['1564408'])

	def test_creates_files_when_necessary(self):
		cik = '1564408'
		# Will fail if no snapchap data file
		self.assertTrue(self.Creator.file_exists(cik, reparse=False))
		start_time = time()
		self.assertTrue(os.path.getmtime(os.path.abspath(os.path.join(
			os.path.dirname( __file__ ), f'../data/{cik}-labels.txt'))) < start_time)

	def test_overrides_when_reparse_passed(self):
		cik = '1564408'
		self.assertFalse(self.Creator.file_exists(cik, reparse=True))
		start_time = time()
		self.Creator.create_company_files(cik)
		self.assertTrue(os.path.getmtime(os.path.abspath(os.path.join(
			os.path.dirname( __file__ ), f'../data/{cik}-labels.txt'))) > start_time)
		
	def test_file_are_found_only_when_exist(self):
		cik = '1564408'
		fake_cik = '-1'
		self.assertTrue(self.Creator.file_exists(cik, reparse=False))
		self.assertFalse(self.Creator.file_exists(cik, reparse=True))
		self.assertFalse(self.Creator.file_exists(fake_cik, reparse=False))
		self.assertFalse(self.Creator.file_exists(fake_cik, reparse=True))