% sqlite3 gene_database.db                   
SQLite version 3.45.1 2024-01-30 16:01:20
Enter ".help" for usage hints.
sqlite> select hg.HGNC_ID, hg.Disease
from hgnc_genes hg;
HGNC:1100|
HGNC:11998|
HGNC:3236|
HGNC:9588|
HGNC:391|
sqlite> select hg.HGNC_Gene_Name, ga.alias_name
from hgnc_genes hg
join gene_aliases ga on hg.HGNC_ID = ga.HGNC_ID
order by hg.HGNC_Gene_Name, ga.alias_name;
AKT serine/threonine kinase 1|AKT
AKT serine/threonine kinase 1|PKB
AKT serine/threonine kinase 1|PRKBA
AKT serine/threonine kinase 1|RAC
AKT serine/threonine kinase 1|RAC-alpha
BRCA1 DNA repair associated|BRCC1
BRCA1 DNA repair associated|FANCS
BRCA1 DNA repair associated|PPP1R53
BRCA1 DNA repair associated|RNF53
epidermal growth factor receptor|ERBB1
epidermal growth factor receptor|ERRP
phosphatase and tensin homolog|MMAC1
phosphatase and tensin homolog|PTEN1
phosphatase and tensin homolog|TEP1
tumor protein p53|LFS1
tumor protein p53|p53
sqlite> 