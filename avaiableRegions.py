#!/usr/bin/env python3

import regex as re
from datetime import datetime
from typing import List

import numpy as np
import click
import matplotlib.pyplot as plt
import xlrd
import requests
import urllib.request
from bs4 import BeautifulSoup


def _get_xls_url() -> str:
    url = "https://www.ecdc.europa.eu/en/publications-data/download-todays-data-geographic-distribution-covid-19-cases-worldwide"

    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    xls_link_box = soup.find("a", href=re.compile(r".+\.xls"))
    return xls_link_box["href"]

def avalable_regions():
    import matplotlib.pyplot as plt
    import pandas as pd

    # TODO: Make sure that XLS file is actually downloaded
    df = pd.read_excel(
        _get_xls_url(), index_col="DateRep", parse_dates=True
    ).sort_index()

    regions = []
    for region in df["Countries and territories"]:
      regions.append(region)

    # Remove duplicates
    regions = set(regions)
    regions = list(regions)

    regions.sort()

    f = open("regions.txt","w")
    firstRegion = True
    for region in regions:
      f.write( ("," + region) if not firstRegion else region ) 
      firstRegion = False
    f.close()

if __name__ == "__main__":
    avalable_regions()
