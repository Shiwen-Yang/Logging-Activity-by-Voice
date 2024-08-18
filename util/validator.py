import datetime
import threading
from playsound import playsound

def validate_entry(cursor, table_name, entered_data):
    cursor.execute(f"PRAGMA table_info({table_name})")
    column_info = cursor.fetchall()

    for col, entry_value in entered_data.items():
        col_type = next(info[2] for info in column_info if info[1] == col)

        if col_type == "INTEGER":
            if not entry_value.isdigit():
                return f"'{col}' must be an integer."
        elif col_type == "REAL":
            try:
                float(entry_value)
            except ValueError:
                return f"'{col}' must be a number."
        elif col_type == "DATE":
            try:
                datetime.datetime.strptime(entry_value, '%m/%d/%Y')
            except ValueError:
                return f"'{col}' must be in the format MM/DD/YYYY."
    return None

def has_autoincrement(cursor, table_name):
    # Get the SQL used to create the table
    cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    create_table_sql = cursor.fetchone()[0]
    
    # Check if AUTOINCREMENT is present in the table creation SQL
    if "AUTOINCREMENT" in create_table_sql.upper():
        return True
    return False

def calculate_optimal_column_width(cursor, table_name):
    # Fetch the first row of data from the selected table
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
    row_data = cursor.fetchone()

    # Get column names
    columns = [desc[0] for desc in cursor.description]

    # Calculate the optimal width for each column
    column_widths = {}
    if row_data:
        for col, data in zip(columns, row_data):
            # Calculate the width based on the header and the first row data
            max_width = max(int(len(str(col))/3), len(str(data))) * 10
            column_widths[col] = max_width

    return column_widths


def play_sound_in_background():
    threading.Thread(target=playsound, args=(r"support_files/ding.mp3",), daemon=True).start()
    
def calculate_width(text, padding=0):
    return len(text) * 5 + padding

columns = {
    "speaker": {"text": "Speaker"},
    "date": {"text": "Date"},
    "time": {"text": "time"},
    "activity": {"text": "Activity"},
    "details": {"text": "Details"},
    "transcript": {"text": "Transcript"}
}
