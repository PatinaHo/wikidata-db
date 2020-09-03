import os
import csv, json
import psycopg2
import nltk
from tqdm import tqdm
from nltk.corpus import wordnet as wn

SERVER_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DIRECTORY_ROOT = os.getcwd()

conn = psycopg2.connect(database="wikidata", user="", password="", host="localhost", port="5432")
cur = conn.cursor()


def wd_title(wdid):
    cur.execute(f"""SELECT entitle FROM title_table WHERE wdid='{wdid}';""")
    offset_list = cur.fetchall()
    return offset_list[0][0]


def wd_hyponym(wdid):
    """ Get 1 layer of hyponym, which means other wikidata item having "subclassOf" with input wdid.
    Input: 
        wdid(str): wikidata ID.
    Output: 
        offset_list(list): [(id, entitle), ...]
    """

    cur.execute(f"""SELECT re.sourceid, tt.entitle
                    FROM relation_table AS re INNER JOIN title_table AS tt on re.sourceid=tt.wdid
                    WHERE targetid='{wdid}' AND relation='subclass';
                 """)
    offset_list = cur.fetchall()
    return offset_list


def wd_hypernym(wdid):
    """ Get 1 layer of hypernym, which means input wdid's "subclassOf" item.
    Input: 
        wdid(str): wikidata ID.
    Output: 
        offset_list(list): [(id, entitle), ...]
    """

    if wdid=='Q35120':
        return []
    cur.execute(f"""SELECT re.targetid, tt.entitle
                    FROM relation_table AS re INNER JOIN title_table AS tt ON re.targetid=tt.wdid 
                    WHERE sourceid='{wdid}';
                 """)
    offset_list = cur.fetchall()
    return offset_list


def wd_hypernym_multilayer(wdid, maxRecur, recur=0):
    """ Get multiple layers of hypernym (ancestors).
    Input: 
        wdid(str): wikidata ID.
        maxRecur:  layers of ancestors.
    Output: 
        offset_list(set): {id, id, ...}
    """
    result = []
    if recur==maxRecur:
        return result
    parentids = [item[0] for item in wd_hypernym(wdid) if item[0]]
    result = [item[1] for item in wd_hypernym(wdid) if item[1]]
    for parent in parentids:
        result += wd_hypernym_multilayer(parent, maxRecur, recur+1)
    return set(result)


def wd_sister(wdid):
    """ Get sisters, which means all hypernyms of input wdid's parents.
    Input: 
        wdid(str): wikidata ID.
    Output: 
        offset_list(set): {id, id, ...}
    """
    result = []
    parentsid = [item[0] for item in wd_hypernym(wdid) if item[0]]
    for parent in parentsid:
        sisters = [item[1] for item in wd_hyponym(parent) if item[1]]
        result += sisters
    result.append(wd_title(wdid))
    return set(result)
