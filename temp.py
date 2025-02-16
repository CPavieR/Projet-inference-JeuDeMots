# https://jdm-api.demo.lirmm.fr/schema
import requests
import json
link_api ="https://jdm-api.demo.lirmm.fr/schema"
api_get_node_by_name = "https://jdm-api.demo.lirmm.fr/v0/node_by_name/{node_name}"
get_relation_from ="https://jdm-api.demo.lirmm.fr/v0/relations/from/{node1_name}"
get_relation_between = "https://jdm-api.demo.lirmm.fr/v0/relations/from/{node1_name}/to/{node2_name}"



def requestWrapper(url):
    cache = open("cache.json", "r")
    data = json.load(cache)
    cache.close()
    if url in data:
        print("Cache hit")
        return data[url]
    response = requests.get(url)
    
    data[url] = response.text
    cache = open("cache.json", "w")
    cache.write(json.dumps(data))
    return response.text

def getNodeByName(node_name):
    jsonString = requestWrapper(api_get_node_by_name.format(node_name=node_name))
    return json.loads(jsonString)


"""response = requests.get(link_api)
print(response.status_code)
print(response.text)"""

# Get node by name
node_name = "chat"
response = requestWrapper(api_get_node_by_name.format(node_name=node_name))
print(response)
node_name = "calin"
response = requestWrapper(api_get_node_by_name.format(node_name=node_name))
print(response)
"""
# Get relation from node
node1_name = "chat"
response = requests.get(get_relation_from.format(node1_name=node1_name))
print(response.status_code)
print(response.text)
"""


"""node1= "chat"
node2 = "calin"
response = requests.get(get_relation_between.format(node1_name=node1, node2_name=node2))
print(response.status_code)
print(response.text)"""


if __name__ == "__main__":
    print("Hello world")
    while True:
        input_text = input("entrer une relation entre deux mots:(exit pour quitter) ")
        if input_text == "exit":
            break
        li = input_text.split(" ")
        if len(li) == 3:
            node1 = li[0]
            node2 = li[2]
            relation = li[1]
            print(f"node1: {node1}, node2: {node2}, relation: {relation}")
            #print node1 id
            node1_data = getNodeByName(node1)
            print(node1_data["id"])