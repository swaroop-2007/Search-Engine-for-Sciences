from pymongo import MongoClient
import csv

# MongoDB connection URI
uri = "mongodb+srv://ir-project:YM9p8dKEZehONP54@cluster0.rslnzkm.mongodb.net/science_search_engine"

# Connect to MongoDB
client = MongoClient(uri)

# Access the database
db = client.science_search_engine

# Access the collection
collection = db.docs_v1


field_names = ['url', 'title', 'text', 'imageURL', 'source']

documents = collection.find({})
csv_file = "docs_v1.csv"

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

    
# Now you can perform operations on the collection, such as finding documents
documents = collection.find({})
i = 0
# Iterate over the documents
for document in documents:
    print(document, "\n")
    i += 1
    if  i ==5 :
        break