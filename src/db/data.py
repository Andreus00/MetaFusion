from typing import Dict, List, Tuple
import sqlite3
import base58
import json
import os
from ..utils.utils import *
from .database import CreateDatabase, DatabaseConnection

class Packet:
	id: int
	isListed: bool
	price: int
	userIdHex: str

	def initWithDb(self, res):
		self.id = from_str_hex_to_int_str(res[0])
		self.isListed = res[1]
		self.price = from_str_hex_to_int_str(res[2])
		self.userIdHex = res[3]
	def initWithParams(self, id, userIdHex: str, isListed: bool = False, price: int = 0, data=None):
		self.id: int = id
		self.isListed: bool = isListed
		self.price: int = price
		self.userIdHex = userIdHex
		if data is not None:
			self.writeToDb(data)
	
	def writeToDb(self, data):
		cur = data.get_cursor()
		cur.execute('INSERT OR REPLACE INTO Packets(id, isListed, price, userHex, collectionId) VALUES (?, ?, ?, ?, ?)', (from_int_to_hex_str(self.id), self.isListed, from_int_to_hex_str(self.price), self.userIdHex, self.getOriginalCollection()))
		data.con.commit()
		cur.close()

	def getIndexInCollection(self):
		return getInfoFromPacketId(self.id)[0]
	def getOriginalCollection(self):
		return getInfoFromPacketId(self.id)[1]

	def fromJson(self, data):
		self.__dict__ = json.loads(data)
	def toJson(self):
		return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)

class Prompt:
	id: int
	hash: str   # IPFS hash
	isListed: bool
	price: int
	isFreezed: bool
	userIdHex: str
	name: str
	
	def initWithDb(self, res):
		self.id = from_str_hex_to_int_str(res[0])
		self.hash = res[1]
		self.isListed = res[2]
		self.price = from_str_hex_to_int_str(res[3])
		self.isFreezed = res[4]
		self.userIdHex = res[5]
		self.name = res[6]
	def initWithParams(self, id: int, userIdHex: str, hash: str = None, name: str = None, isListed: bool = False, price: int = 0, isFreezed: bool = False, data=None):
		self.id: int = id
		self.hash: str = hash   # IPFS hash
		self.isListed: bool = isListed
		self.price: int = price
		self.isFreezed: bool = isFreezed	
		self.userIdHex: str = userIdHex
		self.name: str = name
		if data is not None:
			self.writeToDb(data)

	def writeToDb(self, data):
		cur = data.get_cursor()
		cur.execute('INSERT OR REPLACE INTO Prompts(id, ipfsHash, isListed, price, isFreezed, userHex, name, collectionId, type) VALUES (?, ?, ?, ?, ? , ?, ?, ?, ?)', (from_int_to_hex_str(self.id), self.hash, self.isListed, from_int_to_hex_str(self.price), self.isFreezed, self.userIdHex, self.name, self.getOriginalCollection(), self.getType()))
		data.con.commit()
		cur.close()

	def getPromptIndexInPacket(self):
		return getInfoFromPromptId(self.id)[0]
	def getOriginalPacketIndexInCollection(self):
		return getInfoFromPromptId(self.id)[1]
	def getType(self):
		return getInfoFromPromptId(self.id)[2]
	def getOriginalCollection(self):
		return getInfoFromPromptId(self.id)[3]
	def getPackedId(self):
		return getPackedIdFromPromptId(self.id)
	def getOriginalPacket(self, data):
		return data.get_packet(self.getPackedId())
	
	def fromJson(self, data):
		self.__dict__ = json.loads(data)
	def toJson(self):
		return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)

class Image:
	id: int
	hash: str   # IPFS hash
	isListed: bool
	price: int
	userIdHex: str

	def initWithDb(self, res):
		self.id = from_str_hex_to_int_str(res[0])
		self.hash = res[1]
		self.isListed = res[2]
		self.price = from_str_hex_to_int_str(res[3])
		self.userIdHex = res[4]
	def initWithParams(self, id: int, userIdHex: str, hash: str = None, isListed: bool = False, price: int = 0, data=None):
		self.id: int = id
		self.hash: str = hash   # IPFS hash
		self.isListed: bool = isListed
		self.price: int = price
		self.userIdHex: str = userIdHex
		if data is not None:
			self.writeToDb(data)

	def freezePrompts(self, data):
		_, prompts = getInfoFromImageId(self.id)
		for prompt in prompts:
			if prompt != 0:
				data.freeze_prompt(prompt_id=prompt)
	def unfreezePrompts(self, data):
		_, prompts = getInfoFromImageId(self.id)
		for prompt in prompts:
			if prompt != 0:
				data.unfreeze_prompt(prompt_id=prompt)
		
	def writeToDb(self, data):
		cur = data.get_cursor()
		cur.execute('INSERT OR REPLACE INTO Images(id, ipfsHash, isListed, price, userHex, collectionId) VALUES (?, ?, ?, ?, ?, ?)', (from_int_to_hex_str(self.id), self.hash, self.isListed, from_int_to_hex_str(self.price), self.userIdHex, self.getOriginalCollection()))
		data.con.commit()
		cur.close()

	def getPromptIndexInPacke_ofPrompt(self, promptNo):
		return getInfoFromPromptId(self.getPromptId(promptNo))[0]
	def getOriginalPacketIndexInCollection_ofPrompt(self, promptNo):
		return getInfoFromPromptId(self.getPromptId(promptNo))[1]
	def getType_ofPrompt(self, promptNo):
		return getInfoFromPromptId(self.getPromptId(promptNo))[2]
	def getOriginalCollection(self):
		return getInfoFromPromptId(self.getPromptId(0))[3]
	def getPackedId_ofPrompt(self, promptNo):
		return getPackedIdFromPromptId(self.getPromptId(promptNo))
	def getPromptId(self, promptNo):
		return getInfoFromImageId(self.id)[1][promptNo]
	def getSeed(self):
		return getInfoFromImageId(self.id)[0]
	def getOriginalPacket_ofPrompt(self, data, promptNo):
		return data.get_packet(getPackedIdFromPromptId(self.getPromptId(promptNo)))
	def getPrompt(self, data, promptNo):
		return data.get_prompt(self.getPromptId(promptNo))
	
	def fromJson(self, data):
		self.__dict__ = json.loads(data)
	def toJson(self):
		return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)
	


class Data:
	def __init__(self, create_db: bool = False):
		self.con = DatabaseConnection(create_db)
		
		if create_db:
			cd = CreateDatabase(self.con)
			cd.create()
		

	def get_cursor(self):
		return self.con().cursor()


	def get_packets_id_of(self, userIdHex: str):
		cur = self.get_cursor()
		try:
			ret = []
			cur.execute('SELECT * FROM Packets WHERE userHex=?', (userIdHex,))
			res = cur.fetchone()
			while res is not None:
				obj = Packet()
				obj.initWithDb(res)
				ret.append(obj)
				res = cur.fetchone()
			return ret
		finally:
			cur.close()
	
	def get_prompts_id_of(self, userIdHex: str):
		cur = self.get_cursor()
		try:
			ret = []
			cur.execute('SELECT * FROM Prompts WHERE userHex=?', (userIdHex,))
			res = cur.fetchone()
			while res is not None:
				obj = Prompt()
				obj.initWithDb(res)
				ret.append(obj)
				res = cur.fetchone()
			return ret
		finally:
			cur.close()
	
	def get_images_id_of(self, userIdHex: str):
		cur = self.get_cursor()
		try:
			ret = []
			cur.execute('SELECT * FROM Images WHERE userHex=?', (userIdHex,))
			res = cur.fetchone()
			while res is not None:
				obj = Image()
				obj.initWithDb(res)
				ret.append(obj)
				res = cur.fetchone()
			return ret
		finally:
			cur.close()
		

	def get_packet(self, packet_id: int):
		cur = self.get_cursor()
		try:
			cur.execute('SELECT * FROM Packets WHERE id=?', (from_int_to_hex_str(packet_id),))
			res = cur.fetchone()
			if res is not None:
				print(res)
				ret = Packet()
				ret.initWithDb(res)
				return ret
		finally:
			cur.close()
	
	def get_prompt(self, prompt_id: int):
		cur = self.get_cursor()
		try:
			cur.execute('SELECT * FROM Prompts WHERE id=?', (from_int_to_hex_str(prompt_id),))
			res = cur.fetchone()
			if res is not None:
				ret = Prompt()
				ret.initWithDb(res)
				return ret
		finally:
			cur.close()
	
	def get_image(self, image_id: int):
		cur = self.get_cursor()
		try:
			cur.execute('SELECT * FROM Images WHERE id=?', (from_int_to_hex_str(image_id),))
			res = cur.fetchone()
			if res is not None:
				ret = Image()
				ret.initWithDb(res)
				return ret
		finally:
			cur.close()
	
	
	def is_packet_listed(self, packet_id: int):
		cur = self.get_cursor()
		try:
			cur.execute('SELECT COUNT(DISTINCT ID) as c FROM Packets WHERE isListed=1 and id=?', (from_int_to_hex_str(packet_id),))
			# cur.execute('SELECT isListed FROM Packets WHERE id=? LIMIT 1', (from_int_to_hex_str(packet_id),))
			res = cur.fetchone()
			if res is not None:
				return res[0]
			return False
		finally:
			cur.close()
	
	def is_prompt_listed(self, prompt_id: int):
		cur = self.get_cursor()
		try:
			cur.execute('SELECT COUNT(DISTINCT ID) as c FROM Prompts WHERE isListed=1 and id=?', (from_int_to_hex_str(prompt_id),))
			# cur.execute('SELECT isListed FROM Prompts WHERE id=? LIMIT 1', (from_int_to_hex_str(packet_id),))
			res = cur.fetchone()
			if res is not None:
				return res[0]
			return False
		finally:
			cur.close()
	
	def is_image_listed(self, image_id: int):
		cur = self.get_cursor()
		try:
			cur.execute('SELECT COUNT(DISTINCT ID) as c FROM Images WHERE isListed=1 and id=?', (from_int_to_hex_str(image_id),))
			# cur.execute('SELECT isListed FROM Images WHERE id=? LIMIT 1', (from_int_to_hex_str(packet_id),))
			res = cur.fetchone()
			if res is not None:
				return res[0]
			return False
		finally:
			cur.close()
	

	def get_all_packets(self):
		cur = self.get_cursor()
		try:
			cur.execute('SELECT * FROM Packets')
			res = cur.fetchone()
			ret = []
			while res is not None:
				obj = Packet()
				obj.initWithDb(res)
				ret.append(obj)
				res = cur.fetchone()
			return ret
		finally:
			cur.close()
	
	def get_all_prompts(self):
		cur = self.get_cursor()
		try:
			cur.execute('SELECT * FROM Promps')
			res = cur.fetchone()
			ret = []
			while res is not None:
				obj = Prompt()
				obj.initWithDb(res)
				ret.append(obj)
				res = cur.fetchone()
			return ret
		finally:
			cur.close()

	
	def get_all_images(self):
		cur = self.get_cursor()
		try:
			cur.execute('SELECT * FROM Images')
			res = cur.fetchone()
			ret = []
			while res is not None:
				obj = Image()
				obj.initWithDb(res)
				ret.append(obj)
				res = cur.fetchone()
			return ret
		finally:
			cur.close()
	

	def list_packet(self, packet_id: int, price: int):
		cur = self.get_cursor()
		try:
			cur.execute('UPDATE Packets SET isListed = 1, price = ? WHERE id = ?', 
				(from_int_to_hex_str(packet_id), from_int_to_hex_str(price)))
			self.con.commit()
			return True
		finally:
			cur.close()
	
	def list_prompt(self, prompt_id: int, price: int):
		cur = self.get_cursor()
		try:
			cur.execute('UPDATE Prompts SET isListed = 1, price = ? WHERE id = ?', (from_int_to_hex_str(prompt_id), from_int_to_hex_str(price)))
			self.con.commit()
			return True
		finally:
			cur.close()

	def list_image(self, image_id: int, price: int):
		cur = self.get_cursor()
		try:
			cur.execute('UPDATE Images SET isListed = 1, price = ? WHERE id = ?', (from_int_to_hex_str(image_id), from_int_to_hex_str(price)))
			self.con.commit()
			return True
		finally:
			cur.close()


	def unlist_prompt(self, prompt_id: int):
		cur = self.get_cursor()
		try:
			cur.execute('UPDATE Prompts SET isListed = 0 WHERE id = ?', (from_int_to_hex_str(prompt_id),))
			self.con.commit()
			return True
		finally:
			cur.close()

	def unlist_image(self, image_id: int):
		cur = self.get_cursor()
		try:
			cur.execute('UPDATE Images SET isListed = 0 WHERE id = ?', (from_int_to_hex_str(image_id),))
			self.con.commit()
			return True
		finally:
			cur.close()

	def unlist_packet(self, packet_id: int):
		cur = self.get_cursor()
		try:
			cur = cur.execute('UPDATE Packets SET isListed = 0 WHERE id = ?', (from_int_to_hex_str(packet_id),))
			self.con.commit()
			return True
		finally:
			cur.close()
	
	def remove_packet_from(self, packet_id: int, user_id: str):
		cur = self.get_cursor()
		try:
			cur.execute('DELETE FROM Packets WHERE id=? and userHex=?', (from_int_to_hex_str(packet_id), user_id))
			self.con.commit()
			return True
		finally:
			cur.close()

	def freeze_prompt(self, prompt_id: int):
		cur = self.get_cursor()
		try:
			print("FREEZING PROMPT: ", prompt_id, "...")
			cur.execute('UPDATE Prompts SET isFreezed=1, isListed=0 WHERE id=?', (from_int_to_hex_str(prompt_id),))
			self.con.commit()
			return True
		finally:
			cur.close()
	def unfreeze_prompt(self, prompt_id: int):
		cur = self.get_cursor()
		try:
			cur.execute('UPDATE Prompts SET isFreezed=0 WHERE id=?', (from_int_to_hex_str(prompt_id),))
			self.con.commit()
			return True
		finally:
			cur.close()

	def remove_image_from(self, image_id: int, user_id: str):
		img = self.get_image(image_id)
		img.unfreezePrompts(self)
		cur = self.get_cursor()
		try:
			cur.execute('DELETE FROM Images WHERE id=? and userHex=?', (from_int_to_hex_str(image_id.id), user_id))
			self.con.commit()
			return True
		finally:
			cur.close()

	
	def addTransferEvent(self, objId: int, from_user_id: str, to_user_id: str, objType):
		obj = None
		if objType == 0:
			obj = self.get_packet(objId)
		elif objType == 1:
			obj = self.get_prompt(objId)
		elif objType == 2:
			obj = self.get_image(objId)
		if(obj is None):
			print("[addTransferEvent] INVALID OBJ TYPE!!!")
			return
		
		cur = self.get_cursor()
		try:
			cur.execute('INSERT INTO SellEvents(objId, userFromHex, userToHex, price, type) values (?, ?, ?, ?, ?)', (from_int_to_hex_str(objId), from_user_id, to_user_id, obj.price, objType))
			self.con.commit()
			return True
		finally:
			cur.close()

	def getPacketTransferEvent(self, objId: int):
		cur = self.get_cursor()
		try:
			cur.execute('SELECT userFromHex, userToHex, price FROM SellEvents WHERE objId=? and type=?', (objId, 0))
			res = cur.fetchone()
			if res is not None:
				return {"from": from_str_hex_to_int_str(res[0]), "to": from_str_hex_to_int_str(res[1]), "price": res[2]}
		finally:
			cur.close()
	def getPromptTransferEvent(self, objId: int):
		cur = self.get_cursor()
		try:
			cur.execute('SELECT userFromHex, userToHex, price FROM SellEvents WHERE objId=? and type=?', (from_int_to_hex_str(objId), 1))
			res = cur.fetchone()
			if res is not None:
				return {"from": from_str_hex_to_int_str(res[0]), "to": from_str_hex_to_int_str(res[1]), "price": res[2]}
		finally:
			cur.close()
	def getImageTransferEvent(self, objId: int):
		cur = self.get_cursor()
		try:
			cur.execute('SELECT userFromHex, userToHex, price FROM SellEvents WHERE objId=? and type=?', (from_int_to_hex_str(objId), 2))
			res = cur.fetchone()
			if res is not None:
				return {"from": from_str_hex_to_int_str(res[0]), "to": from_str_hex_to_int_str(res[1]), "price": res[2]}
		finally:
			cur.close()

	def transfer_packet(self, packet_id: int, from_user_id: int, to_user_id: int):
		cur = self.get_cursor()
		try:
			cur.execute('UPDATE Packets SET userHex = ?, isListed = 0 WHERE id = ?', (to_user_id, from_int_to_hex_str(packet_id)))
			self.con.commit()
			self.addTransferEvent(packet_id, from_user_id, to_user_id, 0)
			return True
		finally:
			cur.close()

	def transfer_prompt(self, prompt_id: int, from_user_id: int, to_user_id: int):
		cur = self.get_cursor()
		try:
			cur.execute('UPDATE Prompts SET userHex = ?, isListed = 0 WHERE id = ?', (to_user_id, from_int_to_hex_str(prompt_id)))
			self.con.commit()
			self.addTransferEvent(prompt_id, from_user_id, to_user_id, 1)
			return True
		finally:
			cur.close()

	def transfer_image(self, image_id: int, from_user_id: int, to_user_id: int):
		cur = self.get_cursor()
		try:
			cur.execute('UPDATE Images SET userHex = ?, isListed = 0 WHERE id = ?', (to_user_id, from_int_to_hex_str(image_id)))
			self.con.commit()
			self.addTransferEvent(image_id, from_user_id, to_user_id, 2)
			return True
		finally:
			cur.close()
		
	def fromJson(self, data):
		obj = json.loads(data)
		for k, v in obj:
			if(k.startswith("user_to_")):
				self.__dict__[k] = v
			else:
				o = {}
				for k1, v1 in v:
					obj = None
					if("packet" in k):
						obj = Packet()
					elif("prompt" in k):
						obj = Prompt()
					elif("image" in k):
						obj = Image()
					if(obj != None):
						obj.__dict__ = v1
						o[k1] = obj
				self.__dict__[k] = o
	def toJson(self):
		data = {k: (v if k.startswith("user_to_") else {k1: v1.__dict__ for k1, v1 in v}) for k, v in self.__dict__}
		return json.dumps(data, sort_keys=True)