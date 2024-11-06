from bson.json_util import dumps
from bson.timestamp import Timestamp
from bson.objectid import ObjectId
import pymongo
import json
import os

context = json.loads(os.environ["EXECUTORTASK"].strip())

connstringarg = next(obj for obj in context["arguments"] if obj["key"] == "connectionstring")
connstring = connstringarg["value"]

lastOutput = json.loads(os.environ["EXECUTORLASTOUTPUT"].strip())
lo = json.loads(lastOutput["response"])

client = pymongo.MongoClient(connstring.strip())
db = client["executorscratch"]
id = db["scratch"].insert_one(lo)

print(json.dumps({"id": str(id.inserted_id)}))
