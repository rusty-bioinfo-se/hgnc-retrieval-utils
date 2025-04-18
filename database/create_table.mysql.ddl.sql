-- Table to store gene metadata from PMID: 38790019
CREATE TABLE hgnc_genes (
    HGNC_ID VARCHAR(50) PRIMARY KEY,
    HGNC_Gene_Name VARCHAR(255) NOT NULL,
    Hg38_Coordinates VARCHAR(255),
    Hg19_Coordinates VARCHAR(255),
    Disease TEXT
) ENGINE=InnoDB;

-- Table to store gene aliases, normalized from comma-separated values
CREATE TABLE gene_aliases (
    alias_id INT AUTO_INCREMENT PRIMARY KEY,
    HGNC_ID VARCHAR(50) NOT NULL,
    alias_name VARCHAR(255) NOT NULL,
    FOREIGN KEY (HGNC_ID) REFERENCES hgnc_genes(HGNC_ID) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Index on HGNC_Gene_Name for faster searches
CREATE INDEX idx_hgnc_gene_name ON hgnc_genes (HGNC_Gene_Name);

-- Index on alias_name for faster alias searches
CREATE INDEX idx_alias_name ON gene_aliases (alias_name);
