import duckdb
from pathlib import Path

BASE = Path(__file__).resolve().parent
db_path = BASE / "agri_validation.duckdb"

con = duckdb.connect(str(db_path))

print("Loading Telangana CSVs...")

files = list(BASE.glob("*.csv"))
for f in files:
    print("Found:", f.name)

# Load all CSVs into one raw table
con.execute("""
CREATE OR REPLACE TABLE tg_raw AS
SELECT *,
       filename AS source_file
FROM read_csv_auto('*.csv', filename=True);
""")

print("Total Telangana rows:",
      con.execute("SELECT COUNT(*) FROM tg_raw").fetchone()[0])

print("\nSample columns:")
print(con.execute("DESCRIBE tg_raw").fetchall())

con.close()
print("\nDatabase created:", db_path)

