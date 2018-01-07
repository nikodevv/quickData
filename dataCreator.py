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
		self.values = self.tree.xpath('//td[@class="nump"]/text()')

		self.format_values()
		self.mappedData = self.mapData()

	def mapData(self):
		pass
	def format_values(self):
		"""makes sure the values elements of raw data are all valid integers 
		except per share amounts, which are valid"""
		self.values = [x.strip('$ ') for x in self.values  if x != '\n']
		self.values = [int(x.replace(',', '')) for x in self.values[:2]]
