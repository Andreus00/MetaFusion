from functools import wraps
import sqlite3
from typing import Any
import os

class DatabaseConnection(object):
	def __init__(self) -> None:
		if os.path.exists("tracker.db"):
			os.remove("tracker.db")
		con = sqlite3.connect("tracker.db")
		self.con = con
	
	def __call__(self) -> sqlite3.Connection:
		return self.con
	
	def get_cursor(self):
		return self.con.cursor()
	
	def commit(self):
		self.con.commit()

    
class CreateDatabase(object):
	
	def __init__(self, connection: DatabaseConnection) -> None:
		self.connection = connection()
		self.db_created = False

	def __call__(self):
		if self.db_created:
			return
		connection = self.connection
		cur = connection.cursor()
		try:

			cur = connection.cursor()
			cur.execute("CREATE TABLE IF NOT EXISTS Packets(id VARCHAR(65) PRIMARY KEY, isListed BIT DEFAULT 0, price INT DEFAULT 1, userHex VARCHAR(65) NOT NULL);")
			cur.execute("CREATE TABLE IF NOT EXISTS Prompts(id VARCHAR(65) PRIMARY KEY, ipfsHash VARCHAR(35) NOT NULL, isListed BIT DEFAULT 0, price INT DEFAULT 1, BIT isFreezed DEFAULT 0, userHex VARCHAR(65) NOT NULL, name TEXT);")
			cur.execute("CREATE TABLE IF NOT EXISTS Images(id VARCHAR(65) PRIMARY KEY, ipfsHash VARCHAR(35) NOT NULL, isListed BIT DEFAULT 0, price INT DEFAULT 1, userHex VARCHAR(65) NOT NULL);")
			cur.execute("CREATE TABLE IF NOT EXISTS SellEvents(id INTEGER PRIMARY KEY AUTOINCREMENT, objId VARCHAR(65), userFromHex VARCHAR(65) NOT NULL, userToHex VARCHAR(65) NOT NULL, price INT DEFAULT 0, type TINYINT CHECK(type IN (0, 1, 2)));") # 0 = Packet, 1 = Prompts, 2 = Images
			cur.execute("CREATE INDEX IF NOT EXISTS userPacketsIndex ON Packets(userHex);")
			cur.execute("CREATE INDEX IF NOT EXISTS userPromptsIndex ON Prompts(userHex);")
			cur.execute("CREATE INDEX IF NOT EXISTS userImagesIndex ON Images(userHex);")
			cur.execute("CREATE INDEX IF NOT EXISTS sellEventObjIndex ON SellEvents(objId, type);")
			connection.commit()
		finally:
			cur.close()
		self.db_created = True

	def create(self):
		self()