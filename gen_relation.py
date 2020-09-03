import bz2
import csv
import json
import argparse
from tqdm import tqdm
from core_wikidata import *

def dfs(G, startNode, csvwriter, relation):
    for targetNode in G.neighbors(startNode):
        writer.writerow([targetNode, startNode, relation])
        if(nodeState[targetNode]==0):
            dfs_visit(G, targetNode, csvwriter, relation)

def dfs_visit(G, startNode, csvwriter, relation):
    nodeState[startNode] = 1
    if startNode in G:
        for targetNode in G.neighbors(startNode):
            writer.writerow([targetNode, startNode, relation])
            if nodeState[targetNode]==0:
                dfs_visit(G, targetNode, csvwriter, relation)
                
    nodeState[startNode] = 2
    global nodesCleared
    nodesCleared += 1
    if nodesCleared%1000000==0:
        print(f"Nodes cleared: {nodesCleared}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=__doc__
    )

    parser.add_argument(
        '-wd',
        '--wikidata_filePATH',
        help=(
            'give the file path of extracted wikidata page(jsonline).'
        )
    )

    parser.add_argument(
        '-wdidx',
        '--wikidataIndex_filePath',
        help=(
            'give the file path of wikidata pagenumber(QXXX)-engtitle.'
        )
    )

    parser.add_argument(
        '-o',
        '--output_PATH',
        help=(
            'give the path where output files should locate.'
        )
    )

    args = parser.parse_args()

    ###########  Start building graph  ###########

    wikidata = Wikidata(wikidata_filePATH=arg.wikidata_filePATH,
                        wikidataIndex_filePath=arg.wikidataIndex_filePath,
                        line_count=59189275)
    nodeState = defaultdict(lambda: 0)
    nodesCleared = 0

    ##############################################

    # Generate relation: instance
    print("Generating: table-relation-instance.csv")
    csvfile = open(os.path.join(args.output_PATH, "table-relation-instance.csv"), 'w', newline='')
    writer = csv.writer(csvfile)
    dfs(wikidata.graph, 'Q35120', writer, 'instance')
    csvfile.close()

    # Generate relation: subclass
    print("Generating: table-relation-subclass.csv")
    csvfile = open(os.path.join(args.output_PATH, "table-relation-subclass.csv"), 'w', newline='')
    writer = csv.writer(csvfile)
    dfs(wikidata.graph, 'Q35120', writer, 'subclass')
    csvfile.close()

    # Generate relation: instance without subclass
    # 把 subclass 中被誤認為 instance 的丟掉
    subclassSet = set()
    with open(os.path.join(args.output_PATH, "table-relation.csv"), newline='') as csvfile:
        rows = csv.reader(csvfile)
        for row in rows:
            subclassSet.add((row[0], row[1]))

    ###################################

    csvfile = open(os.path.join(args.output_PATH, "table-relation-instanceNoSubclass.csv"), 'w', newline='')
    writer  = csv.writer(csvfile)
    writer.writerow(["source", "target", "relation"])

    subclassCaught = 0
    with open(os.path.join(args.output_PATH, "table-relation-instance.csv"), newline='') as csvfile:
        rows = csv.reader(csvfile)
        for line_num, row in enumerate(rows):
            if line_num % 1000000 == 0:
                print("Line:", line_num)
            if (row[0], row[1]) in subclassSet:
                subclassCaught += 1
            else:
                writer.writerow(row)

    csvfile.close()