import os
import requests
import pymongo
from datetime import datetime, timezone
from bson.objectid import ObjectId
from croniter import croniter

# MongoDB connection string from environment
connstr = os.environ.get("SPECUIMDBCONNSTR") or os.environ.get("MDBCONNSTR")
client = pymongo.MongoClient(connstr)
db = client["excutor"]

# API endpoint (adjust as needed)
server = os.environ["PORTAL"].strip()
API_URL = os.environ.get("ENQUEUE_API_URL", f"{server}/api/exec/enqueueWorkflow/")

now = datetime.now(timezone.utc)

# Find all workflows with isCronType: true
cron_workflows = db["workflows"].find({"isCronType": True})

for wf in cron_workflows:
    print(f"Found Workflow Name: {wf['name']}")
    cron_expr = wf.get("cronExpression")
    if not cron_expr:
        print("\tNo cron expression found, skipping.")
        continue
    # Check if the cron should run now
    itr = croniter(cron_expr, now)
    prev_time = itr.get_prev(datetime)
    # Allow a 60-second window for execution
    if (now - prev_time).total_seconds() < 59:
        # Prepare payload (empty or as needed)
        payload = wf.get("cronPayload", {})
        workflow_id = str(wf["_id"])
        try:
            resp = requests.post(f"{API_URL}{workflow_id}", json=payload)
            print(f"\tEnqueued workflow {workflow_id}: {resp.status_code}")
        except Exception as e:
            print(f"\tFailed to enqueue workflow {workflow_id}: {e}")
    else:
        print(f"\tNot time to run yet. Last run was at {prev_time.isoformat()}")
