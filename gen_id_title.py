import bz2
import csv
import json
import argparse
from tqdm import tqdm

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
        '-o',
        '--output_PATH',
        help=(
            'give the path where output files should locate.'
        )
    )

    args = parser.parse_args()

    # Generate table - id, enTitle
    csvfile = open(os.path.join(args.output_PATH, 'table-id-title.csv'), 'w', newline='')
    writer = csv.writer(csvfile)
    writer.writerow(['id, enTitle'])

    with bz2.open(args.wikidata_filePATH, 'r') as json_file:
        for line in tqdm(json_file, total=80000000):
            data = json.loads(line)
            wdID = data['id']

            enTitle = data['labels']['en']
            zhhantTitle = data['labels']['zh-hant']
            zhhansTitle = data['labels']['zh-hans']
            writer.writerow([f"{wdID}\t{enTitle}\t{zhhantTitle}\t{zhhansTitle}"])
    csvfile.close()