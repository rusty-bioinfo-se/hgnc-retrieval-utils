import pandas as pd
import sqlite3

# Read CSV
df = pd.read_csv("gene_metadata.csv")

# Connect to SQLite
conn = sqlite3.connect("gene_database.db")
conn.execute("PRAGMA foreign_keys = ON;")

# Insert into hgnc_genes (exclude Gene_Aliases)
hgnc_df = df[["HGNC_ID", "HGNC_Gene_Name", "Hg38_Coordinates", "Hg19_Coordinates", "Disease"]]
hgnc_df.to_sql("hgnc_genes", conn, if_exists="append", index=False)

# Insert into gene_aliases
aliases_data = []
for _, row in df.iterrows():
    hgnc_id = row["HGNC_ID"]
    aliases = row["Gene_Aliases"].split(",") if pd.notna(row["Gene_Aliases"]) else []
    for alias in aliases:
        if alias.strip():  # Skip empty aliases
            aliases_data.append({"HGNC_ID": hgnc_id, "alias_name": alias.strip()})

if aliases_data:
    aliases_df = pd.DataFrame(aliases_data)
    aliases_df.to_sql("gene_aliases", conn, if_exists="append", index=False)

# Close connection
conn.close()