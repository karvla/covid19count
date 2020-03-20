# covid19count
Plots number of confirmed COVID-19 cases for countries worldwide. The data is pulled from 	
[European Centre for Disease Prevention and Control](https://www.ecdc.europa.eu/en/geographical-distribution-2019-ncov-cases).

![example](https://github.com/karvla/covid19count/raw/master/example.png)

## Usage

Install dependencies with `poetry install` (if you have poetry installed) or `pip install --user .`

Run with `python3 covid19count.py country1 country2 ...`. 

To plot with a logarithmic y-axis, add the argument `--log`.

## Docker container

Build the image using the context of the root directory:

`docker build -t covid19-confirmed-cases:1.0 -f docker/Dockerfile .`

Run the application, make it available on port 8080 (the container exposes port 8080, the syntax is '-p hostPort:containerPort'):

`docker run --rm -d -p 8080:8080 covid19-confirmed-cases:1.0`

Open a browser and checkout localhost at 8080.

![example](https://github.com/karvla/covid19count/raw/master/containerExample.png)
