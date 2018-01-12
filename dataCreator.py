from lxml.html import fromstring
import requests
import re

class DataScraper():
	"""Scraps income statement of a given company, aligning historical data"""
	def __init__(self,company_IS_data_link):
		self.main(company_IS_data_link)

	def main(self,company_IS_data_link):
		self.tree = self.create_tree(company_IS_data_link)
		self.line_items = self.tree.xpath('//td[@class="pl "]/a/text()')
		self.values = self.tree.xpath('//td[@class="nump" or @class="num"]/text()')
		self.values = self.format_values(self.values)		
		self.mappedData = self.mapData()

	def format_values(self, values):
		"""makes sure the values elements of raw data are all valid integers 
		except per share amounts, which are valid"""
		def correctSign(x):
			if x[0] == "(":
				return '-'+x.strip('(').strip(')')
			else:
				return x

		values = [x.strip('$ ') for x in values if x != '\n']
		values = [x.replace(',' , '') for x in values]
		return [float(correctSign(x)) for x in values]

	def mapData(self):
		"""used in initialization -- combines names & values into a single
		dictionary"""
		tempValues = []
		for i in range(0, len(self.values), 4):
			tempValues.append([self.values[i+1],self.values[i]])

		return dict(zip(self.line_items, tempValues))

	def find_filings(self, cik, filing_type="10-"):
		"""
		returns links to all financial filings which are available for
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
		try:
			accession_number = re.search('accession_number=(.+?)&', 
				link_to_filing).group(1)
		except:
			raise Exception("extract_links_to_tables_from_link_failing error:"
				+"Couldn't find apporopriate accession number from link")

		if unformatted == True:
			return accession_number
		return re.sub('[-]', '', accession_number)

	def get_tables_for_one_filing(self, cik, link_to_filing):

		def generate_url(counter, cik, accession_number):
			# helper function
			# generates random urls and adds them to dictionary if 
			# they correspond to a financial statement table for filing which
			# is fond via accession_number
			url = (f'https://www.sec.gov/Archives/edgar/data/{cik}/' +
				f'{accession_number}/R{counter}.htm')
			page = requests.get(url)
			if ('Consolidated Statements of Operations' in page.text):
				if not('revenue' in link_dict):
					link_dict['revenue'] = url
			elif ('Consolidated Balance Sheets' in page.text):
				if not('balance' in link_dict):
					link_dict['balance'] = url
			elif ('Consolidated Statements of Cash' in page.text):
				if not('cfs' in link_dict):
					link_dict['cfs'] = url

		accession_number = self.extract_accession_number_from_filings_link(
			link_to_filing)
		link_dict = {}
		counter = 1

		while True:
			generate_url(counter, cik, accession_number)
			# Once all 3 statements are found the loop is exited
			if ('revenue' in link_dict) and ('balance' in link_dict) and (
				'cfs' in link_dict):
				return link_dict

			# exit conditions if code does not perform as expected
			if counter > 50:
				raise Exception("get_tables_for_one_filing error:" + 
					"Couldn't locate full financial statements")
			counter = counter + 1 
		return link_dict

	def get_all_tables_from_find_filings(self, cik, filing_type='10-', 
		table_type='all'):
		"""
		Returns list of links to filing data tables.
		Currently table_type parameter cannot take any features except "all" 
		(feature is awaiting implementation)
		"""
		table_links = {}
		list_of_filings = find_filings(self, cik, filing_type=filing_type)
		for x in list_of_filings:
			extract_links_to_tables_from_link_to_filing(cik, x)
		
	def create_tree(self, link):
		"""returns tree that can be searched via xpath"""
		return fromstring(requests.get(link).content)

class DataProcessor():
	pass