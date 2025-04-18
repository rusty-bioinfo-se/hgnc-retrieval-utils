import requests
import json
from Bio import Entrez
import time
import spacy
from scispacy.abbreviation import AbbreviationDetector
import re

# TODO: Add proper command-line argument parsing.
DEFAULT_PMID = "38790019"

# TODO: Add support to retrieve PMID values from input file.


# Replace with your email (required by NCBI)
# TODO: move service account into conf/config.yaml and default in constants.py.
Entrez.email = "jsundaram@baylorgenetics.com"

# Load SciSpaCy models
print("Loading SciSpaCy models...")
try:
    nlp_bionlp = spacy.load("en_ner_bionlp13cg_md")
    nlp_bionlp.add_pipe("abbreviation_detector")
    print("Loaded en_ner_bionlp13cg_md")
except Exception as e:
    print(f"Error loading en_ner_bionlp13cg_md: {e}")
    nlp_bionlp = None

try:
    nlp_bc5cdr = spacy.load("en_ner_bc5cdr_md")
    nlp_bc5cdr.add_pipe("abbreviation_detector")
    print("Loaded en_ner_bc5cdr_md")
except Exception as e:
    print(f"Error loading en_ner_bc5cdr_md: {e}")
    nlp_bc5cdr = None

def get_gene_symbols_from_pubtator(pmid):
    print(f"Querying PubTator for PMID {pmid}...")
    url = f"https://www.ncbi.nlm.nih.gov/research/pubtator-api/publications/export/biocjson?pmids={pmid}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        gene_symbols = set()
        for passage in data.get('passages', []):
            for annotation in passage.get('annotations', []):
                if annotation.get('infons', {}).get('type') == 'Gene':
                    gene_symbol = annotation.get('text')
                    if gene_symbol:
                        gene_symbols.add(gene_symbol)
        
        print(f"PubTator raw annotations for PMID {pmid}: {[ann for passage in data.get('passages', []) for ann in passage.get('annotations', [])]}")
        return list(gene_symbols)
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from PubTator: {e}")
        return []

def get_gene_symbols_from_entrez(pmid):
    print(f"Querying Entrez for PMID {pmid}...")
    try:
        handle = Entrez.elink(dbfrom="pubmed", db="gene", id=pmid)
        links = Entrez.read(handle)
        handle.close()
        
        gene_symbols = set()
        linksetdb = links[0].get('LinkSetDb', [])
        if not linksetdb:
            print(f"No gene links found in Entrez for PMID {pmid}")
            return []
        
        gene_ids = [link['Id'] for link in linksetdb[0].get('Link', [])]
        if not gene_ids:
            print(f"No gene IDs found in Entrez for PMID {pmid}")
            return []
        
        for gene_id in gene_ids:
            time.sleep(0.34)  # Respect NCBI rate limits
            handle = Entrez.efetch(db="gene", id=gene_id, retmode="xml")
            gene_record = Entrez.read(handle)
            handle.close()
            
            symbol = gene_record[0].get('Entrezgene_gene', {}).get('Gene-ref', {}).get('Gene-ref_locus', '')
            if symbol:
                gene_symbols.add(symbol)
        
        return list(gene_symbols)
    
    except Exception as e:
        print(f"Error fetching gene symbols from Entrez: {e}")
        return []

def get_gene_symbols_from_europe_pmc(pmid):
    print(f"Querying Europe PMC for PMID {pmid}...")
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/PMC/{pmid}/annotations"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        gene_symbols = set()
        for annotation in data.get('annotations', []):
            if annotation.get('type') == 'Gene':
                gene_symbol = annotation.get('exact')
                if gene_symbol:
                    gene_symbols.add(gene_symbol)
        
        print(f"Europe PMC raw annotations for PMID {pmid}: {data.get('annotations', [])}")
        return list(gene_symbols)
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Europe PMC data: {e}")
        return []

def get_gene_symbols_from_scispacy(text):
    print("Processing text with SciSpaCy...")
    gene_symbols = set()
    
    if nlp_bionlp:
        try:
            doc = nlp_bionlp(text)
            gene_symbols.update(ent.text for ent in doc.ents if ent.label_ == "GENE_OR_GENE_PRODUCT")
            print("Processed with en_ner_bionlp13cg_md")
        except Exception as e:
            print(f"Error in SciSpaCy bionlp processing: {e}")
    
    if nlp_bc5cdr:
        try:
            doc = nlp_bc5cdr(text)
            gene_symbols.update(ent.text for ent in doc.ents if ent.label_ == "GENE_OR_GENE_PRODUCT")
            print("Processed with en_ner_bc5cdr_md")
        except Exception as e:
            print(f"Error in SciSpaCy bc5cdr processing: {e}")
    
    return list(gene_symbols)

def get_gene_symbols_from_regex(text):
    print("Processing text with regex...")
    pattern = r'\b[A-Z0-9]{3,10}\b'
    matches = re.findall(pattern, text)
    
    # Exclude known non-gene terms
    gene_symbols = [m for m in matches if m not in ['ES', 'GS', 'EGBP', 'NGS', 'PRaUD']]
    return list(set(gene_symbols))

def get_article_details(pmid):
    print(f"Fetching article details for PMID {pmid}...")
    try:
        handle = Entrez.efetch(db="pubmed", id=pmid, retmode="xml")
        records = Entrez.read(handle)
        handle.close()
        
        article = records['PubmedArticle'][0]
        title = article['MedlineCitation']['Article']['ArticleTitle']
        abstract = article['MedlineCitation']['Article'].get('Abstract', {}).get('AbstractText', ['No abstract'])[0]
        return title, abstract
    except Exception as e:
        print(f"Error fetching article details: {e}")
        return "Unknown title", "Unknown abstract"

def get_gene_symbols(pmid):
    print(f"Starting gene symbol extraction for PMID {pmid}...")
    try:
        # Try PubTator
        gene_symbols = get_gene_symbols_from_pubtator(pmid)
        if gene_symbols:
            print(f"Gene symbols from PubTator for PMID {pmid}: {gene_symbols}")
            return gene_symbols
        print(f"No gene symbols found in PubTator for PMID {pmid}")
        
        # Try Entrez
        gene_symbols = get_gene_symbols_from_entrez(pmid)
        if gene_symbols:
            print(f"Gene symbols from Entrez for PMID {pmid}: {gene_symbols}")
            return gene_symbols
        print(f"No gene symbols found in Entrez for PMID {pmid}")
        
        # Try Europe PMC
        gene_symbols = get_gene_symbols_from_europe_pmc(pmid)
        if gene_symbols:
            print(f"Gene symbols from Europe PMC for PMID {pmid}: {gene_symbols}")
            return gene_symbols
        print(f"No gene symbols found in Europe PMC for PMID {pmid}")
        
        # Try SciSpaCy on title and abstract
        title, abstract = get_article_details(pmid)
        text = f"{title} {abstract}"
        gene_symbols = get_gene_symbols_from_scispacy(text)
        if gene_symbols:
            print(f"Gene symbols from SciSpaCy for PMID {pmid}: {gene_symbols}")
            return gene_symbols
        print(f"No gene symbols found in SciSpaCy for PMID {pmid}")
        
        # Fallback to regex
        gene_symbols = get_gene_symbols_from_regex(text)
        if gene_symbols:
            print(f"Gene symbols from regex for PMID {pmid}: {gene_symbols}")
        else:
            print(f"No gene symbols found in regex for PMID {pmid}")
        return gene_symbols
    
    except Exception as e:
        print(f"Unexpected error in get_gene_symbols: {e}")
        return []


if __name__ == "__main__":
    try:
        pmid = DEFAULT_PMID 
        gene_symbols = get_gene_symbols(pmid)
        
        # Fetch and display article details
        title, abstract = get_article_details(pmid)
        print(f"Title: {title}")
        print(f"Abstract: {abstract}")
    except Exception as e:
        print(f"Main execution failed: {e}")