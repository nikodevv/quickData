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
1. Download Source files either manually or via `git clone https://github.com/nikodevv/quickData`
2. Install requirements using pip
```
	pip install lxml
	pip install requests
	pip install fuzzywuzzy
```

## API
Simply create an instance of `Filings` with the company's CIK, and a Python object containing all of the company's financial statements will be generated. For example
```

```
### Filings
