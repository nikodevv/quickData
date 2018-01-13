from lxml.html import fromstring
import requests
import re
from fuzzywuzzy import fuzz

class DataScraper():
	"""Scraps income statement of a given company, aligning historical data"""

	def get_data_from_table_link(self, cik, link_to_table):
		"""
		Returns dictionary containing data table such that
		{'line item' : [current yr and period value, last year and period value]}
		example:
		{'income': [amt of income Q2 of 2017, amt of income Q2 of 2016]}
		"""
		tree = DataScraper.create_tree(self, link_to_table)
		line_items = tree.xpath('//td[@class="pl "]/a/text()|//td[@class="pl "]/a/strong/text()')
		values = tree.xpath('//td[@class="nump" or @class="num" or @class="text"]/text()')		
		return DataScraper.mapData(self, cik, line_items, 
			DataScraper.format_values(self, values), link_to_table)

	def create_tree(self, link):
		"""returns tree that can be searched via xpath"""
		return fromstring(requests.get(link).content)

	def format_values(self, values):
		# helper function; makes sure the values elements of raw data are all 
		# valid types
		def correctSign(x):
			if str(x)[0] == "(":
				return '-'+x.strip('(').strip(')')
			else:
				return x
		values = [x.strip('$ ') for x in values if x != '\n']
		values = [x.replace(',' , '') for x in values]
		temp_values = []
		for x in values:
			try: temp_values.append(float(correctSign(x)))
			except: temp_values.append(float(0))
		return temp_values

	def mapData(self, cik, line_items, values, link_to_table):
		# helper function; combines names & values into a single
		# dictionary. Since SEC filings for Q1 and FY look different than 
		# all other filings (tables have 2 columns fewer), scraping rules
		# vary
		tempValues = []
		# Should refactor such that page is passed as an argument
		page = requests.get(link_to_table)
		period_ended = DataScraper.get_fiscal_year_and_quarter(self, 
			cik, link_to_table, from_table_link=True)['period_ended']
		if (period_ended == 'Q1' or period_ended == 'FY' or 
			'Consolidated Balance Sheets' in page.text or 
			'Consolidated Statements of Cash' in page.text):
			for i in range(0, len(values), 2):
				#print(line_items[0])
				tempValues.append([values[i+1], values[i]])
			return dict(zip(line_items, tempValues))

		for i in range(0, len(values), 4):
			tempValues.append([values[i+1], values[i]])
		return dict(zip(line_items, tempValues))

	def find_filings(self, cik, filing_type="10-"):
		"""
		Returns links to all financial filings which are available for
		scrapping for a given cik. The type of filigns can be filtered for via
		type_. i.e. type_ = '10-K', will only return 10-Ks 	
		"""
		page = requests.get('https://www.sec.gov/cgi-bin/browse-edgar?' + 
			f'action=getcompany&CIK={cik}&type={filing_type}&dateb=&owner='
			+ 'include&count=100')
		tree = fromstring(page.content)
		filing_links = tree.xpath('//a[@id="interactiveDataBtn"]/@href')
		filing_links = [f'https://www.sec.gov{x}' for x in filing_links]
		return filing_links

	def extract_accession_number_from_filings_link(self, link_to_filing, 
		unformatted=False):
		"""
		Takes a link to interactive SEC filing and returns accession #
		"""
		accession_number = re.search('accession_number=(.+?)&', 
			link_to_filing).group(1)
		if unformatted == True:
			return accession_number
		return re.sub('[-]', '', accession_number)

	def extract_accession_number_from_table_link(self,link_to_table):
		"""
		Takes a link to SEC filing table and returns accession #
		"""
		accession_number = re.search('/[0-9]+?/(.+?)/', 
			link_to_table).group(1)
		return accession_number
		
	def get_tables_for_one_filing(self, cik, link_to_filing):
		"""gives a python dictionary corresponding to the data tables of 
		a specific filing's link"""
		
		def generate_url(counter, cik, accession_number):
			# helper function
			# generates random urls and adds them to dictionary if 
			# they correspond to a financial statement table for filing which
			# is fond via accession_number
			url = (f'https://www.sec.gov/Archives/edgar/data/{cik}/' +
				f'{accession_number}/R{counter}.htm')
			page = requests.get(url)
			if ('Consolidated Statements of Operations' in page.text):
				if not('income' in link_dict):
					link_dict['income'] = url
			elif ('Consolidated Balance Sheets' in page.text):
				if not('balance' in link_dict):
					link_dict['balance'] = url
			elif ('Consolidated Statements of Cash' in page.text):
				if not('cfs' in link_dict):
					link_dict['cfs'] = url

		accession_number = DataScraper.extract_accession_number_from_filings_link(self,
			link_to_filing)
		link_dict = {}
		counter = 1

		while True:
			generate_url(counter, cik, accession_number)
			# Once all 3 statements are found the loop is exited
			if ('income' in link_dict) and ('balance' in link_dict) and (
				'cfs' in link_dict):
				return link_dict

			# exit conditions if code does not perform as expected
			if counter > 50:
				raise Exception("get_tables_for_one_filing error:" + 
					"Couldn't locate full financial statements")
			counter = counter + 1 
		return link_dict

	def get_fiscal_year_and_quarter(self, cik, link_to_filing, from_table_link=False):
		# used internally with from_table_link = False
		if from_table_link == False:
			accession_number = DataScraper.extract_accession_number_from_filings_link(self,
				link_to_filing)
		# if_link_to_filing corresponds to a table url (used by Filings class):
		else:
			accession_number = DataScraper.extract_accession_number_from_table_link(self,
				link_to_filing)
		url = (f'https://www.sec.gov/Archives/edgar/data/{cik}/' +
				f'{accession_number}/R1.htm')
		tree = DataScraper.create_tree(self, url)
		fy_q_dict = {}
		for x in [cell.text_content().strip() for cell in tree.xpath('//td[@class="text"]')]:
			if ',' in x:
				fy_q_dict['year'] = re.search(', +(....)', x).group(1)
			elif 'Q1' in x:
				fy_q_dict['period_ended'] = 'Q1'
			elif 'Q2' in x:
				fy_q_dict['period_ended'] = 'Q2'
			elif 'Q3' in x:
				fy_q_dict['period_ended'] = 'Q3'
			elif 'FY' in x:
				fy_q_dict['period_ended'] = 'FY'
		return fy_q_dict

class Filings():
	"""
	A data structure that holds all the information relevant to a given
	company's financials in the form of a dictionary
	"""
	def __init__(self, cik):
		self.cik = cik
		# statements corresponding to each FS type
		self.statement_keys = ['balance', 'income', 'cfs'] 
		self.collect_raw_data()

	def collect_raw_data(self):
		self.raw_data = {}
		all_filings_links = [DataScraper.get_tables_for_one_filing(self, self.cik, x) for x in DataScraper.find_filings(self, self.cik)]
		for filing_link in all_filings_links:
			# temporary data store before data is copied to self.raw_data
			temp_dict = {} 
			# iterating over each financial statement in a given filing
			for x in filing_link:
				temp_dict[x] = DataScraper.get_data_from_table_link(self, 
					self.cik, filing_link[x])
				#print("executed correctly")
			time_period = DataScraper.get_fiscal_year_and_quarter(self, self.cik, filing_link['income'], from_table_link=True)
			self.raw_data[time_period['year'] + time_period['period_ended']] = temp_dict

	def organize_data(self, data):
		organized_data = {}
		self.set_latest_period(data)

	def select_data_creation_function(self,data,statement_type):
		"""
		uses correct function to compile financial data across time periods
		"""
		data = {}
		if statement_type == 'balance':
			self.compile_balance_sheets(data)
		elif statement_type == 'income':
			self.compile_income_statement(data)
		elif statement_type == 'cfs':
			self.compile_cfs(data)

	def compile_income_statement(self, data):
		self.income = {}
	
	def compile_balance_sheets(self):
		self.income = {}

	def compile_cfs(self):
		self.income = {}

	def set_latest_period(self, data):
		"""
		Helper function to remove logic from organize_data & improve readability.
		Sets the company's latest filing date to self.latest_period
		"""
		self.latest_period = ''
		for period in data:
			if (self.latest_period == ''):
				self.latest_period = period
				break

	def get_row_labels(self, data, statement_type):
		"""
		Determines what the labels for each row will be. Must be executed after
		set_latest_period
		"""
		return [filing[0] for filing in self.raw_data[self.latest_period][statement_type]]

	def clean_data(self):
		"""
		Removes common unecessary line items that were scrapped
		as an unintentional byproduct
		"""
		pass