class TestFilings(TestCase):

	def setUp(self):
		self.testFilings = Filings('1564408') # Snapchat cik

	def test_returns_dict(self):
		self.assertIsInstance(self.testFilings.raw_data, dict)
		print(self.testFilings.raw_data['2017Q1']['income'])

	def test_set_latest_period(self):
		self.testFilings.set_latest_period({'period1' :{'some':'object', 
			'period2' : {'another': 'object'}}})
		self.assertEqual(self.testFilings.latest_period, 'period1')

	def test_returns_row_labels(self):
		self.testFilings.set_latest_period(self.testFilings.raw_data)
		self.assertIsInstance(
			self.testFilings.get_row_labels(self.testFilings.raw_data,
				self.testFilings.statement_keys[0]),
			list)
		self.assertIsInstance(
			self.testFilings.get_row_labels(self.testFilings.raw_data,
				self.testFilings.statement_keys[1])[0],
			str)

	@skip
	def test_picks_correct_compilation_function(self):
		self.fail("incomplete test")
		# tests select_data_creation_function()
