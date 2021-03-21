#file for taking the default mapping.json and creating a remake json file with item IDs as keys


import json
newdict = {}
f = open('mapping.json')

data = json.load(f)
for each in data:
    nameStr = each.get('name')
    id = each.get('id')
    newdict[id] = { 
        'examine' : each.get('examine',0),
        'limit': each.get('limit', 0),
        'members': each.get('members'),
        'highalch': each.get('highalch',0),
        'lowalch' : each.get('lowalch', 0),
        'value': each.get('value',0),
        'icon': each.get('icon',0),
        'name': str(nameStr)
    }
    
    
print(newdict)

with open("remakeMapping.json",'w') as write_file:
    json.dump(newdict,write_file)


     

