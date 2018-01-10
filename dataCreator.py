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
		tempValues = []
		for i in range(0, len(self.values), 4):
			tempValues.append([self.values[i+1],self.values[i]])

		return dict(zip(self.line_items, tempValues))

	def find_filings(self, cik):
		page = requests.get(f'https://www.sec.gov/cgi-bin/browse-edgar?' + 
			f'action=getcompany&CIK={cik}&type=10-&dateb=&owner='
			+ 'include&count=40')
		tree = fromstring(page.content)
		filing_links = tree.xpath('//a[@id="interactiveDataBtn"]/@href')
		filing_links = [f'https://www.sec.gov{x}' for x in filing_links]
		return filing_links

class DataProcessor():
	pass