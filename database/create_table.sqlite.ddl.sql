-- Table to store gene metadata from PMID: 38790019
CREATE TABLE hgnc_genes (
    HGNC_ID TEXT PRIMARY KEY,
    HGNC_Gene_Name TEXT NOT NULL,
    Hg38_Coordinates TEXT,
    Hg19_Coordinates TEXT,
    Disease TEXT
);

-- Table to store gene aliases, normalized from comma-separated values
CREATE TABLE gene_aliases (
    alias_id INTEGER PRIMARY KEY AUTOINCREMENT,
    HGNC_ID TEXT NOT NULL,
    alias_name TEXT NOT NULL,
    FOREIGN KEY (HGNC_ID) REFERENCES hgnc_genes(HGNC_ID) ON DELETE CASCADE
);

-- Index on HGNC_Gene_Name for faster searches
CREATE INDEX idx_hgnc_gene_name ON hgnc_genes (HGNC_Gene_Name);

-- Index on alias_name for faster alias searches
CREATE INDEX idx_alias_name ON gene_aliases (alias_name);