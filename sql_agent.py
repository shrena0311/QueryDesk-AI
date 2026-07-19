"""
The agent itself. Give it a plain English question, it writes SQL,
runs it safely against store.db, and explains the answer back to you.
"""

import os
import sqlite3
from groq import Groq

DB_PATH = "store.db"
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"


def get_schema():
    """Reads table and column names straight from the database, so the LLM
    always knows the real structure instead of guessing."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]

    schema_text = ""
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cursor.fetchall()]
        schema_text += f"Table {table}: {', '.join(columns)}\n"

    conn.close()
    return schema_text


def generate_sql(question, schema):
    """Asks the LLM to turn a plain English question into a SQL query."""
    prompt = f"""You are a SQL expert. Given this database schema:

{schema}

Write a single SQLite SELECT query that answers this question:
"{question}"

Rules:
- Only use SELECT statements, nothing else.
- Column names with special characters may need square brackets, e.g. [Sub_Category].
- Dates are stored as timestamps, use functions like strftime() if filtering by month or year.
- Return ONLY the SQL query, no explanation, no markdown formatting.
"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    sql = response.choices[0].message.content.strip()
    sql = sql.replace("```sql", "").replace("```", "").strip()
    return sql


def run_query(sql):
    """Executes the query, but only if it's a safe read-only SELECT."""
    if not sql.lower().startswith("select"):
        raise ValueError("Only SELECT queries are allowed.")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(sql)
    columns = [description[0] for description in cursor.description]
    rows = cursor.fetchall()
    conn.close()
    return columns, rows


def explain_result(question, columns, rows):
    """Turns the raw query result into a plain English answer."""
    if not rows:
        return "I ran the query but got no matching results."

    result_text = f"Columns: {columns}\nRows: {rows[:20]}"
    prompt = f"""The user asked: "{question}"

Here is the query result:
{result_text}

Answer the user's question in one or two plain, friendly sentences using this data.
Do not mention SQL or columns, just give the answer naturally.
"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()


def ask(question, retries=2):
    """The main agent loop: generate SQL, run it, self-correct if it fails,
    then explain the result."""
    schema = get_schema()
    sql = generate_sql(question, schema)

    last_error = None
    for attempt in range(retries + 1):
        try:
            columns, rows = run_query(sql)
            answer = explain_result(question, columns, rows)
            return {"sql": sql, "answer": answer, "columns": columns, "rows": rows}
        except Exception as error:
            last_error = str(error)
            fix_prompt = f"""This SQL query failed:
{sql}

Error: {last_error}

Schema:
{schema}

Fix the query. Return ONLY the corrected SQL, no explanation."""
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": fix_prompt}],
                temperature=0,
            )
            sql = response.choices[0].message.content.strip()
            sql = sql.replace("```sql", "").replace("```", "").strip()

    return {"sql": sql, "answer": f"Couldn't get a working query. Last error: {last_error}", "columns": [], "rows": []}
