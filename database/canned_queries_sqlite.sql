--
-- Query 1: HGNC ID and disease connection
--
select hg.HGNC_ID, hg.Disease
from hgnc_genes hg;

--
-- Query 2: HGNC Gene Name and any gene name aliases parsed
--
select hg.HGNC_Gene_Name, ga.alias_name
from hgnc_genes hg
join gene_aliases ga on hg.HGNC_ID = ga.HGNC_ID
order by hg.HGNC_Gene_Name, ga.alias_name;
