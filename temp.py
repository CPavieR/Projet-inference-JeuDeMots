# https://jdm-api.demo.lirmm.fr/schema
import requests
import json
import re
import ast
import copy
from lib_helpers import HelperJDM
link_api = "https://jdm-api.demo.lirmm.fr/schema"
api_get_node_by_name = "https://jdm-api.demo.lirmm.fr/v0/node_by_name/{node_name}"
get_relation_from = "https://jdm-api.demo.lirmm.fr/v0/relations/from/{node1_name}"
get_relation_between = "https://jdm-api.demo.lirmm.fr/v0/relations/from/{node1_name}/to/{node2_name}"
get_node_by_id = "https://jdm-api.demo.lirmm.fr/v0/node_by_id/{node_id}"
cache={}

def translate_relationNBtoNOM(relation):
    nom = "Uknown"
    try:
        nom = HelperJDM.nombre_a_nom[relation]
        return nom
    except Exception:
        return nom


"""
def translate_relationNBtoNOM(relation):
    if relation in nombre_a_nom.keys():
        return nombre_a_nom[relation]
    return "Unknown"
"""


def requestWrapper(url):
    global cache
    """cache = open("cache.json", "r")
    data = json.load(cache)
    cache.close()"""
    if url in cache:
        return cache[url]
    response = requests.get(url)

    cache[url] = response.text
    """cache = open("cache.json", "w")
    cache.write(json.dumps(data))"""
    return response.text


def getNodeByName(node_name):
    jsonString = requestWrapper(
        api_get_node_by_name.format(node_name=node_name))
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


class Graph:
    def __init__(self):
        self.nodes = {}
        self.edges = []

    def add_node(self, node_id, name):
        self.nodes[node_id] = name

    def add_edge(self, node1_id, node2_id, relation, weight):
        self.edges.append((node1_id, node2_id, relation, weight))

    def print_graph(self):
        for edge in self.edges:
            node1_id, node2_id, relation, weight = edge
            node1_name = self.nodes[node1_id]
            node2_name = self.nodes[node2_id]
            print(f"{node1_name} {relation} {node2_name} (w={weight})")

    def test_node(self, node_id):
        return node_id in self.nodes

    def test_edge(self, node1_id, node2_id):
        for edge in self.edges:
            if edge[0] == node1_id and edge[1] == node2_id:
                return True
        return False

    def printTriangles(self, node1, node2):
        msg = ""
        for edge in self.edges:
            if edge[0] == node1:
                typeOfTriangles = ""
                if edge[2] == "r_isa":
                    typeOfTriangles = "deductive"
                if edge[2] == "r_hypo":
                    typeOfTriangles = "inductive"
                for edge2 in self.edges:
                    if edge2[0] == edge[1] and edge2[1] == node2:
                        msg = msg+("Triangle "+typeOfTriangles +
                                   f" : {self.nodes[node1]} -> {edge[2]} -> {self.nodes[edge[1]]} -> {edge2[2]} -> {self.nodes[node2]}"+"\n")
        return msg


"""node1= "chat"
node2 = "calin"
response = requests.get(get_relation_between.format(node1_name=node1, node2_name=node2))
print(response.status_code)
print(response.text)"""


def sortRelationsInducDeduc(relations):
    accepted_types = [6, 8]
    relations = [
        relation for relation in relations if relation["type"] in accepted_types]
    relations = sorted(relations, key=lambda x: x["w"], reverse=True)
    return relations[:3]


def sortRelationsSym(relations):
    accepted_types = [5, 24]
    relations = [
        relation for relation in relations if relation["type"] in accepted_types]
    relations = sorted(relations, key=lambda x: x["w"], reverse=True)
    return relations[:3]


def create_graphInducDeduc(node1_data, node2_data, relation_wanted):
    # On initialise le graphe avec neoud de depart et objectif
    graph = Graph()
    graph.add_node(node1_data["id"], node1_data["name"])
    graph.add_node(node2_data["id"], node2_data["name"])
    # on fait la requete à l'api pour avoir les relations du noeud de depart
    li_relation = requestWrapper(
        get_relation_from.format(node1_name=node1_data["name"]))
    li_relation = json.loads(li_relation)
    # On trie les requetes qui concernne que les relations inductives et deductives
    li_relation["relations"] = sortRelationsInducDeduc(
        li_relation["relations"])
    # pour chacune de ces relations :
    for relation in li_relation["relations"]:
        # on recupere le noeud de destination de la relation
        node2Id = relation["node2"]
        node2 = None
        for node in li_relation["nodes"]:
            if node["id"] == node2Id:
                node2 = node
        # on recupere les relation entre le noeud de destination et l'objectif
        li_relation2 = requestWrapper(get_relation_between.format(
            node1_name=node2["name"], node2_name=node2_data["name"]))
        li_relation2 = json.loads(li_relation2)
        if "relations" in li_relation2:
            # pour chacune de ces relation
            for rel in li_relation2["relations"]:
                # on teste qu'elle sont du bon type
                if (rel["type"] == HelperJDM.nom_a_nombre[relation_wanted]):
                    # si oui, on ajoute tout au graphe
                    graph.add_node(node2["id"], node2["name"])
                    graph.add_edge(node1_data["id"], node2["id"], translate_relationNBtoNOM(
                        relation["type"]), relation["w"])
                    graph.add_edge(node2["id"], node2_data["id"], translate_relationNBtoNOM(
                        rel["type"]), rel["w"])

    msg = graph.printTriangles(node1_data["id"], node2_data["id"])
    print(msg)
    return msg

def tuple_chemin_to_hasahtable(inf, chemin):
    #inf = list of string
    #chemin_tuple = lst of dict
    inf_lst = ast.literal_eval(inf)
    res=""
    i=0
    for e in chemin:
        res+=(e["name"])
        if i != len(inf_lst):
            res+=" -> "
        if i < len(inf_lst):
            res+=(inf_lst[i])
            if i != len(inf_lst) and i!=0:
                res+=" -> "
            i+=1
            if i < len(inf_lst):
                res+= " -> "
    return res


def create_graphGen(node1_data, node2_data, li_Inference, wanted_relation):
    # On initialise le graphe avec neoud de depart et objectif
    #li_inference = liste de type d'inference, par exemple : [["r_isa", "{r_cible}"],["r_hypo", "{r_cible}"],["r_syn", "{r_cible}"],["{r_cible}", "r_syn"]]
    graph = Graph()
    graph.add_node(node1_data["id"], node1_data["name"])
    graph.add_node(node2_data["id"], node2_data["name"])
    # on recupère la taille de la l'inference la plus grande pour savoir le nombre de bouble a faire
    max_size = max([len(inf) for inf in li_Inference])
    # on initialise un dico associant chaque type d'inference à une liste de chemins possibles
    chemins = {str(inf): [[node1_data]] for inf in li_Inference}
    poids_chemin = {}
    #on initialise le poids de chaque chemin à 0
    for (inference_courante, chemins_par_type_inf) in chemins.items():
        for chemin in chemins_par_type_inf:
            poids_chemin[tuple_chemin_to_hasahtable(inference_courante, chemin)] = 0
    #on boucle sur la longueur de chaque type d'inférence
    i = 0
    while i < max_size:
        # on fait une deepcopie des chemins pour pouvoir les modifier
        chemins_copy = copy.deepcopy(chemins)
        # on boucle sur chaque type d'inférence
        for (inference_courante, liste_chemins_inference_courante) in chemins_copy.items():
            #on boucle pour chemin possible
            for chemin in liste_chemins_inference_courante:
                #on convertie l'inférence courante de string à liste
                inference_courante_list = ast.literal_eval(inference_courante)
                # si on est pas à la fin du chemin ou que ce chemin n'a pas échoué précédement on continue
                if i < len(inference_courante_list) and i+1 == len(chemin):
                    try:
                        # on recupere les relations du noeud de depart
                        li_relation = requestWrapper(
                            get_relation_from.format(node1_name=chemin[i]["name"]))
                        li_relation = json.loads(li_relation)
                        # on trie les relations pour ne garder que celles qui sont dans l'inférence
                        li_relation["relations"] = [
                            relation for relation in li_relation["relations"] if relation["type"] == HelperJDM.nom_a_nombre[inference_courante_list[i]]]
                       # on normalise les poids
                        HelperJDM.normalize(li_relation["relations"])
                        print(li_relation["relations"])
                         # on trie les relations par poids
                        li_relation["relations"] = sorted(
                            li_relation["relations"], key=lambda x: x["w"], reverse=True)
                        #Si on est pas à la fin du chemin, on ne garde que les 5 premières relations
                        #dans le cas opposé on garde tout pour éviter d'échoué le chemin
                        if (i+1 != len(inference_courante_list)):
                            li_relation["relations"] = li_relation["relations"][:3]
                        # pour chaque relation qui ont passées le filtre
                        for relation in li_relation["relations"]:
                            # on recupere le noeud de destination
                            node2Id = relation["node2"]
                            node2 = None
                            for node in li_relation["nodes"]:
                                if node["id"] == node2Id:
                                    node2 = node
                            # si le noeud final du type d'inference, on veut que celui ci soit le noeud de destination, sinon on s'en fiche
                            if ((i+1 == len(inference_courante_list) and node2["id"] == node2_data["id"]) or i+1 != len(inference_courante_list)):
                                # on continue le chemin courant avec le noeud que l'ont vient de trouver
                                new_chemin = chemin + [node2]
                                # on ajoute ce chemin à la liste des chemins possibles
                                chemins[str(inference_courante_list)].append(new_chemin)
                                print(tuple_chemin_to_hasahtable(inference_courante, new_chemin))
                                #On ajoute le poids du chemin courant au dico des poids
                                if tuple_chemin_to_hasahtable(inference_courante, chemin) in poids_chemin:
                                    poids_chemin[tuple_chemin_to_hasahtable(inference_courante, new_chemin)] = poids_chemin[tuple_chemin_to_hasahtable(inference_courante, chemin)] + relation["w"]
                                else:
                                    print(f"Warning: Key {tuple_chemin_to_hasahtable(inference_courante, chemin)} not found in poids_chemin.")
                    except Exception as e:
                        print("Exception : ", e)
        #A l'avenir, quand le calculs des poids sera normalisé, mettre un filtre sur les chemins ici, prendre le top5 de tout les types d'inférence
        i = i+1
        print(i)
    #On affiche les chemins et leur poids
    res=""
    for (inference_courante, chemin_inf) in chemins.items():
        inf_lst = ast.literal_eval(inference_courante)
        for chemin in chemin_inf:
            if len(chemin) == len(inf_lst)+1:
                for i in range(len(inf_lst)):
                    res=res+chemin[i]["name"] + " -> " +inf_lst[i] + " -> "
                    if i+1 == len(inf_lst):
                        res=res+chemin[i+1]["name"]
                # (inf + " : " + chemin)
                res= res+" : "+str(poids_chemin[tuple_chemin_to_hasahtable(inference_courante, chemin)])+"\n"
    ##for (inf, chemin_ind) in chemins.items():
        #for chemin in chemin_ind:
            #print(str(inf) + " : " + str(chemin))
        # print(poids_chemin[(inf, chemin)])
    return res


def create_graphSymTri(node1_data, node2_data, relation_wanted):
    graph = Graph()
    graph.add_node(node1_data["id"], node1_data["name"])
    graph.add_node(node2_data["id"], node2_data["name"])

    li_relation = requestWrapper(
        get_relation_from.format(node1_name=node1_data["name"]))
    li_relation = json.loads(li_relation)
    li_relation["relations"] = sortRelationsSym(li_relation["relations"])
    for relation in li_relation["relations"]:
        node2Id = relation["node2"]
        node2 = None
        for node in li_relation["nodes"]:
            if node["id"] == node2Id:
                node2 = node
        li_relation2 = requestWrapper(get_relation_between.format(
            node1_name=node2["name"], node2_name=node2_data["name"]))
        li_relation2 = json.loads(li_relation2)
        if "relations" in li_relation2:
            # li_relation2["relations"]=sortRelationsSym(li_relation2["relations"])
            for rel in li_relation2["relations"]:
                if (rel["type"] == HelperJDM.nom_a_nombre[relation_wanted]):
                    graph.add_node(node2["id"], node2["name"])
                    graph.add_edge(node1_data["id"], node2["id"], translate_relationNBtoNOM(
                        relation["type"]), relation["w"])
                    graph.add_edge(node2["id"], node2_data["id"], translate_relationNBtoNOM(
                        rel["type"]), rel["w"])

    msg = graph.printTriangles(node1_data["id"], node2_data["id"])
    print(msg)
    return msg


# chat r_isa animal
# chat r_agent-1 miauler
# pigeon r_agent-1 voler
dicttt = {'("[\'r_isa\', \'r_isa\']", [[{\'id\': 150, \'name\': \'chat\', \'type\': 1, \'w\': 5591, \'c\': 0, \'level\': 84.7367, \'infoid\': None, \'creationdate\': \'2007-06-21\', \'touchdate\': \'2025-02-27T12:14:04\'}]])': 0,
          '("[\'r_hypo\', \'r_isa\']", [[{\'id\': 150, \'name\': \'chat\', \'type\': 1, \'w\': 5591, \'c\': 0, \'level\': 84.7367, \'infoid\': None, \'creationdate\': \'2007-06-21\', \'touchdate\': \'2025-02-27T12:14:04\'}]])': 0, 
          '("[\'r_syn\', \'r_isa\']", [[{\'id\': 150, \'name\': \'chat\', \'type\': 1, \'w\': 5591, \'c\': 0, \'level\': 84.7367, \'infoid\': None, \'creationdate\': \'2007-06-21\', \'touchdate\': \'2025-02-27T12:14:04\'}]])': 0}


def callFromDiscord(input_text,li_infer):
    li = re.split(r"(\sr_.+\s)", input_text)
    if len(li) == 3:
        node1 = li[0].strip()
        node2 = li[2].strip()
        relation = li[1].strip()
        print(f"node1: {node1}, node2: {node2}, relation: {relation}")
        # print node1 id
        node1_data = getNodeByName(node1)
        # r_syn       ,["{r_cible}", "r_syn"],["r_syn", "{r_cible}", "r_syn"],["r_syn", "{r_cible}", "r_syn"]
        node2_data = getNodeByName(node2)
        li_infer= li_infer.format(
            r_cible=relation)
        res=create_graphGen(node1_data, node2_data, ast.literal_eval(li_infer), relation)
        cacheFile = open("cache.json", "w")
        cacheFile.write(json.dumps(cache))
        return res

def callFromDiscordSym(input_text):
    li_infer = '[["r_syn", "{r_cible}"],["{r_cible}", "r_syn"]]'
    return callFromDiscord(input_text,li_infer)


def callFromDiscordInduc(input_text):
    li_infer = '[["r_isa", "{r_cible}"],["r_hypo", "{r_cible}"]]'
    return callFromDiscord(input_text,li_infer)

def callFromDiscordAll(input_text):
    li_infer = '[["r_isa", "{r_cible}"],["r_hypo", "{r_cible}"],["r_syn", "{r_cible}"],["{r_cible}", "r_syn"]]'
    return callFromDiscord(input_text,li_infer)

cacheFile = open("cache.json", "r")
cache = json.load(cacheFile)
cacheFile.close()
if __name__ == "__main__":
    while True:
        input_text = input(
            "entrer une relation entre deux mots:(exit pour quitter) ")
        if input_text == "exit":
            break
        li = re.split(r"(\sr_.+\s)", input_text)
        if len(li) == 3:
            node1 = li[0].strip()
            node2 = li[2].strip()
            relation = li[1].strip()
            print(f"node1: {node1}, node2: {node2}, relation: {relation}")
            # print node1 id
            node1_data = getNodeByName(node1)
            # r_syn       ,["{r_cible}", "r_syn"],["r_syn", "{r_cible}", "r_syn"],["r_syn", "{r_cible}", "r_syn"]
            node2_data = getNodeByName(node2)
            li_infer = '[["r_isa", "{r_cible}"],["r_hypo", "{r_cible}"],["r_syn", "{r_cible}"],["{r_cible}", "r_syn"]]'.format(
                r_cible=relation)
            create_graphGen(node1_data, node2_data, ast.literal_eval(li_infer), relation)
            cacheFile = open("cache.json", "w")
            cacheFile.write(json.dumps(cache))
