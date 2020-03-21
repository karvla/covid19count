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
from covid19count import _get_xls_url

def save_regions():
    import pandas as pd

    df = pd.read_excel(
        _get_xls_url(), index_col="DateRep", parse_dates=True
    ).sort_index()

    regions = df["Countries and territories"].drop_duplicates()
    regions.sort_values()

    with open("regions.txt","w") as f:
        f.write(", ".join(regions))

if __name__ == "__main__":
    save_regions()
