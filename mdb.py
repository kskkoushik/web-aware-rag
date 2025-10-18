import os
from pymongo.mongo_client import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from datetime import datetime
from dotenv import load_dotenv
from pymongo.server_api import ServerApi


load_dotenv()


MONGODB_URI = os.getenv("MONGODB_URI")

    
client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))

db = client['Aira_db']

collection = db['data_status']
    
def insert_data( url , status):

      document = {
            "url": url,
            "status": status,
            "inserted_at": datetime.now()
        }
      
      try :
        result = collection.update_one(
                {"url": url},
                {
                    "$set": {
                        "status": status,
                        "updated_at": datetime.now()
                    },
                    "$setOnInsert": {
                        "inserted_at": datetime.now()
                    }
                },
                upsert=True
            )
      except Exception as e :
          print(f'Error inserting data into MongoDB : {e}')


def get_all_data():


    try :

        documents = list(collection.find({}, {"_id": 0}))  # Exclude _id

        return documents
    except Exception as e :

        print(f"Error fetching data from MongoDB : {e}")

        return []