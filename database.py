from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")

db = client["StudySphereDB"]

collections = db["users"]

print("MongoDB Connected Successfully!")