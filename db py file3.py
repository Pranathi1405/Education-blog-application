import pymongo
password = "Butterfly@1211"
client = pymongo.MongoClient(f"mongodb+srv://girivarkala1:Butterfly1211@cluster0.ca6tkne.mongodb.net/?retryWrites=true&w=majority")
database = client.EducationDB

users = database.user
user_data = database.userdata

