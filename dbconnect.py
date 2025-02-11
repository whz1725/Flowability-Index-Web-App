import sqlite3

def connection():
    conn = sqlite3.connect('materials.db')
    c =conn.cursor()
    return c, conn

def create_table():
    # Setup connection
    c, conn = connection()

    # Create table
    c.execute('''CREATE TABLE materials
                (MaterialName text, AngleofRepose text, Compressibility text, AngleofSpatula text, UniformityCoeff text, Cohesion text, FlowabilityPoints text, Flowability text)''')

    # Save (commit) the changes
    conn.commit()

    # Close the connection
    conn.close()

def delete_table():
    c, conn = connection()
    c.execute('DROP TABLE materials')
    conn.commit()
    conn.close()

def check_existing_table():
    c, conn = connection()
    c.execute("SELECT name FROM sqlite_master WHERE type = 'table';")
    print(c.fetchall())
    conn.commit()
    conn.close()

def check_table_schemata(name):
    # name: ('materials',)
    c, conn = connection()
    c.execute("SELECT sql FROM sqlite_master WHERE type = 'table' and name = ?;", name)
    print(c.fetchall())
    conn.commit()
    conn.close()

def show_table_content(name):
    # name: 'materials'
    c, conn = connection()
    c.execute("SELECT * FROM {n};".format(n=name))
    print(c.fetchall())
    conn.commit()
    conn.close()