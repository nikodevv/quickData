from lxml.html import fromstring
import requests

class DataScraper():
	"""Scraps income statement of a given company, aligning historical data"""
	def __init__(self,company_IS_data_link):
		self.main(company_IS_data_link)

	def main(self,company_IS_data_link):
		self.page = requests.get(company_IS_data_link)
		self.tree = fromstring(self.page.content)
		self.line_items = self.tree.xpath('//td[@class="pl "]/a/text()')
		self.values = self.tree.xpath('//td[@class="nump" or @class="num"]/text()')
		self.format_values()		
		self.mappedData = self.mapData()


	def format_values(self):
		"""makes sure the values elements of raw data are all valid integers 
		except per share amounts, which are valid"""
		def correctSign(x):
			if x[0] == "(":
				return '-'+x.strip('(').strip(')')
			else:
				return x

		self.values = [x.strip('$ ') for x in self.values if x != '\n']
		self.values = [x.replace(',' , '') for x in self.values]
		self.values = [float(correctSign(x)) for x in self.values]

	def mapData(self):
		"""used in initialization -- combines names & values into a single
		dictionary"""
		tempValues = []
		for i in range(0, len(self.values), 4):
			tempValues.append([self.values[i+1],self.values[i]])

		return dict(zip(self.line_items, tempValues))

	def find_filings(self, cik, type_="10-"):
		"""
		returns links to all financial filings which are available for
		scrapping for a given cik. The type of filigns can be filtered for via
		type_. i.e. type_ = '10-K', will only return 10-Ks 	
		"""
		page = requests.get('https://www.sec.gov/cgi-bin/browse-edgar?' + 
			f'action=getcompany&CIK={cik}&type={type_}&dateb=&owner='
			+ 'include&count=100')
		tree = fromstring(page.content)
		filing_links = tree.xpath('//a[@id="interactiveDataBtn"]/@href')
		filing_links = [f'https://www.sec.gov{x}' for x in filing_links]
		return filing_links

	def categorize_filing(self, link_to_filing):
		"""takes a filing and returns its type"""
		page = requests.get(link_to_filing)
		tree = fromstring(page.content)
		if '10-Q' in tree.xpath('//strong/text()'):
			return '10-Q'
		# Could be bad if a somehow a filing with less than 4 characters 
		# gets through. Shouldn't occur due to the way find_find_filings
		# looks for filings.
		if '10-K' in [x[:4] for x in tree.xpath('//strong/text()')]:
			return '10-K'
		return "unknown filing type"

class DataProcessor():
	pass