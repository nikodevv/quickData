from lxml.html import fromstring
import requests
import re
from time import sleep
from fuzzywuzzy import fuzz
import time # for testing runtime lengths; remove from distributions.  

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
		line_items = DataScraper.make_line_items_unique(self, 
			# first xpath string is for new filings: pl class has a space after name
			tree.xpath('//td[@class="pl "]/a/text()|//td[@class="pl "]/a/strong/text()|//td[@class="pl custom"]/a/text()' 
				# second xpath string is for older filings: pl class does have space after name
				+ '//td[@class="pl"]/a/text()|//td[@class="pl"]/a/strong/text()|//td[@class="pl custom"]/a/text()'))
		values = tree.xpath('//td[@class="nump" or @class="num" or @class="text"]/text()')
		# if (link_to_table == 'https://www.sec.gov/Archives/edgar/data/1564408/000156459017017303/R2.htm' or
		# 	link_to_table == 'https://www.sec.gov/Archives/edgar/data/1564408/000156459017017303/R6.htm'):
		# 	print(len(line_items)*2 - len(DataScraper.format_values(self, values)))
		return DataScraper.mapData(self, cik, line_items, 
			DataScraper.format_values(self, values), link_to_table)

	def make_line_items_unique(self, line_items):
		unique_line_items = []
		counter = 0
		for item in line_items:
			if item not in unique_line_items:
				unique_line_items.append(item)
			else:
				unique_line_items.append(item + str(counter))
				counter = counter + 1
		return unique_line_items

	def create_tree(self, link):
		"""returns tree that can be searched via xpath"""
		return fromstring(requests.get(link).content)

	def format_values(self, values):
		'''
		makes sure the values elements of raw data are all valid types
		'''
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
		# combines names & values into a single
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
			for i in range(0, len(values)-1, 2):
				tempValues.append([values[i+1], values[i]])
			return dict(zip(line_items, tempValues))

		for i in range(0, len(values)-1, 4):
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

			if (('consolidated statements of operations' in page.text.lower()) or ('consolidated statements of income' in page.text.lower())):
				if not('income' in link_dict):
					link_dict['income'] = url
			elif (('consolidated balance' in page.text.lower())
				or ('f financial condition' in page.text.lower())):
				if not('balance' in link_dict):
					link_dict['balance'] = url
			elif ('consolidated statements of cash' in page.text.lower()):
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
		
		# print([cell.text_content().strip() for cell in tree.xpath('//td[@class="text"]')])
		fy_q_dict = {}
		for x in [cell.text_content().strip() for cell in tree.xpath('//td[@class="text"]')]:
			if ',' in x:
				# The 'except' part of this block might be sufficient for all financials,
				# and the 'try' may not be necessary. Needs further testing.
				try:
					fy_q_dict['year'] = re.search(', +(....)', x).group(1)
				# Older statements have some funky formatting so this fixes that.
				except:
					fy_q_dict['year'] = x[-4:]
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
		self.collect_raw_data()
		self.set_latest_period(self.raw_data)
		statement_keys = ['balance', 'income', 'cfs']
		self.statement_splicers = {
			'balance': ['Total assets', 'Total liabilities', "Total stockholders’ equity"],
			'income': ['operati', 'taxes'],
			'cfs': ['operating activities', 'investing activities', 'financing activities', 'end of']
		}
		self.add_accounts = {
			'balance': ['other assets', 'other liabilities', "other equity"],
			'income': ['other operating income', 'other IS items'],
			'cfs': ['other operating activities', 'other investing activities', 'other financing activities', 'Supplemental disclosures']
		}
		self.statement_splicer_index = {'balance': [],
			'income': [], 'cfs': []}
		self.row_labels = {}

	# Execution time 6-7 sec on my machine for Snapchat.
	def collect_raw_data(self):
		"""
		Takes all data from filings and stores it in a dictionary
		of dictionaries.
		
		For example if a company, only has only been public for 
		Q1 of 2017, the dictionary would have the following 
		format:
		self.raw_data = {
			'2017Q1': filings_dictionary			
		}
		where filings_dictionary = {
			'income' : {
				'Revenue': '2000'
				...all income statement items...
				'Diluted' : '2000' # as in Basic EPS
				}

			'balance' : {
				...all balance sheet items as in 'income'
				key example...
			}
			'cfs' : {
				...all statement of cashflows items as in 
				'income' key example...
			}
		}
		In the example above the values of 2000 are just placeholder for 
		the company's actual reported amounts.
		"""

		self.raw_data = {}
		all_filings_links = [DataScraper.get_tables_for_one_filing(self, 
			self.cik, x) for x in DataScraper.find_filings(self, self.cik)]
		for filing_link in all_filings_links:
			temp_dict = {} 
			for x in filing_link:
				temp_dict[x] = DataScraper.get_data_from_table_link(self, self.cik, filing_link[x])
			time_period = DataScraper.get_fiscal_year_and_quarter(self, 
				self.cik, filing_link['income'], from_table_link=True)
			self.raw_data[time_period['year'] + time_period['period_ended']] = temp_dict

	def get_row_labels(self, statement_type):
		"""
		Determines what the "raw" labels of each table
		(i.e. excludes any additional rows not in the filing)
		"""
		return [key for key in self.raw_data[self.latest_period][statement_type]]

	def set_latest_period(self, data):
		"""
		Sets the company's latest filing date to self.latest_period
		"""
		self.latest_period = ''
		for period in data:
			if (self.latest_period == ''):
				self.latest_period = period
				break

	def prepare_row_labels(self, statement_type):
		"""
		Calls get_row_labels to get a list of financial accounts which will be used
		to combine multiple time periods of filings to create a time seires, 
		and adds in financial accounts which are not present in get_row_labels
		but necessary for creating a time_series of the financials.
		"""
		row_labels = []
		for rowname in self.get_row_labels(statement_type):
			# if nonempty, the statement_splicers (which represent additional
			# financial accounts that are not present in labels list 
			# generated by get_row_labels) are inserted in the appropriate
			# spot of get_row_labels list, nd then saves this new list
			# via set_row_labels_in_self
			if self.statement_splicers[statement_type] != []:
				if fuzz.ratio(self.statement_splicers[statement_type][0], rowname)> 0.95:
					row_labels.append(self.add_accounts[statement_type][0])
					row_labels.append(rowname)
					self.statement_splicer_index[statement_type].append(row_labels.index(self.add_accounts[statement_type].pop(0)))
					self.statement_splicers[statement_type].pop(0)
				else:
					row_labels.append(rowname)
			else:
				row_labels.append(rowname)
		if self.statement_splicers[statement_type] != []:
			raise FinancialStandardError()
		self.row_labels[statement_type] = row_labels

	def save_row_labels(self):
		for statement_type in self.raw_data[self.latest_period]:
			self.prepare_row_labels(statement_type)
	
	def compile_statement(self, data_table, statement_type):
		"""
		creates a list of values that fits in with the predesignated self.row_labels
		"""
		#operati is a partial string for operti[ng income] and [income from] operati[ons]
		data_col = [[0,0]] * len(self.row_labels[statement_type])
		counter = 0
		for key in data_table:
			data_col = self.insert_row(key, data_table, counter, self.row_labels[statement_type], 
				data_col, statement_type)
			counter = counter + 1
		return data_col

	def insert_row(self, key, data_table, counter, labels, data_col, statement_type):
		"""
		takes a key + data_table and inserts
		them into the correct spot of a list corresponding
		the correct format of the final time series
		"""
		# Code Smell
		best_match = [0,'']
		label_counter = 0
		threshold = 0
		for label in labels:
			# the label_counter is to make sure that non-unique names
			# like 'Net loss', which can show up at the start and end of
			# financial statements (see snapchat cfs 2017Q3),
			# end up within some fixed threshold of to the
			# index they appear in the original filing used
			# to generate the row labels.
			# if (label_counter - counter <= 3) and (counter - label_counter <= 3): ### NOT DOING WHAT IT SHOULD BE
			if (fuzz.ratio(key, label)) >= max(0.70, best_match[0]):
				best_match = [fuzz.ratio(key, label), label]
			label_counter = label_counter + 1

		if best_match[0] >= 0.70:
			data_col[labels.index(best_match[1])] = data_table[key]# + data_col[labels.index(best_match[1])]
			return data_col
		else:
			# Right now this code WILL result in bugs for certain
			# financials (i.e. agriculture companies) 
			# because of the 'counter' variable mechanic only
			# "guessing" where to insert the keys. This is based
			# off matching the index of key (counter variable)
			# to the index of statement_splicer in labels.
			# For most companies the output is correct;
			# If any strange scenarios arise please let me know
			# at nick.oshinov@gmail.com with a link to filing
			# This is especially dangerous when dealing with
			# balance sheets, and potentially cashflow statements.
			smallest_gap = [100, 100]
			for x in self.statement_splicer_index[statement_type]:
				if (counter - x) < smallest_gap[0]:
					smallest_gap = [(counter - x), x]
			data_col[smallest_gap[1]] = [[x[0]+x[2], x[1] + x[3]] for x in data_col[key] + data_col[smallest_gap[1]]]
			
			return data_col

	def save_data_cols(self):
		self.save_row_labels()
		# Should refactor; could get an extra one year of financial data if I 
		# take advantage of self.compilestatment(...)[...][1], (i.e. entry[0])
		# which already exists but is not being saved.
		self.full_dict = {period: {statement_type: [entry[1] for entry 
			in self.compile_statement(self.raw_data[period][statement_type],statement_type)]
			for statement_type in self.raw_data[period]} 
			for period in self.raw_data}

	def add_Q4_cols(self):
		temp_dict = {}
		for period in self.full_dict:
			if 'FY' in period and self.filing_exists(f'{period[:3]}Q1')==True:
				temp_dict[f'{period[:3]}Q4'] = self.generate_Q4_cols(self.full_dict[period], 
					self.full_dict[f'{period[:3]}Q1'],
					self.full_dict[f'{period[:3]}Q2'],
					self.full_dict[f'{period[:3]}Q3'])
			temp_dict[period] = full_dict[period]
		self.full_dict = temp_dict

	def generate_Q4_cols(self, fy, q1, q2, q3):
		q4 = {}
		for stmnt in fy:
			q4[stmnt] = []
			for i in range(0, len(fy[stmnt])):
				q4[stmnt].append(fy[stmnt][i] - q1[stmnt][i] - q2[stmnt][i] - q3[stmnt][i])
		return q4

	def filing_exists(self, filing_period):
		"""
		returns true if full_dict has the specified filing
		"""
		try: 
			self.full_dict[filing_period]
			return True
		except:
			return False
	def clean_data(self):
		"""
		Removes common unecessary line items that were scrapped
		as an unintentional byproduct
		"""
		pass

class FinancialStandardError(Exception):
    def __init__(self):
        self.message = ("This company's financial statements deviate too far" + 
				"from common reporting methods. If you notify me of this company's "
				"cik and name on github (@nikodevv), I can work on improving the"
				"parsing algorithms")