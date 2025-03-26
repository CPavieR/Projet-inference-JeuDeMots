# https://jdm-api.demo.lirmm.fr/schema
import math
import requests
import json
import re
import ast
import copy
from lib_helpers import HelperJDM
import requests_cache
link_api = "https://jdm-api.demo.lirmm.fr/schema"
api_get_node_by_name = "https://jdm-api.demo.lirmm.fr/v0/node_by_name/{node_name}"
get_relation_from = "https://jdm-api.demo.lirmm.fr/v0/relations/from/{node1_name}"
get_relation_between = "https://jdm-api.demo.lirmm.fr/v0/relations/from/{node1_name}/to/{node2_name}"
get_node_by_id = "https://jdm-api.demo.lirmm.fr/v0/node_by_id/{node_id}"
cache = {}

requests_cache.install_cache('jdm_cache', backend='sqlite', expire_after=None)
session = requests.Session()
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


def getNodeByName(node_name):
    jsonString = requestWrapper(
        api_get_node_by_name.format(node_name=node_name))
    return json.loads(jsonString)


def tuple_chemin_to_hasahtable(inf, chemin):
    # inf = list of string
    # chemin_tuple = lst of dict
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

def directRelation(node1, node2, wanted_relation):
    li_relation = requestWrapper(get_relation_between.format(
        node1_name=node1["name"], node2_name=node2["name"]))
    li_relation = json.loads(li_relation)
    li_relation["relations"] = [
        relation for relation in li_relation["relations"] if relation["type"] == wanted_relation]
    return li_relation

def create_graphGen(node1_data, node2_data, li_Inference, wanted_relation):
    # On initialise le graphe avec neoud de depart et objectif
    # li_inference = liste de type d'inference, par exemple : [["r_isa", "{r_cible}"],["r_hypo", "{r_cible}"],["r_syn", "{r_cible}"],["{r_cible}", "r_syn"]]
    # on recupère la taille de la l'inference la plus grande pour savoir le nombre de bouble a faire
    max_size = max([len(inf) for inf in li_Inference])
    # on initialise un dico associant chaque type d'inference à une liste de chemins possibles
    chemins = {str(inf): [[node1_data]] for inf in li_Inference}
    poids_chemin = {}
    # on initialise le poids de chaque chemin à 0
    for (inference_courante, chemins_par_type_inf) in chemins.items():
        for chemin in chemins_par_type_inf:
            poids_chemin[tuple_chemin_to_hasahtable(
                inference_courante, chemin)] = 1
    # on boucle sur la longueur de chaque type d'inférence
    i = 0
    while i < max_size:
        # on fait une deepcopie des chemins pour pouvoir les modifier
        chemins_copy = copy.deepcopy(chemins)
        # on boucle sur chaque type d'inférence
        for (inference_courante, liste_chemins_inference_courante) in chemins_copy.items():
            # on boucle pour chemin possible
            for chemin in liste_chemins_inference_courante:
                # on convertie l'inférence courante de string à liste
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
                        #On enlève les relations qui ont un node2 qui commence par "::" (relation interne ?)
                        dico_name = {}
                        for node in li_relation["nodes"]:
                            dico_name[node["id"]] = node
                        
                        li_relation["relations"] = [
                            relation for relation in li_relation["relations"] if relation["node2"] in dico_name and not dico_name[relation["node2"]]["name"].startswith("::")]
                        
                       # on normalise les poids
                        HelperJDM.normalize(li_relation["relations"])
                        # on trie les relations par poids
                        li_relation["relations"] = sorted(
                            li_relation["relations"], key=lambda x: x["w"], reverse=True)
                        # Si on est pas à la fin du chemin, on ne garde que les 5 premières relations
                        # dans le cas opposé on garde tout pour éviter d'échoué le chemin
                        if (i+1 != len(inference_courante_list)):
                            li_relation["relations"] = li_relation["relations"][:20]
                        # pour chaque relation qui ont passées le filtre
                        for relation in li_relation["relations"]:
                            # on recupere le noeud de destination
                            node2Id = relation["node2"]
                            node2=None
                            if node2Id in dico_name:
                                node2 = dico_name[node2Id]
                            # si le noeud final du type d'inference, on veut que celui ci soit le noeud de destination, sinon on s'en fiche
                            if ((i+1 == len(inference_courante_list) and node2["id"] == node2_data["id"]) or i+1 != len(inference_courante_list)):
                                # on continue le chemin courant avec le noeud que l'ont vient de trouver
                                new_chemin = chemin + [node2]
                                # on ajoute ce chemin à la liste des chemins possibles
                                chemins[str(inference_courante_list)
                                        ].append(new_chemin)
                                print(tuple_chemin_to_hasahtable(
                                    inference_courante, new_chemin))
                                # On ajoute le poids du chemin courant au dico des poids
                                if tuple_chemin_to_hasahtable(inference_courante, chemin) in poids_chemin:
                                    ancien_poids = poids_chemin[tuple_chemin_to_hasahtable(
                                        inference_courante, chemin)]
                                    taille_ancienChemin = len(chemin)
                                    log_ancien_poids = math.log(ancien_poids)
                                    ancien_poids_sum = log_ancien_poids*taille_ancienChemin
                                    if(relation["w"]>0):
                                        fact = 1
                                    else:
                                        fact = -1
                                    if (relation["w"]!=0):
                                        nouveau_poids = math.exp((ancien_poids_sum+(fact*math.log(abs(relation["w"]))))/(taille_ancienChemin+1))
                                    else:
                                        nouveau_poids = 0
                                    poids_chemin[tuple_chemin_to_hasahtable(inference_courante, new_chemin)] = nouveau_poids
                                    
                                else:
                                    print(
                                        f"Warning: Key {tuple_chemin_to_hasahtable(inference_courante, chemin)} not found in poids_chemin.")
                    except Exception as e:
                        print("Exception : ", e)
        # on supprime les chemins qui ont un poids trop faible
        #on copie les chemins pour pouvoir les modifier
        chemins_copy = copy.deepcopy(chemins)
        #on initialise une liste des poids à trier correspondant aux poids des chemins valides (cad qui soit sont terminé, soit qui sont en cours de construction)
        li_poids_a_trier = []
        for (inference_courante, liste_chemins_inference_courante) in chemins_copy.items():
            for chemin in liste_chemins_inference_courante:
                #si le chemin est terminé ou alors on continue de le construire
                if (chemin[-1]["id"] == node2_data["id"] or len(chemin) == i+2):
                    #on ajoute le poids du chemin à la liste des poids à trier
                    li_poids_a_trier.append(
                        poids_chemin[tuple_chemin_to_hasahtable(inference_courante, chemin)])
                else:
                    #sinon on supprime le chemin
                    chemins[inference_courante].remove(chemin)
                    if tuple_chemin_to_hasahtable(inference_courante, chemin) in poids_chemin:
                        poids_chemin.pop(
                            tuple_chemin_to_hasahtable(inference_courante, chemin))
        #si on a plus de 10 chemins, definie un seuil pour garder les 10 chemins avec les meilleurs scores
        if(len(li_poids_a_trier) >= 20):
            li_poids_a_trier.sort()
            seuil = li_poids_a_trier[-20]
        #si il y a moins de 10 chemins, on garde tout
        else:
            seuil= 0
        #on refait une copie des chemins pour bien prendre en compte les suppressions de la boucle précédente
        chemins_copy = copy.deepcopy(chemins)
        for (inference_courante, liste_chemins_inference_courante) in chemins_copy.items():
            for chemin in liste_chemins_inference_courante:
                #si le poids du chemin est inférieur au seuil, on supprime le chemin
                if (poids_chemin[tuple_chemin_to_hasahtable(inference_courante, chemin)] < seuil):
                    chemins[inference_courante].remove(chemin)
                    poids_chemin.pop(
                        tuple_chemin_to_hasahtable(inference_courante, chemin))
        i=i+1
        print(i)
    # On affiche les chemins et leur poids
    res = ""
    for (inference_courante, chemin_inf) in chemins.items():
        inf_lst = ast.literal_eval(inference_courante)
        for chemin in chemin_inf:
            if len(chemin) == len(inf_lst)+1:
                for i in range(len(inf_lst)):
                    res = res+chemin[i]["name"] + " -> " + inf_lst[i] + " -> "
                    if i+1 == len(inf_lst):
                        res = res+chemin[i+1]["name"]
                # (inf + " : " + chemin)
                res = res+" : " + \
                    str(poids_chemin[tuple_chemin_to_hasahtable(
                        inference_courante, chemin)])+"\n"
    # for (inf, chemin_ind) in chemins.items():
        # for chemin in chemin_ind:
            # print(str(inf) + " : " + str(chemin))
        # print(poids_chemin[(inf, chemin)])
    return res

# chat r_isa animal
# chat r_agent-1 miauler
# pigeon r_agent-1 voler


def callFromDiscord(input_text, li_infer):
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
        li_infer = li_infer.format(
            r_cible=relation)
        res = create_graphGen(node1_data, node2_data,
                              ast.literal_eval(li_infer), relation)
        cacheFile = open("cache.json", "w")
        cacheFile.write(json.dumps(cache))
        return res


def callFromDiscordSym(input_text):
    li_infer = '[["r_syn", "{r_cible}"],["{r_cible}", "r_syn"]]'
    return callFromDiscord(input_text, li_infer)


def callFromDiscordInduc(input_text):
    li_infer = '[["r_isa", "{r_cible}"],["r_hypo", "{r_cible}"]]'
    return callFromDiscord(input_text, li_infer)


def callFromDiscordAll(input_text):
    li_infer = '[["r_isa", "{r_cible}"],["r_hypo", "{r_cible}"],["r_syn", "{r_cible}"],["{r_cible}", "r_syn"]]'
    return callFromDiscord(input_text, li_infer)


"""cacheFile = open("cache.json", "r")
cache = json.load(cacheFile)
cacheFile.close()"""
if __name__ == "__main__":
    while True:
        input_text = input(
            "entrer une relation entre deux mots:(exit pour quitter) ")
        if input_text == "exit":
            break
        li = re.split(r"(\sr_[^\s]+\s)", input_text)
        if len(li) == 3:
            node1 = li[0].strip()
            node2 = li[2].strip()
            relation = li[1].strip()
            print(f"node1: {node1}, node2: {node2}, relation: {relation}")
            # print node1 id
            node1_data = getNodeByName(node1)
            # r_syn       ,["{r_cible}", "r_syn"],["r_syn", "{r_cible}", "r_syn"],["r_syn", "{r_cible}", "r_syn"]
            node2_data = getNodeByName(node2)
            li_infer = '[["r_isa", "{r_cible}"],["r_hypo", "{r_cible}"],["r_syn", "{r_cible}"],["{r_cible}", "r_syn"],["{r_cible}"]]'.format(
                r_cible=relation)
            res = create_graphGen(node1_data, node2_data,
                            ast.literal_eval(li_infer), relation)
            print("-------------------Result-----------------------")
            print(res)
            print("------------------Please stay indoors--------------------")
            #cacheFile = open("cache.json", "w")
            #cacheFile.write(json.dumps(cache))
