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
		basic_values = [self.values[-3],self.values[-4]]
		diluted_values = [self.values[-7], self.values[-8]]
		self.values = [int(correctSign(x)) for x in self.values[:-8]]
		for x in (basic_values + diluted_values):
			self.values.append(float(correctSign(x)))

	def mapData(self):
		tempValues = []
		for i in range(0,len(self.values[:-4]),4):
			tempValues.append([self.values[i+1],self.values[i]])

		# have to do this second loop since format_values strips out the year
		# cumulative financial values for EPS but not for other metrics
		for i in range(len(self.values[:-4]),len(self.values),2):
			tempValues.append([self.values[i],self.values[i+1]])
		return dict(zip(self.line_items, tempValues))

	