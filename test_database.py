import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

connection = pymysql.connect(
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    ssl={
        "ca": os.getenv("DB_SSL_CA")
    }
)

try:
    print("Connected to ToolTrack database successfully!")

    with connection.cursor() as cursor:
        cursor.execute("SELECT DATABASE();")
        result = cursor.fetchone()
        print("Current database:", result[0])

finally:
    connection.close()