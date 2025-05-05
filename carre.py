from lib_helpers import HelperJDM
import json
import requests
import json
import re
import ast
import copy
import re
import math
import numpy as np
import requests_cache
link_api = "https://jdm-api.demo.lirmm.fr/schema"
api_get_node_by_name = "https://jdm-api.demo.lirmm.fr/v0/node_by_name/{node_name}"
get_relation_from = "https://jdm-api.demo.lirmm.fr/v0/relations/from/{node1_name}"
get_relation_between = "https://jdm-api.demo.lirmm.fr/v0/relations/from/{node1_name}/to/{node2_name}"
get_node_by_id = "https://jdm-api.demo.lirmm.fr/v0/node_by_id/{node_id}"
cache = {}

R_SYN = 5
MAX_INFERENCES = 10

requests_cache.install_cache('jdm_cache', backend='sqlite', expire_after=None)
session = requests.Session()
def translate_relationNBtoNOM(relation):
    nom = "Unknown"
    try:
        nom = HelperJDM.nombre_a_nom[relation]
        return nom
    except Exception:
        return nom

def translate_relationNBtoNOM(relation):
    nom = "Uknown"
    try:
        nom = HelperJDM.nombre_a_nom[relation]
        return nom
    except Exception:
        return nom


def requestWrapper(url):
    global cache
    """cache = open("cache.json", "r")
    data = json.load(cache)
    cache.close()"""
    #if url in cache:
    #    return cache[url]
    #response = requests.get(url)
    response = session.get(url)
    #cache[url] = response.text
    #"""cache = open("cache.json", "w")
    #cache.write(json.dumps(data))"""
    return response.text


def tuple_chemin_to_hasahtable(inf, chemin):
    inf_lst = ast.literal_eval(inf)
    res = ""
    i = 0
    for e in chemin:
        res += (e["name"])
        if i != len(inf_lst):
            res += " -> "
        if i < len(inf_lst):
            res += (inf_lst[i])
            if i != len(inf_lst) and i != 0:
                res += " -> "
            i += 1
            if i < len(inf_lst):
                res += " -> "
    return res



def filter_relations(relationSet : dict, relationsToKeep: list, max_num_relations=0):
    res = []
    for r in relationSet:
        type = r["type"]
        if type in relationsToKeep:
            res.append(r)
    res.sort(reverse=True, key=lambda x : x["w"])
   
    return res

def carre(depart,relationCible,arrivee):
    resultats = []
    # tient le compte du nombre de relations inferees
    count = 0
    try:
        relationCibleNumber = HelperJDM.nom_a_nombre[relationCible.strip()]
    except Exception as e:
        print("Erreur impossible de trouver la relation cible")
        return resultats
    # Aller chercher les noeuds correpondants dans l'api JdM
    nodeDepart = json.loads(requestWrapper(api_get_node_by_name.format(node_name=depart)))
    nodeBut = json.loads(requestWrapper(api_get_node_by_name.format(node_name=arrivee)))
    # Requete pour obtenir les relations syn du depart
    relationsDepart = json.loads(requestWrapper(get_relation_from.format(node1_name=depart)))["relations"]
    
    relationsDepart = filter_relations(relationsDepart,[R_SYN])
    
    # Requete pour obtenir les relations syn du but
    relationsBut = json.loads(requestWrapper(get_relation_from.format(node1_name=arrivee)))["relations"]
    relationsBut = filter_relations(relationsBut,[R_SYN])
    #print(relationsDepart, relationsBut)
    if len(relationsDepart) == 0 or len(relationsBut) == 0 :
        print("cannot cook")
        return resultats
    
    # boucle imbriquee qui fait un produit cartesien des syn du node de depart et des syn du node but
    for r1 in relationsDepart:
        node1_syn = json.loads(requestWrapper(get_node_by_id.format(node_id=r1["node2"])))
        # code pour enlever les nodes en anglais
        if re.match("en:.*",node1_syn["name"]):
            continue
        elif node1_syn["name"].startswith("::"):
            continue
        for r2 in relationsBut:
            node2_syn = json.loads(requestWrapper(get_node_by_id.format(node_id=r2["node2"])))
            if re.match("en:.*",node2_syn["name"]):
                continue
            elif node2_syn["name"].startswith("::"):
                continue
            # trouve ttes les relations entres les 2 synomymes
            relationsSynEntre = requestWrapper(get_relation_between.format(node1_name=node1_syn["name"],node2_name=node2_syn["name"]))
            try:
                relationsSynEntre = json.loads(relationsSynEntre)["relations"]
                # en enleve les relations qui ne nous interessent pas
                relationsSouhaitees = filter_relations(relationsSynEntre,[relationCibleNumber])
                #print("R1 :", r1)
                # print("R2 :",r2)
                # print(relationsSouhaitees)
                for r in relationsSouhaitees:
                    #print(f"{n1["name"]} r {n2["name"]} W : {r["w"]}")
                    #resultats.append([nodeDepart,n1,nodeBut,n2])
                    #print(nodeDepart["name"],nodeBut["name"], node1_syn["name"], node2_syn["name"])
                    chemin_courant = [r1,r,r2]
                    HelperJDM.normalize(chemin_courant)
                    try:
                        negative = False
                        poids = 0
                        for i in range(3):
                            if(chemin_courant[i]["w"] < 0):
                                negative = True
                            poids += np.log(abs(chemin_courant[i]["w"]))
                        poids /= 3
                        poids = np.exp(poids)
                        if negative:
                            poids *= -1
                        print(f"poids quelconque : {poids}")
                    except Exception as e:
                        print(e)
                    
                    resultats.append({"chemin":chemin_courant,"w":poids})

                    if(poids > 0):
                        count += 1
                        print(f"poid positif : {poids}, count : {count}")
                    
                    if(count >= MAX_INFERENCES):
                        print("Found 10 positive relations !")
                        resultats = sorted(
                            resultats, key=lambda x: x["w"], reverse=True)
                        
                        for path in resultats:
                            depart = json.loads(requestWrapper(get_node_by_id.format(node_id=path["chemin"][0]["node1"])))
                            depart_syn = json.loads(requestWrapper(get_node_by_id.format(node_id=path["chemin"][0]["node2"])))
                            but = json.loads(requestWrapper(get_node_by_id.format(node_id=path["chemin"][2]["node1"])))
                            but_syn = json.loads(requestWrapper(get_node_by_id.format(node_id=path["chemin"][2]["node2"])))
                            print(path["chemin"][2])
                            print(f"{depart_syn["name"]} est un synomyne de {depart["name"]} , {but_syn["name"]} est un synonyme de {but["name"]} et nous avons {depart_syn["name"]} {relationCible} {but_syn["name"]}")
            
                        return resultats[:10]
                
            except Exception as e:
                continue
    

    resultats = sorted(resultats, key=lambda x: x["w"], reverse=True)

    if(len(resultats) >= 10):
        return resultats[:10]       
                 
    return resultats;

def callFromDiscordCarre(input_text):
    li = re.split(r"(\sr_.+\s)", input_text)
    if len(li) == 3:
        node1 = li[0].strip()
        node2 = li[2].strip()
        relation = li[1].strip()
        print(f"node1: {node1}, node2: {node2}, relation: {relation}")
        res = carre(li[0],li[1],li[2])
        return res


cacheFile = open("cache.json", "r")
cache = json.load(cacheFile)
cacheFile.close()
if __name__ == "__main__":
   callFromDiscordCarre("chat r_agent-1 sauter")