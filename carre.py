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
link_api = "https://jdm-api.demo.lirmm.fr/schema"
api_get_node_by_name = "https://jdm-api.demo.lirmm.fr/v0/node_by_name/{node_name}"
get_relation_from = "https://jdm-api.demo.lirmm.fr/v0/relations/from/{node1_name}"
get_relation_between = "https://jdm-api.demo.lirmm.fr/v0/relations/from/{node1_name}/to/{node2_name}"
get_node_by_id = "https://jdm-api.demo.lirmm.fr/v0/node_by_id/{node_id}"
cache = {}

R_SYN = 5


def translate_relationNBtoNOM(relation):
    nom = "Uknown"
    try:
        nom = HelperJDM.nombre_a_nom[relation]
        return nom
    except Exception:
        return nom


def requestWrapper(url):
    global cache
    if url in cache:
        return cache[url]
    response = requests.get(url)

    cache[url] = response.text

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
        for r2 in relationsBut:
            node2_syn = json.loads(requestWrapper(get_node_by_id.format(node_id=r2["node2"])))
            if re.match("en:.*",node2_syn["name"]):
                continue
            relationsSynEntre = requestWrapper(get_relation_between.format(node1_name=node1_syn["name"],node2_name=node2_syn["name"]))
            try:
                relationsSynEntre = json.loads(relationsSynEntre)["relations"]
                relationsSouhaitees = filter_relations(relationsSynEntre,[relationCibleNumber])
                #print("R1 :", r1)
               # print("R2 :",r2)
               # print(relationsSouhaitees)
                for r in relationsSouhaitees:
                    # Reflechir comment gerer les relations a poids negatifs

                   
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
                        print(poids)
                    except Exception as e:
                        print(e)
                    
                    resultats.append({"chemin":chemin_courant,"w":poids})
                
            except Exception as e:
                continue
    
    # goal : faire un carre en legende
    

    for r in resultats:
        if(r["w"] < 0): continue
        n1 = json.loads(requestWrapper(get_node_by_id.format(node_id=r["chemin"][0]["node2"])))
        n2 = json.loads(requestWrapper(get_node_by_id.format(node_id=r["chemin"][1]["node2"])))
        chemin_courant = "{} -> r_syn -> {}, {} -> r_syn -> {} , {} -> {} -> {}".format(
nodeDepart["name"], n1["name"], nodeBut["name"], n2["name"], n1["name"], relationCible, n2["name"]
)
        print(chemin_courant)

    
    print(resultats)     
    return resultats;




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
            # algo carre
            carre(li[0],li[1],li[2])
            cacheFile = open("cache.json", "w")
            cacheFile.write(json.dumps(cache))