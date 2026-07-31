import seaborn.objects as so
import pandas as pd


data = pd.read_csv('/home/dthedie/Documents/Metadata_prediction/Data/BD2_SciSpacy_NER.csv')

ent_counts = (data
              .groupby('label')
              .agg(count = ('id', 'count'))
              .sort_values('count', ascending=False)
              )

(
    so.Plot(ent_counts, x='count', y='label', text='count')
    .add(so.Bar())
    .add(so.Text(halign='left'))
    .label(x='Number of entities', y='')
    .show()
)

###

unique_counts = (data
                 .groupby('label')
                 .agg(count = ('id', lambda x: len(x.unique())))
                 .sort_values('count', ascending=False)
                 )

(
    so.Plot(unique_counts, x='count', y='label', text='count')
    .add(so.Bar())
    .add(so.Text(halign='left'))
    .label(x='Number of unique entities', y='')
    .show()
)

###

top_labels = (data
              .rename(columns={'text': 'entity'})
              .groupby('entity')
              .agg(count = ('id', 'count'),
                   label = ('label', 'first'))
              .sort_values('count', ascending=False)
              .iloc[:50,]
              )

(
    so.Plot(top_labels, x='count', y='entity', text='count', color='label')
    .add(so.Bar())
    .add(so.Text(halign='left'))
    .label(x='Number of entities', y='', color='SciSpacy label')
    .show()
)

###

label = 'ORGAN'

top_single_label = (data
                    .rename(columns={'text': 'entity'})
                    .query(f'label == "{label}"')
                    .groupby('entity')
                    .agg(count = ('id', 'count'),
                         label = ('label', 'first'))
                    .sort_values('count', ascending=False)
                    .iloc[:50,]
                    )

(
    so.Plot(top_single_label, x='count', y='entity', text='count')
    .add(so.Bar())
    .add(so.Text(halign='left'))
    .label(x='Number of entities', y='', title=label)
    .show()
)
