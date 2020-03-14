import mysql.connector
import os

def connect():
  return mysql.connector.connect(
    host=os.getenv("HOST"),
    user=os.getenv("USER"),
    passwd=os.getenv("PASSWORD")
  )