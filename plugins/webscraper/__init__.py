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
#print("DOWNLOADING" + link)
page = requests.get(link)
soup = BeautifulSoup(page.content, 'html.parser')
title = soup.title.text
content = soup.get_text()

print(content)