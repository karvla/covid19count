#!/usr/bin/env python3

import regex as re
from datetime import datetime
from typing import List, Callable
from pathlib import Path

import pandas as pd
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


def _download_file_cached(
    get_url: Callable[[], str], path: Path, cache_expire: int = 300
):
    if (
        not path.exists()
        or path.lstat().st_mtime < datetime.now().timestamp() - cache_expire
    ):
        print("Downloading file...")
        _download_file(get_url(), path)
    else:
        print("Used cache")
    return path


def _download_file(url: str, path: Path) -> Path:
    r = requests.get(url)
    path.open("wb").write(r.content)
    return path


@click.group()
def main():
    """Tools to analyze cases and deaths from COVID-19"""
    pass


def _load_df() -> pd.DataFrame:
    path = Path("data.xls")
    _download_file_cached(_get_xls_url, path)
    return pd.read_excel(path, index_col="DateRep", parse_dates=True).sort_index()


@main.command()
@click.argument("regions", nargs=-1, required=True)
@click.option("--cum", is_flag=True, help="Plot cumulative cases/deaths")
@click.option("--deaths", is_flag=True, help="Plot deaths")
@click.option("--log", is_flag=True, help="Use a log scale on the y-axis")
@click.option("--bar", is_flag=True, help="Use a bar plot instead")
def plot(regions: List[str], cum: bool, deaths: bool, log: bool, bar: bool):
    """Plot cases (by default) or deaths for different regions"""

    cases_or_deaths = "Cases" if not deaths else "Deaths"
    regions = [r.lower() for r in regions]

    df = _load_df()

    for region in regions:
        if region not in set(df["Countries and territories"].str.lower()):
            print(f"Error: Region '{region}' does not exist in the dataset")
            regions.remove(region)

    df = df[df["Countries and territories"].str.lower().isin(regions)]
    df = df.pivot(columns="Countries and territories", values=cases_or_deaths)

    # Remove rows before first case
    df = df.truncate(before=df.sum(axis=1).ge(1).idxmax())
    df = df.loc[: pd.Timestamp("2020-03-2")]
    if cum:
        df = df.cumsum()

    plotf = df.plot if not bar else df.plot.bar
    plotf(logy=log)

    plt.ylabel(f"Number of new {cases_or_deaths}")
    plt.title(f"New {cases_or_deaths} as of {max(df.index).date()}")
    plt.ylim(0)
    plt.legend()
    plt.show()

    # Saving figure
    plt.savefig('output.png')


if __name__ == "__main__":
    main()
