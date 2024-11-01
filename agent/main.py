import requests
import os
import json
import zipfile
import subprocess
import time

server = os.environ["PORTAL"].strip()
agentDetails = {"name":"Test Agent"}

while True:

    print("Getting next workflow")
    response = requests.post(f"{server}/api/exec/getNextExecution", json = agentDetails)
    print(response.text)
    resObj = json.loads(response.text)
    index = 0

    os.environ["EXECUTOR"] = response.text

    for wf in resObj['workflow']["wf"]:
        print("--------------------BEGIN WORKFLOW----------------------")
        templateFileId = wf["gridfspointer"]["$oid"]
        zipfileName = templateFileId+".zip"    
        os.chdir("/usr/src/app")
        if not os.path.exists(templateFileId):
            print("Downloading template file")
            file = requests.get(f"{server}/api/exec/downloadZip/{templateFileId}")
            open(zipfileName, "wb").write(file.content)

            print("Unzipping")
            with zipfile.ZipFile(zipfileName, 'r') as zip_ref:
                zip_ref.extractall("./"+templateFileId)

            os.chdir(templateFileId)

            if wf["engine"] == "python3":
                print("Making venv")
                os.system("python3 -m venv venv")
                os.system("./venv/bin/pip install -r requirements.txt")
        else:
            print("Template already downloaded")
            os.chdir(templateFileId)

        print("Running workflow")
        if wf["engine"] == "python3":
            result = subprocess.check_output("./venv/bin/python3 __init__.py", shell=True, text=True)
        elif wf["engine"] == "nodejs":
            result = subprocess.check_output("node index.js", shell=True, text=True)

        print("Saving result")
        postObj = {"result":result, "status":"complete", "taskId":wf["_id"]["$oid"], "workflowId":resObj["_id"], "index":index}
        response = requests.post(f"{server}/api/exec/executionOutput", json = postObj)
        print(postObj)
        print("--------------------END WORKFLOW----------------------")
        index += 1

    if index > 0:
        print("All workflows complete")
        response = requests.post(f"{server}/api/exec/completeExecution/"+resObj["_id"]["$oid"], json = agentDetails)

    print("Sleeping")
    time.sleep(60)