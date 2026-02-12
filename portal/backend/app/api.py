from fastapi import FastAPI, Response, File, UploadFile, Form
import pymongo
from datetime import datetime, timedelta
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

# check if SPECUIMDBCONNSTR is set, if so override MDBCONNSTR
connstr = None
if "SPECUIMDBCONNSTR" in os.environ:
    connstr = os.environ["SPECUIMDBCONNSTR"].strip()
else:
    connstr = os.environ["MDBCONNSTR"].strip()

client = pymongo.MongoClient(connstr)
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
async def saveTemplate(id:str, file: UploadFile = None, template: str = Form()):
    d = json.loads(template)
    d.pop("_id")
    db["templates"].update_one({"_id": ObjectId(id) }, {"$set": d })
    if file != None:
        contents = file.file.read()
        pointer = gridfs.GridFS(db).put(contents, filename=d["title"])
        db["templates"].update_one({"_id": ObjectId(id) }, {"$set": {"gridfspointer": pointer} })

@api_app.get("/crud/getTemplate/{id}")
async def getTemplate(id:str):
    d = db["templates"].find_one({"_id": ObjectId(id) })
    return json.loads(dumps(d))

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
async def enqueueWorkflow(id:str, d: Dict[Any, Any]):
    newObj ={}
    newObj["payload"] = d
    newObj["workflowId"] = id
    newObj["status"] = "queued"
    newObj["created"] = datetime.now(timezone.utc)
    newObj["modified"] = datetime.now(timezone.utc)
    w = db["workflows"].find_one({"_id": ObjectId(id) })
    newObj["workflow"] = w
    d = db["executions"].insert_one(newObj)
    return {"executionId": str(d.inserted_id) }

@api_app.post("/exec/getNextExecution")
async def getNextExecution(server: Dict[Any, Any]):
    me = db["servers"].find_one({"_id": server["name"]})
    waitUntil = 10
    if me:
        waitUntil = me["nextPoll"]
        db["servers"].update_one({"_id": server["name"]}, {"$set": {"lastSeen": datetime.now(timezone.utc)}})
    else:
        # set to a random number to avoid thundering herd
        primes = [7, 11, 13, 17, 19, 23, 29, 31]
        waitUntil = primes[hash(server["name"]) % len(primes)]
        db["servers"].insert_one({"_id": server["name"], "nextPoll":waitUntil, "lastSeen": datetime.now(timezone.utc), "firstSeen": datetime.now(timezone.utc)})
    wf = db["executions"].find_one({"status": "queued" })
    #print(wf)
    if wf:
        db["executions"].update_one({"_id": wf["_id"] }, {"$set": {"status": "allocated", "ownedBy":server["name"]} })
        wf["nextPoll"] = int(waitUntil)
        return json.loads(dumps(wf))
    else:
        return {"workflow":{"wf":[]}, "nextPoll": int(waitUntil)}

@api_app.get("/exec/servers")
async def listServers():
    cursor = db["servers"].find({}).sort("lastSeen", pymongo.DESCENDING)
    return json.loads(dumps(cursor))

@api_app.put("/exec/updateServer")
async def updateServer(server: Dict[Any, Any]):
    db["servers"].update_one({"_id": server["name"]}, {"$set": {"nextPoll":server["nextPoll"]}})

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
    two_days_ago = datetime.now(timezone.utc) - timedelta(days=2)
    cursor = db["executions"].find(
        {"created": {"$gte": two_days_ago}},
        {"_id": 1, "workflow._id": 1, "workflow.name": 1, "created": 1, "status":1}
    ).sort("_id", pymongo.DESCENDING)
    return json.loads(dumps(cursor))

@api_app.get("/crud/listExecutionSteps/{id}")
async def listExecutionSteps(id:str):
    d = db["executions"].find_one({"_id": ObjectId(id) })
    return json.loads(dumps(d))

@api_app.post("/exec/completeExecution/{id}")
async def completeExecution(id:str):
    db["executions"].update_one({"_id": ObjectId(id) }, {"$set": {"status": "complete"} })

@api_app.post("/exec/errorExecution/{id}")
async def errorExecution(id:str):
    db["executions"].update_one({"_id": ObjectId(id) }, {"$set": {"status": "error"} })

@api_app.get("/exec/getLastStepOutput/{execid}/{currStepId}")
async def getLastStepOutput(execid:str, currStepId:str):
    d = db["executions"].find_one({"_id": ObjectId(execid) })
    retVal = {}
    retVal["response"] = ""
    retVal["status"] = "unknown"
    i = 0
    found = False
    for wf in d["workflow"]["wf"]:
        if wf["_id"]["$oid"] == currStepId:
            found = True
            break
        i += 1
    if found:
        if i > 0:
            retVal["response"] = d["workflow"]["wf"][i-1]["result"]
            retVal["status"] = d["workflow"]["wf"][i-1]["status"]
    
    return json.loads(dumps(retVal))

@api_app.get("/hello")
async def hello():
    return {"message": "Hello World"}
