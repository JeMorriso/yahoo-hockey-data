import mysql.connector
import os

db = mysql.connector.connect(
  host=os.getenv("HOST"),
  user=os.getenv("USER"),
  passwd=os.getenv("PASSWORD")
)

print('aloha heroku')
print("please?")