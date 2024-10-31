import requests
import os
import json
import zipfile
import subprocess
from datetime import datetime
from datetime import timezone

server = os.environ["PORTAL"].strip()
agentDetails = {"name":"Test Agent"}

print("Getting next workflow")
response = requests.post(f"{server}/api/exec/getNextExecution", json = agentDetails)
print(response.text)
resObj = json.loads(response.text)


templateFileId = resObj['workflow']["wf"][0]["gridfspointer"]["$oid"]
zipfileName = templateFileId+".zip"
if not os.path.exists(templateFileId):
    print("Downloading template file 0")
    file = requests.get(f"{server}/api/exec/downloadZip/{templateFileId}")
    open(zipfileName, "wb").write(file.content)

    print("Unzipping")
    with zipfile.ZipFile(zipfileName, 'r') as zip_ref:
        zip_ref.extractall("./"+templateFileId)

    os.chdir(templateFileId)

    print("Making venv")
    os.system("python3 -m venv venv")
    os.system("./venv/bin/pip install -r requirements.txt")
else:
    print("Template already downloaded")
    os.chdir(templateFileId)

print("Running workflow")
result = subprocess.check_output("./venv/bin/python3 __init__.py", shell=True, text=True)
print(result)

print("Saving result")
resultObj = {"result":result, "status":"complete", "taskId":resObj['workflow']["wf"][0]["_id"]["$oid"], "workflowId":resObj["_id"]}
response = requests.post(f"{server}/api/exec/executionOutput", json = resultObj)