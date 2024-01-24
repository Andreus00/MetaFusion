from typing import Dict, List, Tuple
import sqlite3
import base58
import json
import os
from ..utils.utils import *
from .database import CreateDatabase, DatabaseConnection

class Packet:

	def __init__(self):
		self.id: int = 0
		self.isListed: bool = False
		self.price: int = 0
		self.userIdHex: str = ''

	def initWithDb(self, res):
		self.id = from_str_hex_to_int(res[0])
		self.isListed = res[1]
		self.price = from_str_hex_to_int(res[2])
		self.userIdHex = res[3].lower()
		return self
	def initWithParams(self, id, userIdHex: str, isListed: bool = False, price: int = 0, data=None):
		self.id: int = id
		self.isListed: bool = isListed
		self.price: int = price 
		self.userIdHex = userIdHex.lower()
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

	def __init__(self):
		self.id: int = 0
		self.hash: str = ''
		self.isListed: bool = False
		self.price: int = 0
		self.userIdHex: str = ''
		self.isFreezed = 0
		self.name = ''
		self.rarity = 0
	
	def initWithDb(self, res):
		self.id = res[0]
		self.hash = res[1]
		self.isListed = res[2]
		self.price = from_str_hex_to_int(res[3])
		self.isFreezed = res[4]
		self.userIdHex = res[5].lower()
		self.name = res[6]
		self.rarity = res[7]
		return self
	def initWithParams(self, id: int, userIdHex: str, hash: str = None, name: str = None, rarity: int = None, isListed: bool = False, price: int = 0, isFreezed: bool = False, data=None):
		self.id: int = id
		self.hash: str = hash   # IPFS hash
		self.isListed: bool = isListed
		self.price: int = price
		self.isFreezed: bool = isFreezed	
		self.userIdHex: str = userIdHex.lower()
		self.name: str = name
		self.rarity: int = rarity
		if data is not None:
			self.writeToDb(data)

	def writeToDb(self, data):
		cur = data.get_cursor()
		cur.execute('INSERT OR REPLACE INTO Prompts(id, ipfsHash, isListed, price, isFreezed, userHex, name, collectionId, type, rarity) VALUES (?, ?, ?, ?, ? , ?, ?, ?, ?, ?)', (from_int_to_hex_str(self.id), self.hash, self.isListed, from_int_to_hex_str(self.price), self.isFreezed, self.userIdHex, self.name, self.getOriginalCollection(), self.getType(), self.rarity))
		data.con.commit()
		cur.close()

	def addIPFSHash(self, id, promptCid, name, rarity, data):
		cur = data.get_cursor()
		cur.execute('UPDATE Prompts SET ipfsHash=?, name=?, rarity=? WHERE id=?', (promptCid, name, rarity, from_int_to_hex_str(id)))
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

	def __init__(self):
		self.id: int = 0
		self.hash: str = ''
		self.isListed: bool = False
		self.price: int = 0
		self.userIdHex: str = ''

	def initWithDb(self, res):
		self.id = res[0]
		self.hash = res[1]
		self.isListed = res[2]
		self.price = from_str_hex_to_int(res[3])
		self.userIdHex = res[4].lower()
		return self
	
	def initWithParams(self, id: int, userIdHex: str, hash: str = None, isListed: bool = False, price: int = 0, data=None):
		self.id: int = id
		self.hash: str = hash   # IPFS hash
		self.isListed: bool = isListed
		self.price: int = price
		self.userIdHex: str = userIdHex.lower()
		if data is not None:
			self.writeToDb(data)

	def freezePrompts(self, data):
		_, prompts = getInfoFromImageId(self.id)
		for prompt in prompts:
			if prompt != 0:
				data.freeze_prompt(prompt_id=prompt)
				
	def unfreezePrompts(self, data):
		if isinstance(self.id, str):
			self.id = from_str_hex_to_int(self.id)
		_, prompts = getInfoFromImageId(self.id)
		for prompt in prompts:
			if prompt != 0:
				data.unfreeze_prompt(prompt_id=prompt)
		
	def writeToDb(self, data):
		cur = data.get_cursor()
		cur.execute('INSERT OR REPLACE INTO Images(id, ipfsHash, isListed, price, userHex, collectionId) VALUES (?, ?, ?, ?, ?, ?)', (from_int_to_hex_str(self.id), self.hash, self.isListed, from_int_to_hex_str(self.price), self.userIdHex, self.getOriginalCollection()))
		data.con.commit()
		cur.close()
	
	def addIPFSHash(self, id, imageCid, data):
		cur = data.get_cursor()
		cur.execute('UPDATE Images SET ipfsHash=? WHERE id=?', (imageCid, from_int_to_hex_str(id)))
		data.con.commit()
		cur.close()

	def deleteFromDb(self, data):
		cur = data.get_cursor()
		cur.execute('DELETE FROM Images WHERE id=?', (from_int_to_hex_str(self.id),))
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


	def get_packets_id_of(self, userIdHex: str, tiny=False):
		cur = self.get_cursor()
		try:
			result = []
			cur.execute('SELECT id, isListed, price, collectionId FROM Packets WHERE userHex=?', (userIdHex,))
			query_result = cur.fetchall()
			for row in query_result:
				result.append({
					"id": row[0], 
					"isListed": row[1], 
					"price": from_str_hex_to_int(row[2]), 
					"collectionId": row[3],
					"nft_type": 0})
			return result
		finally:
			cur.close()
	
	def get_prompts_id_of(self, userIdHex: str, tiny=False):
		cur = self.get_cursor()
		try:
			result = []
			cur.execute('SELECT id, isListed, price, isFreezed, name, type, collectionId, rarity FROM Prompts WHERE userHex=?', (userIdHex,))
			query_result = cur.fetchall()
			for row in query_result:
				result.append({
					"id": row[0], 
					"isListed": row[1], 
					"price": from_str_hex_to_int(row[2]), 
					"isFreezed": row[3], 
					"name": row[4], 
					"category": row[5], 
					"collectionId": row[6], 
					"rarity": row[7], 
					"nft_type": 1})
			return result
		finally:
			cur.close()
	
	def get_images_id_of(self, userIdHex: str, tiny=False):
		cur = self.get_cursor()
		try:
			result = []
			cur.execute('SELECT id, isListed, price, collectionId FROM Images WHERE userHex=?', (userIdHex,))
			query_result = cur.fetchall()
			for row in query_result:
				result.append({
					"id": row[0], 
					"isListed": row[1], 
					"price": from_str_hex_to_int(row[2]), 
					"collectionId": row[3],
					"nft_type": 2})
			return result
		finally:
			cur.close()
		

	def get_packet(self, packet_id, as_json=False):
		if isinstance(packet_id, int):
			packet_id = from_int_to_hex_str(packet_id)
		cur = self.get_cursor()
		try:
			cur.execute('SELECT * FROM Packets WHERE id=?', (packet_id,))
			res = cur.fetchone()
			if res is not None:
				if as_json:
					return {
						"id": res[0],
						"isListed": res[1],
						"price": from_str_hex_to_int(res[2]),
						"owner": res[3],
						"collectionId": res[4],
						"nft_type": 0
					}
				return Packet().initWithDb(res)
		finally:
			cur.close()
	
	def get_prompt(self, prompt_id, as_json=False):
		if isinstance(prompt_id, int):
			prompt_id = from_int_to_hex_str(prompt_id)
		if prompt_id == "0x0":
			return None
		cur = self.get_cursor()
		try:
			cur.execute('SELECT * FROM Prompts WHERE id=?', (prompt_id,))
			res = cur.fetchone()
			if res is not None:
				if as_json:
					return {
						"id": res[0],
						"ipfsCid": res[1],
						"isListed": res[2],
						"price": from_str_hex_to_int(res[3]),
						"isFreezed": res[4],
						"owner": res[5],
						"name": res[6],
						"category": res[7],
						"collectionId": res[8],
						"rarity": res[9],
						"nft_type": 1
					}
				return Prompt().initWithDb(res)
		finally:
			cur.close()
	
	def get_image(self, image_id: str, as_json=False):
		if isinstance(image_id, int):
			image_id = from_int_to_hex_str(image_id)
		cur = self.get_cursor()
		try:
			cur.execute('SELECT * FROM Images WHERE id=?', (image_id,))
			res = cur.fetchone()
			if res is not None:
				# get prompts that are in this image
				_, prompts = getInfoFromImageId(from_str_hex_to_int(image_id))

				if as_json:
					return {
						"id": res[0],
						"ipfsCid": res[1],
						"isListed": res[2],
						"price": from_str_hex_to_int(res[3]),
						"owner": res[4],
						"collectionId": res[5],
						"prompts": sorted([
							self.get_prompt(from_int_to_hex_str(prompt), as_json=True) for prompt in prompts if prompt != 0
						], key=lambda x: x["category"]),
						"nft_type": 2
					}
				return Image().initWithDb(res)
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
			cur.execute('SELECT isListed FROM Images WHERE id=?', (from_int_to_hex_str(image_id),))
			# cur.execute('SELECT isListed FROM Images WHERE id=? LIMIT 1', (from_int_to_hex_str(packet_id),))
			res = cur.fetchone()
			if res is not None:
				return int(res[0])
			return False
		finally:
			cur.close()
	

	def get_all_packets(self, only_listed=True):
		cur = self.get_cursor()
		try:
			cur.execute('SELECT id, isListed, price, collectionId FROM Packets WHERE isListed=1')
			result = cur.fetchall()
			response = []
			if result is not None:
				for row in result:
					response.append({
						"id": row[0], 
						"isListed": row[1], 
						"price": from_str_hex_to_int(row[2]), 
						"collectionId": row[3],
						"nft_type": 0
					})
			return response
		finally:
			cur.close()
	
	def get_all_prompts(self, only_listed=True):
		cur = self.get_cursor()
		try:
			cur.execute('SELECT id, isListed, price, isFreezed, name, type, collectionId, rarity FROM Prompts WHERE isListed=1')
			res = cur.fetchall()
			ret = []
			if res is not None:
				for row in res:
					ret.append({
						"id": row[0],
						"isListed": row[1],
						"price": from_str_hex_to_int(row[2]),
						"isFreezed": row[3],
						"name": row[4],
						"category": row[5],
						"collectionId": row[6],
						"rarity": row[7],
						"nft_type": 1
					})
			return ret
		finally:
			cur.close()

	
	def get_all_images(self, only_listed=True):
		cur = self.get_cursor()
		try:
			cur.execute('SELECT id, isListed, price, collectionId FROM Images WHERE isListed=1')
			res = cur.fetchall()
			ret = []
			if res is not None:
				for row in res:
					ret.append({
						"id": row[0],
						"isListed": row[1],
						"price": from_str_hex_to_int(row[2]),
						"collectionId": row[3],
						"nft_type": 2
					})
			return ret
		finally:
			cur.close()
	

	def list_packet(self, packet_id: int, price: int, token_owner: str):
		cur = self.get_cursor()
		try:
			cur.execute('UPDATE Packets SET isListed = 1, price = ? WHERE id = ? AND userHex = ?', 
				(from_int_to_hex_str(price), from_int_to_hex_str(packet_id), token_owner))
			self.con.commit()
			return True
		finally:
			cur.close()
	
	def list_prompt(self, prompt_id: int, price: int, token_owner: str):
		cur = self.get_cursor()
		try:
			cur.execute('UPDATE Prompts SET isListed = 1, price = ? WHERE id = ? AND userHex = ?', 
			   (from_int_to_hex_str(price), from_int_to_hex_str(prompt_id), token_owner))
			self.con.commit()
			return True
		finally:
			cur.close()

	def list_image(self, image_id: int, price: int, token_owner: str):
		cur = self.get_cursor()
		try:
			cur.execute('UPDATE Images SET isListed = 1, price = ? WHERE id = ? AND userHex = ?', 
			   (from_int_to_hex_str(price), from_int_to_hex_str(image_id), token_owner))
			self.con.commit()
			return True
		finally:
			cur.close()


	def unlist_prompt(self, prompt_id: int, token_owner: str):
		cur = self.get_cursor()
		try:
			cur.execute('UPDATE Prompts SET isListed = 0 WHERE id = ? AND userHex = ?', (from_int_to_hex_str(prompt_id), token_owner))
			self.con.commit()
			return True
		finally:
			cur.close()

	def unlist_image(self, image_id: int, token_owner: str):
		cur = self.get_cursor()
		try:
			cur.execute('UPDATE Images SET isListed = 0 WHERE id = ? AND userHex = ?', (from_int_to_hex_str(image_id), token_owner))
			self.con.commit()
			return True
		finally:
			cur.close()

	def unlist_packet(self, packet_id: int, token_owner: str):
		cur = self.get_cursor()
		try:
			cur = cur.execute('UPDATE Packets SET isListed = 0 WHERE id = ? AND userHex = ?', (from_int_to_hex_str(packet_id), token_owner))
			self.con.commit()
			return True
		finally:
			cur.close()
	
	def remove_packet_from(self, packet_id: int, user_id: str):
		cur = self.get_cursor()
		try:
			cur.execute('DELETE FROM Packets WHERE id=?', (from_int_to_hex_str(packet_id),))
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
			obj = self.get_packet(from_int_to_hex_str(objId))
		elif objType == 1:
			obj = self.get_prompt(from_int_to_hex_str(objId))
		elif objType == 2:
			obj = self.get_image(from_int_to_hex_str(objId))
		if(obj is None):
			print("[addTransferEvent] INVALID OBJ TYPE!!!")
			return
		
		cur = self.get_cursor()
		try:
			cur.execute('INSERT INTO SellEvents(objId, userFromHex, userToHex, price, type) values (?, ?, ?, ?, ?)', (from_int_to_hex_str(objId), from_user_id, to_user_id,from_int_to_hex_str(obj.price), objType))
			self.con.commit()
			return True
		finally:
			cur.close()

	def get_token_transfer_events(self, objId: str):
		cur = self.get_cursor()
		try:
			cur.execute('SELECT objId, userFromHex, userToHex, price, type FROM SellEvents WHERE objId=? ORDER BY id', (objId,))
			result = cur.fetchall()
			if result is not None:
				response = []
				for row in result:
					response.append({
						"id": row[0], 
					  	"seller": row[1], 
						"buyer": row[2], 
						"price": from_str_hex_to_int(row[3]), 
						"type": row[4]})
				return response
		finally:
			cur.close()

	def get_user_transfer_events(self, user_id: str):
		cur = self.get_cursor()
		try:
			cur.execute('SELECT objId, userFromHex, userToHex, price, type FROM SellEvents WHERE userFromHex=? or userToHex=? ORDER BY id', (user_id, user_id))
			result = cur.fetchall()
			if result is not None:
				response = []
				for row in result:
					response.append({
						"id": row[0], 
						"seller": row[1], 
						"buyer": row[2], 
						"price": from_str_hex_to_int(row[3]), 
						"type": row[4]
						})
				return response
		finally:
			cur.close()

	def transfer_packet(self, packet_id: int, from_user_id: str, to_user_id: str):
		cur = self.get_cursor()
		try:
			cur.execute('UPDATE Packets SET userHex = ?, isListed = 0 WHERE id = ?', (to_user_id.lower(), from_int_to_hex_str(packet_id)))
			self.con.commit()
			self.addTransferEvent(packet_id, from_user_id.lower(), to_user_id.lower(), 0)
			return True
		finally:
			cur.close()

	def transfer_prompt(self, prompt_id: int, from_user_id: str, to_user_id: str):
		cur = self.get_cursor()
		try:
			cur.execute('UPDATE Prompts SET userHex = ?, isListed = 0 WHERE id = ?', (to_user_id.lower(), from_int_to_hex_str(prompt_id)))
			self.con.commit()
			self.addTransferEvent(prompt_id, from_user_id.lower(), to_user_id.lower(), 1)
			return True
		finally:
			cur.close()

	def transfer_image(self, image_id: int, from_user_id: str, to_user_id: str):
		cur = self.get_cursor()
		try:
			cur.execute('UPDATE Images SET userHex = ?, isListed = 0 WHERE id = ?', (to_user_id.lower(), from_int_to_hex_str(image_id)))
			self.con.commit()
			self.addTransferEvent(image_id, from_user_id.lower(), to_user_id.lower(), 2)
			return True
		finally:
			cur.close()

	def get_user(self, user_id: str):
		user_packets = self.get_packets_id_of(user_id, tiny=True)
		user_prompts = self.get_prompts_id_of(user_id, tiny=True)
		user_images = self.get_images_id_of(user_id, tiny=True)
		user_transactions = self.get_user_transfer_events(user_id)
		return user_packets, user_prompts, user_images, user_transactions
	
	def get_username(self, user_id: str):
		cur = self.get_cursor()
		try:
			cur.execute('SELECT username FROM User WHERE userId=?', (user_id.lower(),))
			result = cur.fetchone()
			if result is not None:
				return result[0]
			return None
		finally:
			cur.close()

	def set_username(self, user_id: str, username: str):
		cur = self.get_cursor()
		try:
			cur.execute('INSERT OR REPLACE INTO User(userId, username) values (?, ?)', (user_id.lower(), username))
			self.con.commit()
			return True
		finally:
			cur.close()

	def get_remainig_number_of_packets(self, collectionId: int):
		cur = self.get_cursor()
		TOT_PACKETS = 750
		try:
			cur.execute('SELECT COUNT(ID) as c FROM Packets WHERE collectionId=?', (collectionId,))
			packets_to_open = cur.fetchone()[0]
			
			cur.execute('SELECT COUNT(ID) as c FROM Prompts WHERE collectionId=?', (collectionId,))
			prompts_generated = cur.fetchone()[0]
			packets_opened = prompts_generated // 8

			return TOT_PACKETS - (packets_to_open + packets_opened)
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