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

		self.mappedData = self.mapData()

	def mapData(self):
		return dict(zip(self.line_items,self.values))