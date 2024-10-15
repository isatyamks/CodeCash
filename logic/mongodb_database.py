from pymongo import MongoClient
from datetime import datetime,timedelta
client = MongoClient('mongodb://localhost:27017')  


#client database

db = client.login
users_collection = db.users

#bank data mongodb datasets
db_codecash = client.bank
bank_collection = db_codecash['assets']
bank_assets_record = bank_collection.find_one({'_id': 'bank_assets'})


bank_assets = int(bank_assets_record.get('total_assets')) if bank_assets else 0