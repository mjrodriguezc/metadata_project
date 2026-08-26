from dl_metadata.api.pdb import PDB
import pandas as pd
import re


pdb = PDB()

ids = pdb.get_all_ids()
data = pdb.get_metadata(ids)
out_list = []

for d in data:

    try:
        organism = d['polymer_entities'][0]['rcsb_entity_source_organism'][0]['ncbi_scientific_name'] or ''
    except (KeyError, IndexError, TypeError):
        organism = ''

    if match := re.match(r'\w+\s+\w+', organism):
        out_list.append({
            'ID': d.get('rcsb_id'),
            'Title': d.get('struct', {}).get('title', ''),
            'Organism': match.group(0)
        })

pd.DataFrame(out_list).to_csv('PDB.csv')
