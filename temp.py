# https://jdm-api.demo.lirmm.fr/schema
import requests
import json
import networkx as nx
import matplotlib.pyplot as plt
link_api ="https://jdm-api.demo.lirmm.fr/schema"
api_get_node_by_name = "https://jdm-api.demo.lirmm.fr/v0/node_by_name/{node_name}"
get_relation_from ="https://jdm-api.demo.lirmm.fr/v0/relations/from/{node1_name}"
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
    "r_agentive_role": 38,
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
    "r_der_morpho": 85,
    "r_has_auteur": 86,
    "r_has_personnage": 87,
    "r_can_eat": 88,
    "r_has_actors": 89,
    "r_deplac_mode": 90,
    "r_has_interpret": 91,
    "r_has_color": 92,
    "r_has_cible": 93,
    "r_has_symptomes": 94,
    "r_has_predecesseur-time": 95,
    "r_has_diagnostic": 96,
    "r_has_predecesseur-space": 97,
    "r_has_successeur-space": 98,
    "r_has_social_tie_with": 99,
    "r_tributary": 100,
    "r_sentiment-1": 101,
    "r_linked-with": 102,
    "r_foncteur": 103,
    "r_comparison": 104,
    "r_but": 105,
    "r_but-1": 106,
    "r_own": 107,
    "r_own-1": 108,
    "r_verb_aux": 109,
    "r_predecesseur-logic": 110,
    "r_successeur-logic": 111,
    "r_isa-incompatible": 112,
    "r_incompatible": 113,
    "r_node2relnode-in": 114,
    "r_require": 115,
    "r_is_instance_of": 116,
    "r_is_concerned_by": 117,
    "r_symptomes-1": 118,
    "r_units": 119,
    "r_promote": 120,
    "r_circumstances": 121,
    "r_has_auteur-1": 122,
    "r_processus>agent-1": 123,
    "r_processus>patient-1": 124,
    "r_processus>instr-1": 125,
    "r_node2relnode-out": 126,
    "r_carac_nominale": 127,
    "r_has_topic": 128,
    "r_pourvoyeur": 129,
    "r_compl_agent": 130,
    "r_has_beneficiaire": 131,
    "r_descend_de": 132,
    "r_domain_subst": 133,
    "r_has_prop": 134,
    "r_activ_voice": 135,
    "r_make_use_of": 136,
    "r_is_used_by": 137,
    "r_adj-nomprop": 138,
    "r_nomprop-adj": 139,
    "r_adj-adv": 140,
    "r_adv-adj": 141,
    "r_homophone": 142,
    "r_potential_confusion_with": 143,
    "r_concerning": 144,
    "r_adj>nom": 145,
    "r_nom>adj": 146,
    "r_opinion_of": 147,
    "r_has_value": 148,
    "r_has_value>": 149,
    "r_has_value<": 150,
    "r_sing_form": 151,
    "r_lieu>origine": 152,
    "r_depict": 153,
    "r_has_prop-1": 154,
    "r_quantificateur-1": 155,
    "r_promote-1": 156,
    "r_context": 157,
    "r_pos_seq": 158,
    "r_translation": 159,
    "r_link": 160,
    "r_cooccurrence": 161,
    "r_aki": 162,
    "r_wiki": 163,
    "r_annotation_exception": 164,
    "r_annotation": 165,
    "r_inhib": 166,
    "r_prev": 167,
    "r_succ": 168,
    "r_termgroup": 169,
    "r_raff_sem-1": 170,
    "r_learning_model": 171
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
    38: "r_agentive_role",
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
    85: "r_der_morpho",
    86: "r_has_auteur",
    87: "r_has_personnage",
    88: "r_can_eat",
    89: "r_has_actors",
    90: "r_deplac_mode",
    91: "r_has_interpret",
    92: "r_has_color",
    93: "r_has_cible",
    94: "r_has_symptomes",
    95: "r_has_predecesseur-time",
    96: "r_has_diagnostic",
    97: "r_has_predecesseur-space",
    98: "r_has_successeur-space",
    99: "r_has_social_tie_with",
    100: "r_tributary",
    101: "r_sentiment-1",
    102: "r_linked-with",
    103: "r_foncteur",
    104: "r_comparison",
    105: "r_but",
    106: "r_but-1",
    107: "r_own",
    108: "r_own-1",
    109: "r_verb_aux",
    110: "r_predecesseur-logic",
    111: "r_successeur-logic",
    112: "r_isa-incompatible",
    113: "r_incompatible",
    114: "r_node2relnode-in",
    115: "r_require",
    116: "r_is_instance_of",
    117: "r_is_concerned_by",
    118: "r_symptomes-1",
    119: "r_units",
    120: "r_promote",
    121: "r_circumstances",
    122: "r_has_auteur-1",
    123: "r_processus>agent-1",
    124: "r_processus>patient-1",
    125: "r_processus>instr-1",
    126: "r_node2relnode-out",
    127: "r_carac_nominale",
    128: "r_has_topic",
    129: "r_pourvoyeur",
    130: "r_compl_agent",
    131: "r_has_beneficiaire",
    132: "r_descend_de",
    133: "r_domain_subst",
    134: "r_has_prop",
    135: "r_activ_voice",
    136: "r_make_use_of",
    137: "r_is_used_by",
    138: "r_adj-nomprop",
    139: "r_nomprop-adj",
    140: "r_adj-adv",
    141: "r_adv-adj",
    142: "r_homophone",
    143: "r_potential_confusion_with",
    144: "r_concerning",
    145: "r_adj>nom",
    146: "r_nom>adj",
    147: "r_opinion_of",
    148: "r_has_value",
    149: "r_has_value>",
    150: "r_has_value<",
    151: "r_sing_form",
    152: "r_lieu>origine",
    153: "r_depict",
    154: "r_has_prop-1",
    155: "r_quantificateur-1",
    156: "r_promote-1",
    157: "r_context",
    158: "r_pos_seq",
    159: "r_translation",
    160: "r_link",
    161: "r_cooccurrence",
    162: "r_aki",
    163: "r_wiki",
    164: "r_annotation_exception",
    165: "r_annotation",
    166: "r_inhib",
    167: "r_prev",
    168: "r_succ",
    169: "r_termgroup",
    170: "r_raff_sem-1",
    171: "r_learning_model"
}

def translate_relationNBtoNOM(relation):
    if relation in nombre_a_nom.keys():
        return nombre_a_nom[relation]
    return "Unknown"


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
    def printTriangles(self, node1, node2):
        for edge in self.edges:
            if edge[0] == node1:
                for edge2 in self.edges:
                    if edge2[0] == edge[1] and edge2[1] == node2:
                        print(f"Triangle: {self.nodes[node1]} -> {edge[2]}->{self.nodes[edge[1]]} -> {edge2[2]} -> {self.nodes[node2]}")


"""node1= "chat"
node2 = "calin"
response = requests.get(get_relation_between.format(node1_name=node1, node2_name=node2))
print(response.status_code)
print(response.text)"""
def create_graph(node1_data, node2_data, relation):
    graph = Graph()
    graph.add_node(node1_data["id"], node1_data["name"])
    graph.add_node(node2_data["id"], node2_data["name"])

    li_relation = requestWrapper(get_relation_from.format(node1_name=node1_data["name"]))
    li_relation = json.loads(li_relation)
    for relation in li_relation["relations"]:
        node2Id = relation["node2"]
        node2 = None
        for node in li_relation["nodes"]:
            if node["id"] == node2Id:
                node2 = node
        if node2 is not None and abs(relation["w"]) > 70 and (relation["type"] == 6 or relation["type"] == 8):
            li_relation2 = requestWrapper(get_relation_between.format(node1_name=node2["name"], node2_name=node2_data["name"]))
            li_relation2 = json.loads(li_relation2)
            if "relations" in li_relation2:
                for rel in li_relation2["relations"]:
                    graph.add_node(node2["id"], node2["name"])
                    graph.add_edge(node1_data["id"], node2["id"], translate_relationNBtoNOM(relation["type"]), relation["w"])
                    graph.add_edge(node2["id"], node2_data["id"], translate_relationNBtoNOM(rel["type"]), rel["w"])

    graph.printTriangles(node1_data["id"], node2_data["id"])
#chat r_isa-1 animal
#pigeon r_agent-1 voler
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
            node2_data = getNodeByName(node2)
            create_graph(node1_data, node2_data, relation)
