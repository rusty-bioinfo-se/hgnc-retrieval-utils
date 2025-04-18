"""Retrieve gene info for PMID."""

import os
import sys
import click
import pathlib
import json
import logging
import calendar
import time
import yaml
import requests
import pandas as pd
from time import sleep
import csv

from uuid import uuid4
from datetime import datetime
from rich.console import Console
from typing import Dict

import constants
from file_utils import check_infile_status

DEFAULT_OUTDIR = os.path.join(
    constants.DEFAULT_OUTDIR_BASE,
    os.path.splitext(os.path.basename(__file__))[0],
    constants.DEFAULT_TIMESTAMP,
)

error_console = Console(stderr=True, style="bold red")
console = Console()


def fetch_hgnc_data(gene_symbol: str) -> Dict[str, str]:
    """Fetch HGNC ID, name, and aliases from HGNC API.

    Args:
        gene_symbol (str): The gene symbol.

    Returns:
        dict: A dictionary containing HGNC ID, gene name, and aliases.
    """
    try:
        response = requests.get(
            f"{constants.HGNC_API}{gene_symbol}", headers={"Accept": "application/json"}
        )
        response.raise_for_status()
        data = response.json()
        if data["response"]["numFound"] == 0:
            logging.warning(f"No HGNC data found for {gene_symbol}")
            return None
        doc = data["response"]["docs"][0]
        return {
            "hgnc_id": doc.get("hgnc_id", ""),
            "gene_name": doc.get("name", ""),
            "aliases": ",".join(doc.get("alias_symbol", [])),
        }
    except requests.RequestException as e:
        logging.error(f"Error fetching HGNC data for {gene_symbol}: {e}")
        return None


def fetch_ensembl_coordinates(gene_symbol: str) -> tuple:
    """Fetch Hg38 and Hg19 genomic coordinates from Ensembl API.

    Args:
        gene_symbol (str): The gene symbol.

    Returns:
        tuple: Hg38 and Hg19 coordinates.
    """
    try:
        response = requests.get(
            f"{constants.ENSEMBL_API}{gene_symbol}?expand=1",
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        data = response.json()

        hg38_coords = f"{data['seq_region_name']}:{data['start']}-{data['end']}"

        xref_response = requests.get(
            f"{constants.ENSEMBL_XREF_API}{gene_symbol}?external_db=HGNC",
            headers={"Content-Type": "application/json"},
        )
        xref_response.raise_for_status()
        xref_data = xref_response.json()
        ensembl_id = xref_data[0]["id"] if xref_data else None

        if ensembl_id:
            hg19_coords = hg38_coords  # Placeholder; replace with actual Hg19 mapping
        else:
            hg19_coords = "N/A"

        return hg38_coords, hg19_coords
    except requests.RequestException as e:
        logging.error(f"Error fetching Ensembl data for {gene_symbol}: {e}")
        return "N/A", "N/A"


def fetch_ncbi_gene_id(gene_symbol):
    """Fetch NCBI Gene ID from Ensembl API for use with Monarch API.

    Args:
        gene_symbol (str): The gene symbol.
        logger (logging.Logger): Logger instance.

    Returns:
        str: NCBI Gene ID or None if not found.
    """
    try:
        response = requests.get(
            f"{constants.ENSEMBL_XREF_API}{gene_symbol}?external_db=EntrezGene",
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        xref_data = response.json()
        for item in xref_data:
            if item.get("dbname") == "EntrezGene":
                return item["primary_id"]
        logging.warning(f"No NCBI Gene ID found for {gene_symbol}")
        return None
    except requests.RequestException as e:
        logging.error(f"Error fetching NCBI Gene ID for {gene_symbol}: {e}")
        return None


def fetch_disease_association(gene_symbol: str) -> str:
    """Fetch disease associations from Monarch Initiative API using NCBI Gene ID.

    Args:
        gene_symbol (str): The gene symbol.
        logger (logging.Logger): Logger instance.

    Returns:
        str: Disease associations (semicolon-separated).
    """
    try:
        ncbi_id = fetch_ncbi_gene_id(gene_symbol)
        if not ncbi_id:
            return "N/A"
        # Use Monarch's association endpoint
        response = requests.get(
            f"https://api.monarchinitiative.org/api/association/gene/NCBIGene:{ncbi_id}/disease",
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()
        data = response.json()
        diseases = [assoc["object"]["label"] for assoc in data.get("associations", [])]
        return ";".join(diseases[:2]) if diseases else "N/A"
    except requests.RequestException as e:
        logging.error(f"Error fetching disease data for {gene_symbol}: {e}")
        return "N/A"


def run(
    pmid: str, outfile: str, config: dict, verbose: bool = constants.DEFAULT_VERBOSE
) -> None:
    """Main processing function to retrieve gene data.

    Args:
        pmid (str): The PubMed ID.
        outfile (str): Output file path.
        config (dict): Configuration dictionary.
    """
    logging.info("Initializing data storage")
    results = []

    # TODO: Add integration for retrieving/parsing gene symbols from PMID resources - currently not working.
    for gene in constants.TEST_GENES:
        logging.info(f"Processing {gene}...")

        hgnc_data = fetch_hgnc_data(gene)
        if not hgnc_data:
            logging.warning(f"Skipping {gene} due to missing HGNC data")
            continue

        hg38_coords, hg19_coords = fetch_ensembl_coordinates(gene)

        disease = fetch_disease_association(gene)

        result = {
            "HGNC_ID": hgnc_data["hgnc_id"],
            "HGNC_Gene_Name": hgnc_data["gene_name"],
            "Gene_Aliases": hgnc_data["aliases"],
            "Hg38_Coordinates": hg38_coords,
            "Hg19_Coordinates": hg19_coords,
            "Disease": disease,
        }

        results.append(result)

        sleep(1)

    if results:
        df = pd.DataFrame(results)
        df.to_csv(outfile, index=False, quoting=csv.QUOTE_MINIMAL)
        logging.info(f"Data saved to {outfile}")
        if verbose:
            print(f"Data saved to {outfile}")
    else:
        logging.warning("No data to save.")


def validate_verbose(ctx, param, value):
    """Validate the verbose option."""
    if value is None:
        click.secho(
            "--verbose was not specified and therefore was set to 'True'", fg="yellow"
        )
        return constants.DEFAULT_VERBOSE
    return value


@click.command()
@click.option(
    "--config_file",
    type=click.Path(exists=True),
    help=f"The configuration file for this project - default is '{constants.DEFAULT_CONFIG_FILE}'",
)
@click.option("--infile", help="The primary input file")
@click.option("--logfile", help="The log file")
@click.option(
    "--outdir",
    help=f"The default is the current working directory - default is '{DEFAULT_OUTDIR}'",
)
@click.option("--outfile", help="The output final report file")
@click.option("--pmid", help="The PMID for which gene metadata should be retrieved.")
@click.option(
    "--verbose",
    is_flag=True,
    callback=validate_verbose,
    help=f"Will print more info to STDOUT - default is '{constants.DEFAULT_VERBOSE}'.",
)
def main(
    config_file: str,
    infile: str,
    logfile: str,
    outdir: str,
    outfile: str,
    pmid: str,
    verbose: bool,
):
    """Retrieve gene info for PMID."""
    error_ctr = 0

    if pmid is None:
        console.print(f"[bold red]--pmid was not specified[/]")
        error_ctr += 1

    if error_ctr > 0:
        error_console.print("[bold red]Exiting because of errors[/]")
        click.echo(click.get_current_context().get_help())
        sys.exit(1)

    if config_file is None:
        config_file = constants.DEFAULT_CONFIG_FILE
        console.print(
            f"[yellow]--config_file was not specified and therefore was set to '{config_file}'[/]"
        )

    if outdir is None:
        outdir = DEFAULT_OUTDIR
        console.print(
            f"[yellow]--outdir was not specified and therefore was set to '{outdir}'[/]"
        )

    if not os.path.exists(outdir):
        pathlib.Path(outdir).mkdir(parents=True, exist_ok=True)
        console.print(f"[yellow]Created output directory '{outdir}'[/]")

    if logfile is None:
        logfile = os.path.join(
            outdir, os.path.splitext(os.path.basename(__file__))[0] + ".log"
        )
        console.print(
            f"[yellow]--logfile was not specified and therefore was set to '{logfile}'[/]"
        )

    if outfile is None:
        outfile = os.path.join(outdir, f"{pmid}_gene_metadata.csv")
        console.print(
            f"[yellow]--outfile was not specified and therefore was set to '{outfile}'[/]"
        )

    logging.basicConfig(
        filename=logfile,
        format=constants.DEFAULT_LOGGING_FORMAT,
        level=constants.DEFAULT_LOGGING_LEVEL,
    )

    check_infile_status(config_file, "yaml")

    logging.info("Will load contents of config file 'config_file'")
    config = yaml.safe_load(pathlib.Path(config_file).read_text())

    run(pmid, outfile, config, verbose)

    if verbose:
        logging.info(f"The log file is '{logfile}'")
        console.print(
            f"[bold green]Execution of '{os.path.abspath(__file__)}' completed[/]"
        )


if __name__ == "__main__":
    main()
