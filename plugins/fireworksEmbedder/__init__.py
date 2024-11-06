import json
import os
import openai
import requests

context = json.loads(os.environ["EXECUTORTASK"].strip())

fwapikeyarg = next(obj for obj in context["arguments"] if obj["key"] == "fwapikey")
fwapikey = fwapikeyarg["value"]

fwmodelarg = next(obj for obj in context["arguments"] if obj["key"] == "fwmodel")
fwmodel = fwmodelarg["value"]

lastOutput = json.loads(os.environ["EXECUTORLASTOUTPUT"].strip())


client = openai.OpenAI(
    base_url = "https://api.fireworks.ai/inference/v1",
    api_key=fwapikey,
)

response = client.embeddings.create(
  model=fwmodel,
  input="search_document: " + lastOutput["response"],
)

retVal = {}
retVal["embedding"] = response.data[0].embedding
retVal["text"] = lastOutput["response"]

print(json.dumps(retVal))