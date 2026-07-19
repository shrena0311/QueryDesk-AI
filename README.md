# Query Desk — Text-to-SQL Agent (Superstore data)

Ask questions about real retail sales data in plain English. The agent
writes the SQL itself, runs it, and answers you in a normal sentence. If a
query fails, it reads the error and fixes it on its own before retrying.

Built on the Kaggle "Superstore" sales dataset (`train.csv`) — 9,800 real
orders with customers, regions, categories, products, and sales figures.

## What's inside

- `train.csv` — the raw dataset (from Kaggle).
- `load_data.py` — loads `train.csv` into `store.db`, a SQLite database.
- `sql_agent.py` — the agent: reads the schema, generates SQL with an LLM,
  runs it safely (SELECT only), and explains the result.
- `app.py` — the Streamlit app with the custom "Query Desk" interface.

## Where to open this project

These are plain Python files (`.py`), not a Jupyter notebook and not a SQL
script — so Google Colab and SQL Workbench aren't the right place for them.
Use one of these instead:

- **VS Code** (recommended): Download and install [VS Code](https://code.visualstudio.com/),
  then File → Open Folder → select this project folder. You'll see and edit
  all the code there, and can open a terminal inside it (Terminal → New Terminal)
  to run the commands below.
- **Any plain text editor** (Notepad, Notepad++) also works just to *view*
  the code, but you'll still need a terminal (Command Prompt / Anaconda
  Prompt) to actually run it — Notepad can't run Python by itself.

Either way, the app itself doesn't open as a file you double-click — you
run a command, and it opens automatically in your web browser.

## Setup

1. Open a terminal in this folder.

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Get a free API key from [console.groq.com](https://console.groq.com) and
   set it as an environment variable.

   Windows (Command Prompt / Anaconda Prompt):
   ```
   set GROQ_API_KEY=your_key_here
   ```
   Mac/Linux:
   ```
   export GROQ_API_KEY=your_key_here
   ```

4. Load the dataset into SQLite:
   ```
   python load_data.py
   ```

5. Run the app:
   ```
   streamlit run app.py
   ```
   A browser tab will open automatically at `http://localhost:8501`.

## Example questions to try

- "Which category made the most sales?"
- "Top 5 customers by total spend"
- "Sales by region in 2017"
- "Which sub-category sells the most in the West?"
- "How many orders were shipped Same Day?"

## How it works

1. The agent reads the actual table and column names from `store.db`, so it
   never has to guess the schema.
2. It sends your question plus the schema to an LLM (Groq's Llama 3.1) and
   asks for a single SELECT query back.
3. Before running anything, it checks the query starts with `SELECT` — no
   DELETE, DROP, or UPDATE can ever slip through.
4. If the query fails (bad column name, syntax issue, etc.), the error
   message is sent back to the LLM so it can fix its own mistake. This
   retries up to 2 times.
5. Once a query succeeds, the raw rows go back to the LLM one more time,
   just to turn them into a normal sentence instead of a table of numbers.

## Notes

- Only SELECT queries are allowed — the database can't be modified through
  the agent, by design.
- Re-run `load_data.py` any time you want to reset `store.db` back to the
  original data.
