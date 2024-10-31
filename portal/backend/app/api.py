from fastapi import FastAPI, Response
import pymongo
import datetime
from bson.json_util import dumps
from bson.timestamp import Timestamp
from bson.objectid import ObjectId
from fastapi.staticfiles import StaticFiles
import json
import os
import requests
from typing import Dict, Any
from fastapi.middleware.cors import CORSMiddleware

api_app = FastAPI(title="api-app")
app = FastAPI(title="spa-app")
app.mount("/api", api_app)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

client = pymongo.MongoClient(os.environ["MDBCONNSTR"].strip())
db = client["excutor"]

@api_app.get("/crud/listAllTemplate")
async def listAllTemplates():
    cursor = db["templates"].find({}).sort("_id", pymongo.DESCENDING)
    return json.loads(dumps(cursor))

@api_app.get("/crud/listAllWorkflows")
async def listAllTemplates():
    cursor = db["workflows"].find({}).sort("_id", pymongo.DESCENDING)
    return json.loads(dumps(cursor))

@api_app.post("/crud/newTemplate")
async def newTemplate(d: Dict[Any, Any]):
    print(d)
    db["templates"].insert_one(d)

@api_app.get("/crud/newWorkflow")
async def new():
    obj = {"name":"New Subscription", "wf":[] }
    id = db["workflows"].insert_one(obj).inserted_id
    obj["_id"] = id
    return json.loads(dumps(obj))

@api_app.get("/crud/getWorkflow/{id}")
async def getWorkflowById(id:str):
    d = db["workflows"].find_one({"_id": ObjectId(id) })
    return json.loads(dumps(d))

@api_app.put("/crud/saveWorkflow/{id}")
async def saveWorkflow(id:str, d: Dict[Any,Any]):
    d.pop("_id")
    db["workflows"].update_one({"_id": ObjectId(id) }, {"$set": d })

@api_app.get("/hello")
async def hello():
    return {"message": "Hello World"}
