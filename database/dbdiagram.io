Table hgnc_genes {
  HGNC_ID           text [pk] // Primary key
  HGNC_Gene_Name    text [not null]
  Hg38_Coordinates  text
  Hg19_Coordinates  text
  Disease           text

  Indexes {
    (HGNC_Gene_Name)
  }
}

Table gene_aliases {
  alias_id    int [pk, increment] // Auto-increment primary key
  HGNC_ID     text [not null, ref: > hgnc_genes.HGNC_ID]
  alias_name  text [not null]

  Indexes {
    (alias_name)
  }
}
