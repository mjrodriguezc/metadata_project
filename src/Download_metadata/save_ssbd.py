from dl_metadata.api.ssbd import SSBD
import pandas as pd


ssbd = SSBD()

records = ssbd.get_records()

out_list = []
for rec in records:

    if rec.get('organism'):
        out_list.append({
            'PMID': rec.get('PMID', ''),
            'bdmlID': rec.get('bdmlID', ''),
            'Title': rec.get('title', ''),
            'Description': rec.get('description', ''),
            'Organism': rec.get('organism', ''),
            'Gene': rec.get('gene', '')
        })

species_replacements = {
    'C. elegans': 'Caenorhabditis elegans',
    'D. rerio': 'Danio rerio',
    'M. musculus': 'Mus musculus',
    'D. discoideum': 'Dictyostelium discoideum',
    'R. norvegicus': 'Rattus norvegicus',
    'Rattus novegicus': 'Rattus norvegicus',
    'M. sieboldi': 'Magnolia sieboldi',
    'D. melanogaster': 'Drosophila melanogaster',
    'E. coli': 'Escherichia coli',
    'Canis lupus familiaris': 'Canis lupus'
}

(
    pd.DataFrame(out_list)
    .assign(Organism = lambda df: df.Organism.replace(species_replacements))
    .query('Organism != "nan" and Organism != "NA"')
    .to_csv('SSBD.csv')
)
