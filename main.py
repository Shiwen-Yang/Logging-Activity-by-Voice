from util.UI import DatabaseApp
import sqlite3

import yaml
with open("support_files/config.yaml", 'r') as file:
    configuration = yaml.safe_load(file)
database = configuration['database']

# Start the application
if __name__ == "__main__":
    # Connect to your database
    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    # Execute a query to get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence';")
    # Fetch all table names
    table_names = cursor.fetchall()
    # Extract table names from tuples
    table_names = [name[0] for name in table_names]  

    app = DatabaseApp(database, table_names)
    app.mainloop()