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
    nom = "Unknown"
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
    # chemin = list of dict
    inf_lst = ast.literal_eval(inf)
    res = ""
    i = 0
    annotation_added = False
    
    for e in chemin:
        if "annotation" in e and not annotation_added:
            res += e["annotation"] + " : "
            annotation_added = True
        
        res += e["name"]

        if i < len(inf_lst):
            res += " -> " + str(inf_lst[i])
            i += 1
        
        if i < len(inf_lst) or e != chemin[-1]:
            res += " -> "

    return res

def directRelation(node1, node2, wanted_relation):
    li_relation = requestWrapper(get_relation_between.format(
        node1_name=node1["name"], node2_name=node2["name"]))
    li_relation = json.loads(li_relation)
    li_relation["relations"] = [
        relation for relation in li_relation["relations"] if relation["type"] == wanted_relation]
    return li_relation

def get_refinements(term, relation_type='r_raff_sem'):
    url = f"https://jdm-api.demo.lirmm.fr/v0/refinements/{term}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"API request failed with status code {response.status_code}")
        return None

def check_isa_relation_with_refinements(node1, node2):
    """check if a isa relation is valid using reff

    Args:
        node1 (string): name of node 1
        node2 (string): name of node 1

    Returns:
        boolean: is the isa relation valid
    """
    # Get the refinements for node1
    refinements_node_1 = get_refinements(node1)
    refinements_node_2 = get_refinements(node2)

    if refinements_node_1 and refinements_node_2:
        li_already_seen = []
        for refs in refinements_node_1["nodes"]:
            li_already_seen.append(refs["id"])
        for refs in refinements_node_2["nodes"]:
            if refs["id"] in li_already_seen:
                # On a trouvé un raff commun entre node1 et node2
                return True
    # Si on n'a pas trouvé de raffinement commun, on retourne False
    return False

def update_poids_chemin(poids_chemin, inference_courante, chemin, relation, annotation_name, new_chemin):
    """
    Updates the poids_chemin dictionary with the new weight for the given chemin.

    Args:
        poids_chemin (dict): Dictionary containing chemin weights.
        inference_courante (str): Current inference as a string.
        chemin (list): Current chemin (path).
        relation (dict): Relation dictionary containing weight information.
        annotation_name (str): Annotation name for the relation.
        new_chemin (list): New chemin to update the weight for.
    """
    key = tuple_chemin_to_hasahtable(inference_courante, chemin)
    if key in poids_chemin:
        ancien_poids = poids_chemin[key]
        taille_ancienChemin = len(chemin)
        log_ancien_poids = math.log(ancien_poids)
        ancien_poids_sum = log_ancien_poids * taille_ancienChemin

        fact = 1 if relation["w"] > 0 else -1
        if relation["w"] != 0:
            nouveau_poids = math.exp(
                (ancien_poids_sum + (fact * math.log(abs(relation["w"])))) / (taille_ancienChemin + 1)
            )
        else:
            nouveau_poids = 0

        print("ancien poids : ", nouveau_poids)
        nouveau_poids = gestion_poids(annotation_name, nouveau_poids)
        print("nouveau poids : ", nouveau_poids)

        poids_chemin[tuple_chemin_to_hasahtable(inference_courante, new_chemin)] = nouveau_poids
    else:
        print(f"Warning: Key {key} not found in poids_chemin. This should never happen")

def traiter_relation(relation, dico_name, annotation_name, i, inference_courante_list, node2_data, chemin, chemins, poids_chemin, inference_courante):
    """
    Processes a relation and updates the chemins and poids_chemin dictionaries.

    Args:
        relation (dict): The relation being processed.
        dico_name (dict): Dictionary mapping node IDs to node data.
        annotation_name (str): Annotation name for the relation.
        i (int): Current index in the inference list.
        inference_courante_list (list): Current inference as a list.
        node2_data (dict): Data of the target node.
        chemin (list): Current chemin (path).
        chemins (dict): Dictionary of chemins for each inference type.
        poids_chemin (dict): Dictionary of chemin weights.
        inference_courante (str): Current inference as a string.
    """
    # Retrieve the destination node
    node2Id = relation["node2"]
    node2 = {}
    if node2Id in dico_name:
        node2 = dico_name[node2Id]
    node2["annotation"] = annotation_name
                            
    # If the relation is of type "r_isa" we want to check the reffinement to see if the relation is indeed valid
    if(inference_courante_list[i] != "r_isa" or check_isa_relation_with_refinements(chemin[i]["name"], node2["name"])):

        # Check if the destination node matches the inference criteria
        if ((i + 1 == len(inference_courante_list) and node2["id"] == node2_data["id"]) or i + 1 != len(inference_courante_list)):
            # Continue the current path with the found node
            new_chemin = chemin + [node2]
            # Add this path to the list of possible paths
            chemins[str(inference_courante_list)].append(new_chemin)
            # Update the weight of the current path in the poids_chemin dictionary
            update_poids_chemin(
                poids_chemin,
                inference_courante,
                chemin,
                relation,
                annotation_name,
                new_chemin
            )

def afficher_chemins_et_poids(chemins, poids_chemin):
    """
    Formats and returns the paths and their weights.

    Args:
        chemins (dict): Dictionary of paths for each inference type.
        poids_chemin (dict): Dictionary of chemin weights.

    Returns:
        str: Formatted string of paths and their weights.
    """
    res = ""
    for (inference_courante, chemin_inf) in chemins.items():
        inf_lst = ast.literal_eval(inference_courante)
        for chemin in chemin_inf:
            if len(chemin) == len(inf_lst) + 1:
                for i in range(len(inf_lst)):
                    res += chemin[i]["name"] + " -> " + inf_lst[i] + " -> "
                    if i + 1 == len(inf_lst):
                        res += chemin[i + 1]["name"]
                res += " : " + str(poids_chemin[tuple_chemin_to_hasahtable(
                    inference_courante, chemin)]) + "\n"
    return res

def get_parsable_output(chemins, poids_chemin):
    """
    Formats and returns the paths and their weights.

    Args:
        chemins (dict): Dictionary of paths for each inference type.
        poids_chemin (dict): Dictionary of chemin weights.

    Returns:
        list of dict: List of dictionaries containing paths and their weights.
    """
    res = []
    for (inference_courante, chemin_inf) in chemins.items():
        inf_lst = ast.literal_eval(inference_courante)
        for chemin in chemin_inf:
            if len(chemin) == len(inf_lst) + 1:
                chemin_dict = {}
                chemin_dict["inference"] = inference_courante
                chemin_dict["chemin"] = []
                for i in range(len(chemin)):
                    chemin_dict["chemin"].append(chemin[i]["name"])
                chemin_dict["poids"] = poids_chemin[tuple_chemin_to_hasahtable(
                    inference_courante, chemin)]
                res.append(chemin_dict)
    return res

def traiter_relation_et_annotation(relation, dico_name, i, inference_courante_list, node2_data, chemin, chemins, poids_chemin, inference_courante, get_relation_from):
    """
    Handles the annotation extraction and processes the relation.

    Args:
        relation (dict): The relation being processed.
        dico_name (dict): Dictionary mapping node IDs to node data.
        i (int): Current index in the inference list.
        inference_courante_list (list): Current inference as a list.
        node2_data (dict): Data of the target node.
        chemin (list): Current chemin (path).
        chemins (dict): Dictionary of chemins for each inference type.
        poids_chemin (dict): Dictionary of chemin weights.
        inference_courante (str): Current inference as a string.
        get_relation_from (str): API endpoint to fetch relations.
    """
    annot = ":r" + str(relation["id"])
    li_relation_for_annotation = requestWrapper(get_relation_from.format(node1_name=annot))
    li_relation_for_annotation = json.loads(li_relation_for_annotation)
    annotation_name = "Pas d'annotation"
    li_annotation = []
    dico_name_annot = {}

    if "relations" in li_relation_for_annotation:
        for relation_annot in li_relation_for_annotation["relations"]:
            if relation_annot["type"] == HelperJDM.nom_a_nombre['r_annotation']:
                li_annotation.append(relation_annot)
        for node in li_relation_for_annotation["nodes"]:
            dico_name_annot[node["id"]] = node

    if len(li_annotation) > 0:
        li_annotation = sorted(li_annotation, key=lambda x: x["w"], reverse=True)
        annotation = li_annotation[0]["node2"]
        if annotation in dico_name_annot:
            annotation_name = dico_name_annot[annotation]["name"]
        else:
            annotation_name = "Pas d'annotation"

    traiter_relation(
        relation,
        dico_name,
        annotation_name,
        i,
        inference_courante_list,
        node2_data,
        chemin,
        chemins,
        poids_chemin,
        inference_courante
    )

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
                        
                        ################### Trie des relations ###################
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
                            li_relation["relations"] = li_relation["relations"][:5]
                        else:
                            li_relation["relations"] = li_relation["relations"][:50]
                        ############# Gestion des annotations #############
                        # on recupere les annotations des relations
                        for relation in li_relation["relations"]:
                            traiter_relation_et_annotation(
                                relation,
                                dico_name,
                                i,
                                inference_courante_list,
                                node2_data,
                                chemin,
                                chemins,
                                poids_chemin,
                                inference_courante,
                                get_relation_from
                            )
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
        #si on a plus de 20 chemins, definie un seuil pour garder les 20 chemins avec les meilleurs scores
        #sauf pour la derniere boulce, on ne garde que les 10 dernier
        # sauf pour la dernière boucle, on ne garde que les 10 derniers
        limite = 20
        if not i < max_size: 
            limite = 10
        if(len(li_poids_a_trier) >= limite):
            li_poids_a_trier.sort()
            seuil = li_poids_a_trier[-limite]
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
    
    return chemins, poids_chemin

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
        chemins, poids_chemin = create_graphGen(node1_data, node2_data,
                              ast.literal_eval(li_infer), relation)
        res = afficher_chemins_et_poids(chemins, poids_chemin)
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

def gestion_poids(annotation_name, poids):
    annotation_weights = {
    "toujours vrai": 1.3,
    "impossible": 0.5,
    "pertinent": 1.2,
    "non pertinent": 0.8,
    "improbable": 0.8,
    "fréquent": 1.1,
    "rare": 0.9
    }
    for key, coef in annotation_weights.items():
        if key == annotation_name:
            poids *= coef
    if poids > 1:
        poids = 1
    return poids


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
            chemins, poids_chemin = create_graphGen(node1_data, node2_data,
                            ast.literal_eval(li_infer), relation)
            res = get_parsable_output(chemins, poids_chemin)
            print("-------------------Result-----------------------")
            print(res)
            print("------------------Please stay indoors--------------------")
            #cacheFile = open("cache.json", "w")
            #cacheFile.write(json.dumps(cache))
