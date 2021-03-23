import json


with open('remakeMapping.json','r') as myfile:
    data = myfile.read()

obj = json.loads(data)

print(obj['99']['name'])