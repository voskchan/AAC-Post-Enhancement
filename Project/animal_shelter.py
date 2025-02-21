from pymongo import MongoClient
from pymongo.server_api import ServerApi


class AnimalShelter(object):
    """ CRUD operations for Animal collection in MongoDB """

    def __init__(self, user, password):
        # Initializing the MongoClient. This helps to 
        # access the MongoDB databases and collections.
        # This is hard-wired to use the aac database, the 
        # animals collection, and the aac user.
        # Definitions of the connection string variables are
        # unique to the individual Apporto environment.
        #
        # You must edit the connection variables below to reflect
        # your own instance of MongoDB!
        #
        # Connection Variables
        #
        USER = user
        PASS = password
        HOST = 'nv-desktop-services.apporto.com'
        PORT = 32041
        DB = 'AAC'
        COL = 'animals'

        uri = "mongodb+srv://"+user+":"+password+"@aacshelter.odcc0.mongodb.net/?retryWrites=true&w=majority&appName=AACShelter"
        #
        # Initialize Connection
        #
        self.client = MongoClient(uri, server_api=ServerApi('1'))
        self.database = self.client['%s' % (DB)]
        self.collection = self.database['%s' % (COL)]

# Complete this create method to implement the C in CRUD.
    def create(self, data):
        if data is not None:
            self.database.animals.insert_one(data)  # data should be dictionary
            return True
        else:
            raise Exception("Nothing to save, because data parameter is empty")
            return False

# Create method to implement the R in CRUD.
    def read(self, criteria):
        if criteria is not None:
            result = list(self.database.animals.find(criteria))
            return result
        else:
            raise Exception('No criteria given for search')
            result = list()
            return result
#Implements a delete function to fufill D in CRUD
    def delete(self, searchKey):
        if searchKey is not None:
            result = self.database.animals.delete_many(searchKey)
        else:
            return "{}"
        return result.raw_result
    
   

    def update(self, searchKey, updateData):
        if searchKey and updateData is not None:
            result = self.database.animals.update_many(searchKey, { "$set" : updateData})
        else:
            return "{}"
        return result.raw_result
    
        
        
            

        