from dl_metadata.api.zenodo import Zenodo
import pandas as pd


with open('biodare2_species.txt', 'r') as f:
    species = f.read().splitlines()

znd = Zenodo('../../../.auth/zenodo_token.txt')

out_list = []
for s in species:
    records = znd.get_organism_records(s)

    for rec in records:
        
        out_list.append({
            'ID': rec.get('id', ''),
            'Title': rec.get('metadata', {}).get('title', ''),
            'Description': rec.get('metadata', {}).get('description', ''),
            'Organism': s
        })

pd.DataFrame(out_list).to_csv('Zenodo.csv')
