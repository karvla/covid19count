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
    get_url: Callable[[], str], path: Path, cache_expire: int = 3600
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
    r.raise_for_status()
    path.open("wb").write(r.content)
    return path


@click.group()
def main():
    """Tools to analyze cases andddeaths from COVID-19"""
    pass


def _load_df() -> pd.DataFrame:
    path = Path("data.xls")
    _download_file_cached(_get_xls_url, path)
    return pd.read_excel(path, index_col="dateRep", parse_dates=True).sort_index()


def _load_population():
    # TODO: Get more recent population data
    path = Path("population.csv")
    _download_file_cached(
        lambda: "https://datahub.io/core/population/r/population.csv", path,
    )
    df = pd.read_csv(path, parse_dates=True)
    df = df.set_index(pd.DatetimeIndex([str(x) for x in df["Year"]]))
    df = df.pivot(columns="Country Name", values="Value")
    df.columns = [x.lower() for x in df.columns]
    return df.iloc[-1]


@main.command()
@click.argument("regions", nargs=-1, required=True)
@click.option("--cum", is_flag=True, help="Plot cumulative cases/deaths")
@click.option("--deaths", is_flag=True, help="Plot deaths")
@click.option("--log", is_flag=True, help="Use a log scale on the y-axis")
@click.option("--bar", is_flag=True, help="Use a bar plot instead")
@click.option("--per-capita", is_flag=True)
@click.option("--from-first-death", is_flag=True)
@click.option("--since")
@click.option("--until")
@click.option("--outfile")
def plot(
    regions: List[str],
    cum: bool,
    deaths: bool,
    log: bool,
    bar: bool,
    per_capita: bool,
    from_first_death: bool,
    since=None,
    until=None,
    outfile=None,
):
    """Plot cases (by default) or deaths for different regions"""

    cases_or_deaths = "cases" if not deaths else "deaths"
    regions = _filter_regions([r.lower() for r in regions])

    df = _load_df()
    most_recent = max(df.index).date()

    df = df[df["countriesAndTerritories"].str.lower().isin(regions)]
    df = df.pivot(columns="countriesAndTerritories", values=cases_or_deaths)
    df.columns = [c.replace("_", " ") for c in df.columns]

    # Remove rows before first case
    df = df.truncate(before=df.sum(axis=1).ge(1).idxmax())

    if cum:
        df = df.cumsum()

    if since:
        df = df.loc[pd.Timestamp(since) :]
    if until:
        df = df.loc[: pd.Timestamp(until)]

    if per_capita:
        pop = _load_population()
        for region in df.columns:
            popreg = region.lower().replace("_", " ")
            if popreg == "united states of america":
                popreg = "united states"
            df[region] = df[region] / pop.loc[popreg]

    if from_first_death:
        dfs = []
        for region in df.columns:
            df_c = df[region]
            df_c = df_c.truncate(before=df_c.gt(0).idxmax())
            df_c.index = list(range(0, len(df_c)))
            dfs.append(df_c)
        df = pd.concat(dfs, axis=1)

    plotf = df.plot if not bar else df.plot.bar
    plotf(logy=log)

    new_or_cum = "Cumulative" if cum else "New"
    plt.xlabel("Days from first death" if from_first_death else "")
    plt.ylabel(
        f"{new_or_cum} {cases_or_deaths.lower()} {'per capita' if per_capita else ''}"
    )
    plt.tick_params(axis="y", which="both", labelleft="off", labelright="on")
    plt.title(
        f"COVID-19 {new_or_cum} {cases_or_deaths.lower()} {'per capita' if per_capita else ''} as of {most_recent}"
    )
    plt.ylim(0 if per_capita else 1)

    plt.legend()
    _draw_watermark(plt.gcf())

    if outfile:
        # Saving figure
        plt.savefig(outfile)
    else:
        # Showing figure
        plt.show()


def _filter_regions(regions: List[str]) -> List[str]:
    df = _load_df()
    all_regions = set(df["countriesAndTerritories"].str.lower())
    # print(sorted(all_regions))
    for region in regions:
        if region not in all_regions:
            print(f"Error: Region '{region}' does not exist in the dataset")
            regions.remove(region)
    return regions


@main.command()
@click.option("--stdout", is_flag=True)
@click.option("--outfile")
def listregions(stdout: bool, outfile=None):
    """Get a list of the available regions"""
    import pandas as pd

    # TODO: Make sure that XLS file is actually downloaded
    df = pd.read_excel(
        _get_xls_url(), index_col="dateRep", parse_dates=True
    ).sort_index()

    regions = []
    for region in df["countriesAndTerritories"]:
        regions.append(region)

    # Remove duplicates
    regions = sorted(set(df["countriesAndTerritories"]))

    if not outfile:
        outfile = "regions.txt"

    data = "\r\n".join(regions)
    if stdout:
        print(data)
    else:
        with open(outfile, "w") as f:
            f.write(data)


@main.command()
@click.argument("regions", nargs=-1, required=True)
@click.option("--outfile")
def fatality(regions: List[str], outfile=None):
    # TODO: Add time-lag to account for testing
    regions = _filter_regions(regions)

    df = _load_df()
    df = df[df["countriesAndTerritories"].str.lower().isin(regions)]
    df_c = df.pivot(columns="countriesAndTerritories", values="cases")
    df_d = df.pivot(columns="countriesAndTerritories", values="deaths")
    df = df_d.cumsum() / df_c.cumsum()

    # Remove rows before first case
    df = df.truncate(before=df.sum(axis=1).ge(0).idxmax())

    (df * 100).plot()

    plt.title("COVID-19 fatality rate (total deaths / total cases)")
    plt.text(
        0.5,
        0.98,
        "Note: heavily influenced by testing capacity of each country",
        horizontalalignment="center",
        verticalalignment="center",
        transform=plt.gca().transAxes,
        color="gray",
    )
    plt.ylabel(f"Rate (%)")
    plt.xlabel("")
    plt.ylim(0)
    _draw_watermark(plt.gcf())

    if outfile:
        # Saving figure
        plt.savefig(outfile)
    else:
        # Showing figure
        plt.show()


def _draw_watermark(fig):
    fig.text(0.01, 0.01, "Data from www.ecdc.europa.eu", ha="left", va="bottom")
    fig.text(0.99, 0.05, "Built by @ErikBjare, @karvla, et al", ha="right", va="bottom")
    fig.text(
        0.99, 0.03, "Generated by covid19count", ha="right", va="bottom",
    )
    fig.text(
        0.99,
        0.01,
        "https://github.com/karvla/covid19count",
        color="gray",
        ha="right",
        va="bottom",
    )


if __name__ == "__main__":
    main()
