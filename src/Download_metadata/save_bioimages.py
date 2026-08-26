from dl_metadata.api.biostudies import BioStudies
import pandas as pd
import re


bs = BioStudies()

studies_list = bs.get_all_bioimage()

print('Got the list of datasets, iterating to retrieve metadata...')

out_list = []

for study in studies_list:
    accession = study.get('accession', '')
    s = bs.get_study(accession)

    if len(s.organisms) == 1 and (match := re.match(r'\w+\s+\w+', next(iter(s.organisms)))):
        out_list.append({
            'Accession': accession,
            'Title': s.title,
            'Description': s.description,
            'Organism': match.group(0)
        })

print(f'Collected {len(out_list)} datasets with a known organism')

pd.DataFrame(out_list).to_csv("BioImages.csv")
