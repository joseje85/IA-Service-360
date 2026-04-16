import pyodbc

def get_connection():
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=172.31.5.146;"
        "DATABASE=Informacion_Estatal;"
        "UID=ollama;"
        "PWD=Temporal2026@"
    )
    return conn