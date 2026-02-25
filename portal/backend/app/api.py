from fastapi import FastAPI, Response, File, UploadFile, Form
from fastapi import Request
from fastapi.responses import JSONResponse
import jwt
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
def kanopy_internal_auth_middleware(app):
    async def middleware(request: Request, call_next):
        # Only enforce for /api/* paths and if both env vars exist
        required_header = os.environ.get("REQUIREDAUTHHEADER")
        required_group = os.environ.get("REQUIREDAUTHGROUP")
        if required_header and required_group:
            required_header = os.environ.get("REQUIREDAUTHHEADER").strip()
            required_group = os.environ.get("REQUIREDAUTHGROUP").strip()
            if request.url.path.startswith("/api/crud") or request.url.path.startswith("/api/analytics"):
                header = request.headers.get(required_header)
                if not header:
                    return JSONResponse(status_code=401, content={"detail": f"Missing {required_header} header"})
                try:
                    # JWT decode without verification for demo; add secret/algorithm for production
                    payload = jwt.decode(header, options={"verify_signature": False})
                except Exception:
                    return JSONResponse(status_code=401, content={"detail": "Invalid JWT in header"})
                groups = payload.get("groups", [])
                # allowed_roles is a list, can be comma-separated in env var
                allowed_roles = [role.strip() for role in required_group.split(",") if role.strip()]
                if not any(role in groups for role in allowed_roles):
                    return JSONResponse(status_code=403, content={"detail": "Insufficient role"})
        return await call_next(request)
    return middleware

api_app.middleware("http")(kanopy_internal_auth_middleware(api_app))
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
async def listAllWorkflows():
    pipeline = [
        {
            '$project': {
                '_id': 1, 
                'name': 1, 
                'stepCount': {
                    '$size': '$wf'
                }
            }
        }, {
            '$sort': {
                '_id': -1
            }
        }
    ]
    cursor = db["workflows"].aggregate(pipeline)
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
    obj = {"name":"New Workflow", "wf":[], "modified": datetime.now(timezone.utc)}
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
    d["modified"] = datetime.now(timezone.utc)
    db["workflows"].update_one({"_id": ObjectId(id) }, {"$set": d })

@api_app.get("/crud/getPageConfig/{page}")
async def getPageConfig(page:str):
    d = db["config"].find_one({"_id": page })
    if not d:
        return {"_id": page, "charts": [] }
    return json.loads(dumps(d))

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

@api_app.get("/crud/retryExecution/{id}")
async def retryExecution(id:str):
    # get current matching ID, copy it, set status to queued, and insert as new document
    d = db["executions"].find_one({"_id": ObjectId(id) })
    newObj = d.copy()
    newObj["originalId"] = d["_id"]
    newObj["isRetry"] = True
    newObj.pop("_id")
    newObj.pop("ownedBy")
    newObj["status"] = "queued"
    newObj["created"] = datetime.now(timezone.utc)
    newObj["modified"] = datetime.now(timezone.utc)
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

@api_app.get("/crud/servers")
async def listServers():
    cursor = db["servers"].find({}).sort("lastSeen", pymongo.DESCENDING)
    return json.loads(dumps(cursor))

@api_app.get("/analytics/serverStats")
async def serverStats():
    pipeline = [
        {
            '$group': {
                '_id': '$ownedBy', 
                'count': {
                    '$sum': 1
                }
            }
        }
    ]
    cursor = db["executions"].aggregate(pipeline)
    return json.loads(dumps(cursor))

@api_app.put("/crud/updateServer")
async def updateServer(server: Dict[Any, Any]):
    db["servers"].update_one({"_id": server["name"]}, {"$set": {"nextPoll":server["nextPoll"]}})

@api_app.post("/exec/executionOutput")
async def executionOutput(q: Dict[Any, Any]):
    query = {"_id": ObjectId(q["workflowId"]["$oid"])}
    update = {"$set": {"workflow.wf."+str(q["index"])+".status": q["status"], "workflow.wf."+str(q["index"])+".result": q["result"]}}
    print(update)
    db["executions"].update_one(query, update)

@api_app.get("/exec/downloadZip/{pointerid}")
async def downloadZip(pointerid: str):
    fs = gridfs.GridFS(db)
    file = fs.get(ObjectId(pointerid))
    return StreamingResponse(file, media_type="application/zip")

@api_app.get("/crud/listAllExecutions")
async def listAllExecutions(errored_only: bool = False):
    two_days_ago = datetime.now(timezone.utc) - timedelta(days=2)
    query = {"created": {"$gte": two_days_ago}}
    if errored_only:
        one_minute_ago = datetime.now(timezone.utc) - timedelta(minutes=1)
        query["$or"] = [
            {"status": "error"},
            {"status": "queued", "created": {"$lt": one_minute_ago}}
        ]
    cursor = db["executions"].find(
        query,
        {"_id": 1, "workflow._id": 1, "workflow.name": 1, "created": 1, "status":1}
    ).sort("_id", pymongo.DESCENDING)
    return json.loads(dumps(cursor))

@api_app.get("/crud/listExecutionSteps/{id}")
async def listExecutionSteps(id:str):
    d = db["executions"].find_one({"_id": ObjectId(id) })
    return json.loads(dumps(d))

@api_app.get("/crud/getExecutionDebug/{id}")
async def getExecutionDebug(id:str):
    if "SPLUNKSERVER" in os.environ:
        if "SPLUNKINDEX" in os.environ:
            d = db["executions"].find_one({"_id": ObjectId(id) })
            splunkServer = os.environ["SPLUNKSERVER"].strip()
            splunkIndex = os.environ["SPLUNKINDEX"].strip()
            if "ownedBy" in d:
                serverName = d["ownedBy"]
                # format of url is ?q=search%20index%3Dsa-prod%20source%3D"*SERVER*"&display.page.search.mode=verbose&dispatch.sample_ratio=1&workload_pool=&earliest=1771431082&latest=1771519582&sid=1771519865.228150
                url = f"{splunkServer}/en-US/app/search/search?q=search%20index%3D{splunkIndex}%20source%3D%22*{serverName}*%22&display.page.search.mode=verbose&dispatch.sample_ratio=1&workload_pool=&earliest={int(d['created'].timestamp())}&latest={int((d['created'] + timedelta(minutes=10)).timestamp())}"
                return {"url": url}
            else:
                return {}, 200
    else:
        return {}, 200

@api_app.post("/exec/completeExecution/{id}")
async def completeExecution(id:str, d: Dict[Any, Any]):
    db["executions"].update_one({"_id": ObjectId(id) }, {"$set": {"status": d["status"]}})

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
