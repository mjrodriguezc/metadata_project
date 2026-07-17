from dl_biostudies.api.biostudies import BioStudies
import pandas as pd


bs = BioStudies()

studies_list = bs.get_all_bioimage()

print('Got the list of datasets, iterating to retrieve metadata...')

out_list = []

for study in studies_list:
    accession = study.get('accession', '')
    s = bs.get_study(accession)

    if len(s.organisms) == 1:
        out_list.append({
            'Accession': accession,
            'Title': s.title,
            'Description': s.description,
            'Organism': next(iter(s.organisms))
        })

print(f'Collected {len(out_list)} datasets with a known organism')

df = pd.DataFrame(out_list, columns=['Accession', 'Title', 'Description', 'Organism'])    

df.to_csv("BioImages.csv")
