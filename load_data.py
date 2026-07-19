"""
Loads train.csv (the Superstore sales dataset from Kaggle) into a SQLite
database called store.db, so the agent has real data to query.

Run this once before starting the app.
"""

import sqlite3
import pandas as pd

df = pd.read_csv("train.csv")

# a couple of small cleanups so the data plays nicely with SQL later
df["Order Date"] = pd.to_datetime(df["Order Date"], format="%d/%m/%Y")
df["Ship Date"] = pd.to_datetime(df["Ship Date"], format="%d/%m/%Y")
df["Postal Code"] = df["Postal Code"].fillna(0).astype(int)

# rename columns to remove spaces and dashes, makes writing SQL less error-prone
df.columns = [col.replace(" ", "_").replace("-", "_") for col in df.columns]

conn = sqlite3.connect("store.db")
df.to_sql("orders", conn, if_exists="replace", index=False)
conn.close()

print(f"store.db created with {len(df)} rows in the 'orders' table.")
