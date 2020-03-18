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

@click.command()
@click.argument("regions", nargs=-1, required=True)
@click.option("--log", is_flag=True)
def plot_data(regions: List[str], log: bool):
    import matplotlib.pyplot as plt
    import pandas as pd

    # TODO: Make sure that XLS file is actually downloaded
    df = pd.read_excel(
        _get_xls_url(), index_col="DateRep", parse_dates=True
    ).sort_index()

    for region in regions:
        df_r = df[df["Countries and territories"].str.lower() == region.lower()]
        df_r = df_r["Cases"].cumsum()
        # Remove rows before first case
        df_r = df_r.truncate(before=df_r.ge(1).idxmax())
        df_r.plot(logy=log, label=region)

    plt.ylabel("Number of confirmed cases")
    if log:
        plt.yscale("log")

    end_date = max(df.index).date()
    plt.title("Confirmed cases per country as of " + str(end_date))
    plt.legend()
    plt.show()

    # Saving figure
    plt.savefig('output.png')


if __name__ == "__main__":
    plot_data()
