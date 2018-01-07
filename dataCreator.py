from lxml.html import fromstring
import requests

class DataScraper():
	"""Scraps income statement of a given company, aligning historical data"""
	def __init__(self,company_IS_data_link):
		self.main(company_IS_data_link)

	def main(self,company_IS_data_link):
		self.page = requests.get(company_IS_data_link)
		self.tree = fromstring(self.page.content)

		self.line_items = self.tree.xpath('//td[@class="pl "]/a//text()')
		self.line_items.pop(0) # unnecessary item which ruins mapping
		self.values = self.tree.xpath('//td[@class="nump"]/text()')
		
