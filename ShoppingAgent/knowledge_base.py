import sqlite3
import os

DB_FILE = "shops.db"

class KnowledgeBase:
    def __init__(self) -> None:
        self.conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        self.create_table()

    def create_table(self) -> None:
        """Creates the shops table if it doesn't exists."""
        with self.conn:
            self.conn.execute("""
                              CREATE TABLE IF NOT EXISTS shops (
                                  id INTEGER PRIMARY KEY,
                                  name TEXT NOT NULL UNIQUE,
                                  scope TEXT,
                                  mcp_enabled BOOLEAN,
                                  api_enabled BOOLEAN,
                                  scraping_enabled BOOLEAN,
                                  mcp_url TEXT,
                                  api_url TEXT,
                                  -- Performance Metrics
                                  mcp_latency REAL DEFAULT 0.0,
                                  mcp_success_rate REAL DEFAULT 1.0,
                                  api_latency REAL DEFAULT 0.0,
                                  api_success_rate REAL DEFAULT 1.0,
                                  scraping_latency REAL DEFAULT 0.0,
                                  scraping_success_rate REAL DEFAULT 1.0,
                                  total_requests INTEGER DEFAULT 0
                              )
                              """)

    def add_shop(self, name, scope, mcp_enabled=False, api_enabled=False, scraping_enabled=True, mcp_url=None, api_url=None):
        """
        Adds a new shop if it doesn't exist. Uses INSERT OR IGNORE to prevent
        crashing on duplicate names.
        """
        with self.conn:
            cursor = self.conn.execute(
                "INSERT OR IGNORE INTO shops (name, scope, mcp_enabled, api_enabled, scraping_enabled, mcp_url, api_url) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (name, scope, mcp_enabled, api_enabled, scraping_enabled, mcp_url, api_url)
            )
            # The cursor.rowcount will be 1 if a row was inserted, and 0 if it was ignored.
            if cursor.rowcount > 0:
                print(f"[KB] Added Shop: {name}")
            else:
                print(f"[KB] Shop '{name}' already exists. Ignoring duplicate.")

    def get_all_shops(self):
        """Retrieves all shops and their details from the database."""
        cursor = self.conn.execute("SELECT * FROM shops")
        # Converse rows to dictionaries for easier access
        rows = cursor.fetchall()
        cols = [column[0] for column in cursor.description]
        return [dict(zip(cols, row)) for row in rows]

    def get_shop_by_name(self, name):
        """Retrieves a single shop by its name."""
        cursor = self.conn.execute("SELECT * FROM shops WHERE name = ?", (name,))
        row = cursor.fetchone()
        if not row:
            return None
        cols = [column[0] for column in cursor.description]
        return dict(zip(cols, row))

    def update_shop_performance(self, shop_name, method, latency, success):
        """Updates the performance metrics for a shop's communication method using a moving average"""
        shop = self.get_shop_by_name(shop_name)
        if not shop:
            print(f"[KB] Could not find shop '{shop_name}' to update.")
            return None

        total_requests = shop['total_requests'] + 1

        # Get current metrics
        old_latency = shop[f'{method}_latency']
        old_success_rate = shop[f'{method}_success_rate']

        # Calculate new moving average
        # Succes is 1, Failure is 0
        success_val = 1 if success else 0
        new_success_rate = ((old_success_rate * (total_requests - 1)) + success_val) / total_requests
        new_latency = ((old_latency * (total_requests - 1)) + latency) / total_requests if success else old_latency

        with self.conn:
            self.conn.execute(
                f"""UPDATE shops SET
                    {method}_latency = ?,
                    {method}_success_rate = ?,
                    total_requests = ?
                    WHERE name = ?""",
                (new_latency, new_success_rate, total_requests, shop_name)
            )
        print(f"[KB] Updated performance for '{shop_name}' ({method}): Success={success}, Latency={latency:.2f}s")
