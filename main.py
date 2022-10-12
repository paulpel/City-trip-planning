import json

with open("attractions.json") as jf:
    data = json.load(jf)

print(len(data['rome']))