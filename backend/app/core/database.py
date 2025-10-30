from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get MongoDB URI from environment variables
MONGO_URI = os.getenv("MONGO_URI")

# Connect to MongoDB client
client = MongoClient(MONGO_URI)
db = client.get_database()

# Check MongoDB connection
try:
    client.admin.command('ping')
    print("MongoDB connection is successful!")
except ConnectionFailure:
    print("MongoDB connection failed!")

# Example: Access the 'claims' collection
claims_collection = db["claims"]
