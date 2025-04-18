import pandas as pd
import pymysql
from sqlalchemy import create_engine
# TODO: Add use of logging.

# TODO: Move these to .env file:
# MySQL connection details
MYSQL_USER = "your_username"
MYSQL_PASSWORD = "your_password"
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_DB = "gene_database"

# Read CSV
df = pd.read_csv("gene_metadata.csv")

# Create SQLAlchemy engine for MySQL
engine = create_engine(f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}")

# Insert into hgnc_genes (exclude Gene_Aliases)
hgnc_df = df[["HGNC_ID", "HGNC_Gene_Name", "Hg38_Coordinates", "Hg19_Coordinates", "Disease"]]
hgnc_df.to_sql("hgnc_genes", con=engine, if_exists="append", index=False, method="multi")

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
    aliases_df.to_sql("gene_aliases", con=engine, if_exists="append", index=False, method="multi")

# Done
engine.dispose()
