from fastapi import FastAPI, Response, File, UploadFile, Form
import pymongo
from datetime import datetime
from datetime import timezone
from bson.json_util import dumps
from bson.timestamp import Timestamp
from bson.objectid import ObjectId
from fastapi.staticfiles import StaticFiles
import json
import os
import requests
from typing import Dict, Any
from fastapi.middleware.cors import CORSMiddleware
import gridfs
from fastapi.responses import StreamingResponse

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
async def newTemplate(file: UploadFile = File(), template: str = Form()):
    print(template)
    tobj = json.loads(template)
    contents = file.file.read()
    pointer = gridfs.GridFS(db).put(contents, filename=tobj["title"])
    tobj["gridfspointer"] = pointer
    db["templates"].insert_one(tobj)

@api_app.put("/crud/saveTemplate/{id}")
async def saveTemplate(id:str, file: UploadFile = File(), template: str = Form()):
    d = json.loads(template)
    d.pop("_id")
    db["templates"].update_one({"_id": ObjectId(id) }, {"$set": d })
    if file:
        contents = file.file.read()
        pointer = gridfs.GridFS(db).put(contents, filename=d["title"])
        db["templates"].update_one({"_id": ObjectId(id) }, {"$set": {"gridfspointer": pointer} })

@api_app.get("/crud/newWorkflow")
async def new():
    obj = {"name":"New Workflow", "wf":[] }
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

@api_app.post("/exec/enqueueWorkflow/{id}")
async def newTemplate(id:str, d: Dict[Any, Any]):
    newObj ={}
    newObj["payload"] = d
    newObj["workflowId"] = id
    newObj["status"] = "queued"
    newObj["created"] = datetime.now(timezone.utc)
    newObj["modified"] = datetime.now(timezone.utc)
    w = db["workflows"].find_one({"_id": ObjectId(id) })
    newObj["workflow"] = w
    db["executions"].insert_one(newObj)

@api_app.post("/exec/getNextExecution")
async def getNextExecution(server: Dict[Any, Any]):
    wf = db["executions"].find_one({"status": "queued" })
    print(wf)
    db["executions"].update_one({"_id": wf["_id"] }, {"$set": {"status": "allocated", "ownedBy":server["name"]} })
    return json.loads(dumps(wf))

@api_app.post("/exec/executionOutput")
async def executionOutput(q: Dict[Any, Any]):
    query = {"_id": ObjectId(q["workflowId"]["$oid"])}
    update = {"$set": {"workflow.wf."+str(q["index"])+".status": "complete", "workflow.wf."+str(q["index"])+".result": q["result"]}}
    print(update)
    db["executions"].update_one(query, update)

@api_app.get("/exec/downloadZip/{pointerid}")
async def downloadZip(pointerid: str):
    fs = gridfs.GridFS(db)
    file = fs.get(ObjectId(pointerid))
    return StreamingResponse(file, media_type="application/zip")

@api_app.get("/crud/listAllExecutions")
async def listAllExecutions():
    cursor = db["executions"].find({}).sort("_id", pymongo.DESCENDING)
    return json.loads(dumps(cursor))

@api_app.get("/crud/listExecutionSteps/{id}")
async def listExecutionSteps(id:str):
    d = db["executions"].find_one({"_id": ObjectId(id) })
    return json.loads(dumps(d))

@api_app.post("/exec/completeExecution/{id}")
async def completeExecution(id:str):
    db["executions"].update_one({"_id": ObjectId(id) }, {"$set": {"status": "complete"} })

@api_app.get("/hello")
async def hello():
    return {"message": "Hello World"}
