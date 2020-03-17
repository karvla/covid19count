# covid19count
Plots number of confirmed COVID-19 cases for countries worldwide. The data is pulled from 	
[European Centre for Disease Prevention and Control](https://www.ecdc.europa.eu/en/geographical-distribution-2019-ncov-cases).

![example](https://github.com/karvla/covid19count/raw/master/example.png)

## Usage

Install dependencies with `poetry install` (if you have poetry installed) or `pip install --user .`

Run with `python3 covid19count.py country1 country2 ...`. 

To plot with a logarithmic y-axis, add the argument `--log`.

