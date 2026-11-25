import sqlite3
from pathlib import Path
import pandas as pd

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "disastermatrix.db"

def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.execute("""CREATE TABLE IF NOT EXISTS readings (
        id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT NOT NULL,
        city TEXT, water_depth_cm REAL, distance_cm REAL, soil_moisture_pct REAL,
        water_sensor INTEGER, pump_status INTEGER, mode TEXT, risk_score REAL,
        experiment TEXT, note TEXT)""")
    con.execute("""CREATE TABLE IF NOT EXISTS chat (
        id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT NOT NULL,
        session TEXT, role TEXT, message TEXT)""")
    con.commit()
    return con

def save_reading(**row):
    con=connect()
    con.execute("""INSERT INTO readings(timestamp,city,water_depth_cm,distance_cm,
    soil_moisture_pct,water_sensor,pump_status,mode,risk_score,experiment,note)
    VALUES(:timestamp,:city,:water_depth_cm,:distance_cm,:soil_moisture_pct,
    :water_sensor,:pump_status,:mode,:risk_score,:experiment,:note)""", row)
    con.commit(); con.close()

def history(limit=1000):
    con=connect()
    df=pd.read_sql_query("SELECT * FROM readings ORDER BY id DESC LIMIT ?",con,params=(limit,))
    con.close()
    return df

def save_chat(session, role, message, timestamp):
    con=connect()
    con.execute("INSERT INTO chat(timestamp,session,role,message) VALUES(?,?,?,?)",
                (timestamp,session,role,message))
    con.commit(); con.close()

def get_chat(session):
    con=connect()
    df=pd.read_sql_query("SELECT role,message,timestamp FROM chat WHERE session=? ORDER BY id",con,params=(session,))
    con.close(); return df

def clear_chat(session):
    con=connect(); con.execute("DELETE FROM chat WHERE session=?",(session,)); con.commit(); con.close()
