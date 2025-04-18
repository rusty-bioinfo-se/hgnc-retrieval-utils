import logging
import os

from datetime import datetime


DEFAULT_PROJECT = "bg-retrieval-utils"

DEFAULT_TIMESTAMP = str(datetime.today().strftime('%Y-%m-%d-%H%M%S'))

DEFAULT_OUTDIR_BASE = os.path.join(
    '/tmp/', 
    os.getenv('USER'),
    DEFAULT_PROJECT,
)

DEFAULT_OUTDIR = os.path.join(
    '/tmp/', 
    os.getenv('USER'),
    DEFAULT_PROJECT,
    os.path.splitext(os.path.basename(__file__))[0], 
    DEFAULT_TIMESTAMP
)

DEFAULT_CONFIG_FILE = os.path.join(
    "conf", 
    "config.yaml"
)

DEFAULT_LOGGING_FORMAT = "%(levelname)s : %(asctime)s : %(pathname)s : %(lineno)d : %(message)s"

DEFAULT_LOGGING_LEVEL = logging.INFO

DEFAULT_VERBOSE = False

# API endpoints
HGNC_API = "https://rest.genenames.org/fetch/symbol/"
ENSEMBL_API = "http://rest.ensembl.org/lookup/symbol/homo_sapiens/"
ENSEMBL_XREF_API = "http://rest.ensembl.org/xrefs/symbol/homo_sapiens/"
MONARCH_API = "https://api.monarchinitiative.org/api/bioentity/gene/"

# Define genes to extract (assumed from knowledge graph context)
# TODO: Example genes; replace with actual mentions from PMID: 38790019
TEST_GENES = ["BRCA1", "TP53", "EGFR", "PTEN", "AKT1"] 

