import mysql.connector as mysql

class Database:
    def __init__(self, host, user, password, database):
        self.db = mysql.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        if self.db.is_connected():
            db_Info = self.db.get_server_info()
            print("Connected to MySQL database... MySQL Server version on ", db_Info)

    def create_database_if_not_exists(self):
        cursor = self.db.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS mtg_arena_helper")
        cursor.execute("USE mtg_arena_helper")

    def create_table_if_not_exists(self):
        cursor = self.db.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS cards(id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), type VARCHAR(255), colors VARCHAR(255), cost VARCHAR(255), power INT, toughness INT, text TEXT)")
        self.db.commit()

    def close(self):
        if self.db.is_connected():
            self.db.close()
            print("Database connection closed.")
