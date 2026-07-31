import json
from pathlib import Path
import pandas as pd
import spacy


exp_path = Path('/home/dthedie/Documents/Metadata_prediction/Data/BD2_metadata_2025-07-22')

texts = []
for id in exp_path.iterdir():

    with id.open('r') as f:
        exp = json.load(f)

    dsc = exp.get('generalDesc', {})
    text = ' '.join([dsc.get('name') or '',
                     dsc.get('purpose') or '',
                     dsc.get('description') or '',
                     dsc.get('comments') or ''])

    texts.append((text, {'id': id.stem}))


with open('bd2_freetext.json', 'w') as f:
    json.dump(texts, f)
    
nlp = spacy.load("en_ner_bionlp13cg_md")

doc_tuples = nlp.pipe(texts, as_tuples=True)

tags = []
for doc, context in doc_tuples:
    for entity in doc.ents:
        tags.append({
            'id': context['id'],
            'text': entity.text.strip(),
            'label': entity.label_
        })

pd.DataFrame(tags).to_csv('BD2_SciSpacy_NER.csv', index=False)
