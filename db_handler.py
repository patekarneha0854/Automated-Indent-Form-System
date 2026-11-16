import sqlite3
import pandas as pd

# Define the local SQLite database file path
# The database will be stored inside the 'database' folder as 'indent_system.db'
DB_FILE = "database/indent_system.db"

def init_db():
    """
    Initializes the SQLite database.
    1. Connects to (or creates) the database file.
    2. Creates the 'equipment' table if it does not already exist.
    3. Populates the table with initial sample data if the table is currently empty.
    """
    # Establish a connection to the SQLite database file
    conn = sqlite3.connect(DB_FILE)
    
    # Create a cursor object to execute SQL commands and queries
    cursor = conn.cursor()
    
    # SQL query to create the equipment table with structured attributes
    # AUTOINCREMENT: Automatically assigns a unique ID to every new item added
    # NOT NULL: Ensures critical fields like item name, category, and price are mandatory
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS equipment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            category TEXT NOT NULL,
            manufacturer TEXT,
            model TEXT,
            part_number TEXT,
            unit_price REAL NOT NULL,
            description TEXT
        )
    ''')
    
    # Execute a query to count how many records currently exist in the equipment table
    cursor.execute("SELECT COUNT(*) FROM equipment")
    
    # fetchone()[0] gets the count integer value
    # If count == 0, it means the database is freshly created and empty
    if cursor.fetchone()[0] == 0:
        # Array of tuple records containing dummy equipment data for testing and initial application use
        sample_items = [
            ("Oscilloscope", "R&D Equipment", "Tektronix", "TBS1104", "TK-101", 45000.0, "100 MHz, 4-Channel Digital Storage Oscilloscope"),
            ("PlutoSDR", "R&D Equipment", "Analog Devices", "ADALM-PLUTO", "AD-PLUTO-01", 25000.0, "Active Learning RF Transceiver Module"),
            ("Digital Multimeter", "General Lab", "Fluke", "117", "FLK-117", 12000.0, "True RMS Digital Multimeter"),
            ("Desktop Computer", "MMD / Office", "Dell", "OptiPlex 7010", "DL-7010", 65000.0, "Core i7, 16GB RAM, 512GB SSD"),
            ("Soldering Station", "General Lab", "Hako", "FX-888D", "HK-888D", 85000.0, "Digital Soldering Station with Precision Iron")
        ]
        
        # executemany inserts multiple rows efficiently in a single operation
        # Parameterized placeholders (?) prevent SQL injection vulnerabilities
        cursor.executemany('''
            INSERT INTO equipment (item_name, category, manufacturer, model, part_number, unit_price, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', sample_items)
        
        # Commit (save) the insertion changes permanently into the database file
        conn.commit()
        
    # Close the database connection after setup completion
    conn.close()

def search_equipment(query=""):
    """
    Searches the equipment database using a flexible search keyword.
    
    Parameters:
    query (str): Search term provided by the user (defaults to empty string to fetch all records).
    
    Returns:
    pandas.DataFrame: A tabular Pandas DataFrame containing matching equipment records.
    """
    # Establish connection to read from database
    conn = sqlite3.connect(DB_FILE)
    
    # Construct a wildcard SQL LIKE pattern (e.g., '%oscilloscope%') for partial string matching
    query_str = f"%{query}%"
    
    # SQL query checking if the query string matches across multiple fields:
    # item_name, category, manufacturer, model, or part_number
    query_sql = '''
        SELECT id, item_name, category, manufacturer, model, part_number, unit_price, description
        FROM equipment
        WHERE item_name LIKE ? OR category LIKE ? OR manufacturer LIKE ? OR model LIKE ? OR part_number LIKE ?
    '''
    
    # Use Pandas read_sql_query to run the SQL query and automatically convert results into a DataFrame
    # Passes query_str 5 times corresponding to each '?' placeholder in the SQL query
    df = pd.read_sql_query(query_sql, conn, params=(query_str, query_str, query_str, query_str, query_str))
    
    # Close connection after reading data
    conn.close()
    
    # Return the result DataFrame back to the caller (UI component)
    return df

def add_new_equipment(item_name, category, manufacturer, model, part_number, unit_price, description):
    """
    Inserts a newly entered equipment record into the database for persistent future use.
    
    Parameters:
    item_name (str): Name of the equipment
    category (str): Equipment category (e.g., R&D Equipment, General Lab, MMD)
    manufacturer (str): Company / Make (e.g., Tektronix, Dell)
    model (str): Model number
    part_number (str): Part or Stock Keeping Unit (SKU) number
    unit_price (float): Estimated unit cost of the item
    description (str): Detailed technical specs or features
    """
    # Establish connection to write to database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Execute parameterized INSERT statement to safely write new record into table
    cursor.execute('''
        INSERT INTO equipment (item_name, category, manufacturer, model, part_number, unit_price, description)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (item_name, category, manufacturer, model, part_number, unit_price, description))
    
    # Commit transaction to persist changes in database
    conn.commit()
    
    # Close connection to release database file lock
    conn.close()