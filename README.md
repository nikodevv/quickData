# quickData
## Installation
### Prerequisites
```
Python 3.6 +
lxml
requests
fuzzy_wuzzy
```
Note earlier versions of python can be used if all f-strings are refactored to normal string concatenations. i.e. change `some_function(f'example {string}')` to `some_function('example ' + string)`
### Install Requirements
1. Download source files either manually or via `git clone https://github.com/nikodevv/quickData`
2. Install requirements using pip
```
	pip install lxml
	pip install requests
	pip install fuzzywuzzy
```

## API
Simply create an instance of `Filings` with a given company's CIK, and a Python object containing all of the company's financial statements will be generated. For example Snapchat's CIK is 1564408 (Snap Inc.), so a Filings object would be created as follows:
```
snapFilings = Filings(1564408)
```
### Example (generating time series data of a financial statement)
To access the data in any SEC-filing table ([example: Snap Inc's 2017 Income Statement](https://www.sec.gov/Archives/edgar/data/1564408/000156459017022434/R4.htm)), just call 
```
custom_table = [] 
# custom_table[0] will be the row labels of income statement
custom_table.append(snapFiligns.row_labels['income'])
# custom_table[1] will be the values
custom_table.append(snapFilings.full_dict['2017Q3'][income])

print(custom_table[0][1] + ':' + custom_table[1][1])
# Revenue: 207937

print(custom_table[0][9] + ':' + custom_table[1][9])
# Loss from operations: -461827
```

### Explanation of example
The company's time-series filings are stored in two objects.
The first is a dictionary of lists containing the row labels (`snapFilings.row_labels`) of all 3 financial statements. These labels are similiar to those found in the original SEC filings. Each financial statement can be accessed by one of three keys: `income` returns income statement line items, `balance` returns balance sheet line items, and `cfs` returns cashflow statement line items (line items refers to accounts). For example, the row labels of Snapchat's quickData income statement can be accessed as follows:
```
snapFilings.row_labels['income']
> ['Income Statement [Abstract]', 'Revenue', 'Costs and expenses', 'Cost of revenue', 'Research and development', 'Sales and marketing', 'General and administrative', ...]
```
The `row_labels` are in 1:1 correspondace with the data columns corresponding to each time period. These data columns are called by `snapFilings.full_dict`. Together, `row_labels` and `full_dict` can create time-series financial statements.

Here is an example of what Snap Inc.'s `full_dict` looks like:
```
# snapFilings.full_dict = 
	{'2017Q1': {
		'balance': [...]
		'income' : [...]
		'cfs': [...]
		}
	'2017Q2': {
		'balance': [...]
		'income' : [...]
		'cfs': [...]
		}
	'2017Q1' : ...
	}
```

Where `2017Q1` refers to the first financial quarter of Snap Inc's 2017 financial year. Annual filings keys are of the following form: '2017FY'.


### Full 

## Disclaimer
The author assumes no responsibility or liability for any errors, inaccuracies, or omissions in the data generated or output by quickData, nor any responsibility or liability for investment or business descicions made on said data. The information provided by quickData is provided on an “as is” basis with no guarantees of completeness, accuracy, usefulness or timeliness.