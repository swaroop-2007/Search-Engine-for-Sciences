import datetime
import csv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo import MongoClient

uri = "mongodb+srv://ir-project:YM9p8dKEZehONP54@cluster0.rslnzkm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))


# Field from mongodb
field_names = ['url', 'title', 'text', 'imageURL', 'source']

def connect_read_data():
    try:
        client.admin.command('ping')
        db = client.science_search_engine
        collection = db.sample_webpages

        documents = collection.find({})
        csv_file = "sample_webpage.csv"

        with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=field_names)
        
            # Write header
            writer.writeheader()
        
            # Write each document
            for document in documents:
                writer.writerow({"title": document.get("title", ""),
                                "url": document.get("url", ""),
                                "text": document.get("text", ""), 
                                "imageURL": document.get("imageURL", ""),
                                "source": document.get("source", "")})

        print("Documents exported to CSV successfully.")
        print("Pinged your deployment. You successfully connected to MongoDB!")

    except Exception as e:
        print(e) 


connect_read_data()


