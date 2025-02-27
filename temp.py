# https://jdm-api.demo.lirmm.fr/schema
import requests
import json
import re
import ast
import copy
link_api = "https://jdm-api.demo.lirmm.fr/schema"
api_get_node_by_name = "https://jdm-api.demo.lirmm.fr/v0/node_by_name/{node_name}"
get_relation_from = "https://jdm-api.demo.lirmm.fr/v0/relations/from/{node1_name}"
get_relation_between = "https://jdm-api.demo.lirmm.fr/v0/relations/from/{node1_name}/to/{node2_name}"
get_node_by_id = "https://jdm-api.demo.lirmm.fr/v0/node_by_id/{node_id}"
nom_a_nombre = {
    "r_associated": 0,
    "r_raff_sem": 1,
    "r_raff_morpho": 2,
    "r_domain": 3,
    "r_pos": 4,
    "r_syn": 5,
    "r_isa": 6,
    "r_anto": 7,
    "r_hypo": 8,
    "r_has_part": 9,
    "r_holo": 10,
    "r_locution": 11,
    "r_flpot": 12,
    "r_agent": 13,
    "r_patient": 14,
    "r_lieu": 15,
    "r_instr": 16,
    "r_carac": 17,
    "r_data": 18,
    "r_lemma": 19,
    "r_has_magn": 20,
    "r_has_antimagn": 21,
    "r_family": 22,
    "r_carac-1": 23,
    "r_agent-1": 24,
    "r_instr-1": 25,
    "r_patient-1": 26,
    "r_domain-1": 27,
    "r_lieu-1": 28,
    "r_chunk_pred": 29,
    "r_lieu_action": 30,
    "r_action_lieu": 31,
    "r_sentiment": 32,
    "r_error": 33,
    "r_manner": 34,
    "r_meaning/glose": 35,
    "r_infopot": 36,
    "r_telic_role": 37,
    "r_agentif_role": 38,
    "r_verbe-action": 39,
    "r_action-verbe": 40,
    "r_has_conseq": 41,
    "r_has_causatif": 42,
    "r_adj-verbe": 43,
    "r_verbe-adj": 44,
    "r_chunk_sujet": 45,
    "r_chunk_objet": 46,
    "r_chunk_loc": 47,
    "r_chunk_instr": 48,
    "r_time": 49,
    "r_object>mater": 50,
    "r_mater>object": 51,
    "r_successeur-time": 52,
    "r_make": 53,
    "r_product_of": 54,
    "r_against": 55,
    "r_against-1": 56,
    "r_implication": 57,
    "r_quantificateur": 58,
    "r_masc": 59,
    "r_fem": 60,
    "r_equiv": 61,
    "r_manner-1": 62,
    "r_agentive_implication": 63,
    "r_has_instance": 64,
    "r_verb_real": 65,
    "r_chunk_head": 66,
    "r_similar": 67,
    "r_set>item": 68,
    "r_item>set": 69,
    "r_processus>agent": 70,
    "r_variante": 71,
    "r_syn_strict": 72,
    "r_is_smaller_than": 73,
    "r_is_bigger_than": 74,
    "r_accomp": 75,
    "r_processus>patient": 76,
    "r_verb_ppas": 77,
    "r_cohypo": 78,
    "r_verb_ppre": 79,
    "r_processus>instr": 80,
    "r_pref_form": 81,
    "r_interact_with": 82,
    "r_alias": 83,
    "r_has_euphemisme": 84,
    "r_der_morpho": 99,
    "r_has_auteur": 100,
    "r_has_personnage": 101,
    "r_can_eat": 102,
    "r_has_actors": 103,
    "r_deplac_mode": 104,
    "r_has_interpret": 105,
    "r_has_color": 106,
    "r_has_cible": 107,
    "r_has_symptomes": 108,
    "r_has_predecesseur-time": 109,
    "r_has_diagnostic": 110,
    "r_has_predecesseur-space": 111,
    "r_has_successeur-space": 112,
    "r_has_social_tie_with": 113,
    "r_tributary": 114,
    "r_sentiment-1": 115,
    "r_linked-with": 116,
    "r_foncteur": 117,
    "r_comparison": 118,
    "r_but": 119,
    "r_but-1": 120,
    "r_own": 121,
    "r_own-1": 122,
    "r_verb_aux": 123,
    "r_predecesseur-logic": 124,
    "r_successeur-logic": 125,
    "r_isa-incompatible": 126,
    "r_incompatible": 127,
    "r_node2relnode-in": 128,
    "r_require": 129,
    "r_is_instance_of": 130,
    "r_is_concerned_by": 131,
    "r_symptomes-1": 132,
    "r_units": 133,
    "r_promote": 134,
    "r_circumstances": 135,
    "r_has_auteur-1": 136,
    "r_processus>agent-1": 137,
    "r_processus>patient-1": 138,
    "r_processus>instr-1": 139,
    "r_node2relnode-out": 140,
    "r_carac_nominale": 141,
    "r_has_topic": 142,
    "r_pourvoyeur": 148,
    "r_compl_agent": 149,
    "r_has_beneficiaire": 150,
    "r_descend_de": 151,
    "r_domain_subst": 152,
    "r_has_prop": 153,
    "r_activ_voice": 154,
    "r_make_use_of": 155,
    "r_is_used_by": 156,
    "r_adj-nomprop": 157,
    "r_nomprop-adj": 158,
    "r_adj-adv": 159,
    "r_adv-adj": 160,
    "r_homophone": 161,
    "r_potential_confusion_with": 162,
    "r_concerning": 163,
    "r_adj>nom": 164,
    "r_nom>adj": 165,
    "r_opinion_of": 166,
    "r_has_value": 167,
    "r_has_value>": 168,
    "r_has_value<": 169,
    "r_sing_form": 170,
    "r_lieu>origine": 171,
    "r_depict": 172,
    "r_has_prop-1": 173,
    "r_quantificateur-1": 174,
    "r_promote-1": 175,
    "r_context": 200,
    "r_pos_seq": 222,
    "r_translation": 333,
    "r_link": 444,
    "r_cooccurrence": 555,
    "r_aki": 666,
    "r_wiki": 777,
    "r_annotation_exception": 997,
    "r_annotation": 998,
    "r_inhib": 999,
    "r_prev": 1000,
    "r_succ": 1001,
    "r_termgroup": 1002,
    "r_raff_sem-1": 2000,
    "r_learning_model": 2001
}
nombre_a_nom = {
    0: "r_associated",
    1: "r_raff_sem",
    2: "r_raff_morpho",
    3: "r_domain",
    4: "r_pos",
    5: "r_syn",
    6: "r_isa",
    7: "r_anto",
    8: "r_hypo",
    9: "r_has_part",
    10: "r_holo",
    11: "r_locution",
    12: "r_flpot",
    13: "r_agent",
    14: "r_patient",
    15: "r_lieu",
    16: "r_instr",
    17: "r_carac",
    18: "r_data",
    19: "r_lemma",
    20: "r_has_magn",
    21: "r_has_antimagn",
    22: "r_family",
    23: "r_carac-1",
    24: "r_agent-1",
    25: "r_instr-1",
    26: "r_patient-1",
    27: "r_domain-1",
    28: "r_lieu-1",
    29: "r_chunk_pred",
    30: "r_lieu_action",
    31: "r_action_lieu",
    32: "r_sentiment",
    33: "r_error",
    34: "r_manner",
    35: "r_meaning/glose",
    36: "r_infopot",
    37: "r_telic_role",
    38: "r_agentif_role",
    39: "r_verbe-action",
    40: "r_action-verbe",
    41: "r_has_conseq",
    42: "r_has_causatif",
    43: "r_adj-verbe",
    44: "r_verbe-adj",
    45: "r_chunk_sujet",
    46: "r_chunk_objet",
    47: "r_chunk_loc",
    48: "r_chunk_instr",
    49: "r_time",
    50: "r_object>mater",
    51: "r_mater>object",
    52: "r_successeur-time",
    53: "r_make",
    54: "r_product_of",
    55: "r_against",
    56: "r_against-1",
    57: "r_implication",
    58: "r_quantificateur",
    59: "r_masc",
    60: "r_fem",
    61: "r_equiv",
    62: "r_manner-1",
    63: "r_agentive_implication",
    64: "r_has_instance",
    65: "r_verb_real",
    66: "r_chunk_head",
    67: "r_similar",
    68: "r_set>item",
    69: "r_item>set",
    70: "r_processus>agent",
    71: "r_variante",
    72: "r_syn_strict",
    73: "r_is_smaller_than",
    74: "r_is_bigger_than",
    75: "r_accomp",
    76: "r_processus>patient",
    77: "r_verb_ppas",
    78: "r_cohypo",
    79: "r_verb_ppre",
    80: "r_processus>instr",
    81: "r_pref_form",
    82: "r_interact_with",
    83: "r_alias",
    84: "r_has_euphemisme",
    99: "r_der_morpho",
    100: "r_has_auteur",
    101: "r_has_personnage",
    102: "r_can_eat",
    103: "r_has_actors",
    104: "r_deplac_mode",
    105: "r_has_interpret",
    106: "r_has_color",
    107: "r_has_cible",
    108: "r_has_symptomes",
    109: "r_has_predecesseur-time",
    110: "r_has_diagnostic",
    111: "r_has_predecesseur-space",
    112: "r_has_successeur-space",
    113: "r_has_social_tie_with",
    114: "r_tributary",
    115: "r_sentiment-1",
    116: "r_linked-with",
    117: "r_foncteur",
    118: "r_comparison",
    119: "r_but",
    120: "r_but-1",
    121: "r_own",
    122: "r_own-1",
    123: "r_verb_aux",
    124: "r_predecesseur-logic",
    125: "r_successeur-logic",
    126: "r_isa-incompatible",
    127: "r_incompatible",
    128: "r_node2relnode-in",
    129: "r_require",
    130: "r_is_instance_of",
    131: "r_is_concerned_by",
    132: "r_symptomes-1",
    133: "r_units",
    134: "r_promote",
    135: "r_circumstances",
    136: "r_has_auteur-1",
    137: "r_processus>agent-1",
    138: "r_processus>patient-1",
    139: "r_processus>instr-1",
    140: "r_node2relnode-out",
    141: "r_carac_nominale",
    142: "r_has_topic",
    148: "r_pourvoyeur",
    149: "r_compl_agent",
    150: "r_has_beneficiaire",
    151: "r_descend_de",
    152: "r_domain_subst",
    153: "r_has_prop",
    154: "r_activ_voice",
    155: "r_make_use_of",
    156: "r_is_used_by",
    157: "r_adj-nomprop",
    158: "r_nomprop-adj",
    159: "r_adj-adv",
    160: "r_adv-adj",
    161: "r_homophone",
    162: "r_potential_confusion_with",
    163: "r_concerning",
    164: "r_adj>nom",
    165: "r_nom>adj",
    166: "r_opinion_of",
    167: "r_has_value",
    168: "r_has_value>",
    169: "r_has_value<",
    170: "r_sing_form",
    171: "r_lieu>origine",
    172: "r_depict",
    173: "r_has_prop-1",
    174: "r_quantificateur-1",
    175: "r_promote-1",
    200: "r_context",
    222: "r_pos_seq",
    333: "r_translation",
    444: "r_link",
    555: "r_cooccurrence",
    666: "r_aki",
    777: "r_wiki",
    997: "r_annotation_exception",
    998: "r_annotation",
    999: "r_inhib",
    1000: "r_prev",
    1001: "r_succ",
    1002: "r_termgroup",
    2000: "r_raff_sem-1",
    2001: "r_learning_model"
}


def translate_relationNBtoNOM(relation):
    nom = "Uknown"
    try:
        nom = nombre_a_nom[relation]
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
                if (rel["type"] == nom_a_nombre[relation_wanted]):
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
        res+=(e["name"]+" -> ")
        if i < len(inf_lst):
            res+=(inf_lst[i]+" -> ")
            i+=1
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
                            relation for relation in li_relation["relations"] if relation["type"] == nom_a_nombre[inference_courante_list[i]]]
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
                if (rel["type"] == nom_a_nombre[relation_wanted]):
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


def callFromDiscordSym(input_text):
    li = input_text.split(" ")
    if len(li) == 3:
        node1 = li[0]
        node2 = li[2]
        relation = li[1]
        print(f"node1: {node1}, node2: {node2}, relation: {relation}")
        # print node1 id
        node1_data = getNodeByName(node1)
        node2_data = getNodeByName(node2)
        return create_graphSymTri(node1_data, node2_data, relation)


def callFromDiscordInduc(input_text):
    li = input_text.split(" ")
    if len(li) == 3:
        node1 = li[0]
        node2 = li[2]
        relation = li[1]
        print(f"node1: {node1}, node2: {node2}, relation: {relation}")
        # print node1 id
        node1_data = getNodeByName(node1)
        node2_data = getNodeByName(node2)
        return create_graphInducDeduc(node1_data, node2_data, relation)

def callFromDiscordAll(input_text):
    li = input_text.split(" ")
    if len(li) == 3:
        node1 = li[0]
        node2 = li[2]
        relation = li[1]
        print(f"node1: {node1}, node2: {node2}, relation: {relation}")
        # print node1 id
        node1_data = getNodeByName(node1)
        node2_data = getNodeByName(node2)
        li_infer = '[["r_isa", "{r_cible}"],["r_hypo", "{r_cible}"],["r_syn", "{r_cible}"],["{r_cible}", "r_syn"]]'.format(
                r_cible=relation)
        return create_graphGen(node1_data, node2_data,ast.literal_eval(li_infer), relation)

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
