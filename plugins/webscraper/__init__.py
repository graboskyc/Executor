from bson.json_util import dumps
from bson.timestamp import Timestamp
from bson.objectid import ObjectId
import json
import os
from bs4 import BeautifulSoup
import requests

context = json.loads(os.environ["EXECUTORTASK"].strip())
arg = next(obj for obj in context["arguments"] if obj["key"] == "page")
link = arg["value"]
response = {}
response["crawls"] = []

if isinstance(link, list):
    for l in link:
        #print("DOWNLOADING" + link)
        page = requests.get(l)
        soup = BeautifulSoup(page.content, 'html.parser')
        title = soup.title.text
        content = soup.get_text()
        response["crawls"].append({"title": title, "content": content})
else:
    page = requests.get(link)
    soup = BeautifulSoup(page.content, 'html.parser')
    title = soup.title.text
    content = soup.get_text()
    response["crawls"].append({"title": title, "content": content})

print(json.dumps(response))