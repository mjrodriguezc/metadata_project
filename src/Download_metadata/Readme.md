# Downloading metadata from different repositories

The code used to connect to the different APIs is stored under `dl_metadata`.

The main function to download metadata from a repository is `save_...` (e.g. `save_zenodo.py`).

## Zenodo

In Zenodo, there is no "organism" field that we can query. However, datasets seem to often contain organism information as keyword.

The current code uses the list of species from BioDare2 (`biodare2_species.txt`) as a list of species to query. This is arbitrary, it is possible to add more species to the text file to extend the dataset.

Note that some dataset titles and descriptions are not in English. I found no easy way of filtering for this. Could make it difficult, although maybe the LLM can deal with that?

## SSBD

Retrieving the full data from SSBD is fairly straightforward (and the data is not very big, 687 datasets). It needed a bit of curation, as organisms were not always recorded in the same format (e.g. "M. musculus" or "Mus musculus"). The code replaces all these instance by the full name ("Mus musculus").

In addition, "Gene" information was available, so I added it to the table in case we want to try predicting it as well.

## BioImages core

The current code queries the core BioImage data, which contains ~1,500 datasets. This could be extended to get more data to other parts of BioImage, or to other parts of BioStudies (3.4M datasets total, though not all have an "organism" field).

BioImage datasets can have multiple organisms. For now, datasets which have several organisms are discarded.

Organisms were often recorded as "Homo sapiens (human)", which gets normalised here to "Homo sapiens" (keep only the first two words). Organisms that had only one word (e.g. "RAT") are discarded.

## PDB

There are ~250,000 structures in the PDB. Fortunately the API is efficient, so it was possible to retrieve organism information for all where it was available (almost all structures).

There is no "description" field in the PDB metadata, so we will have to rely only on title.

There can be multiple organisms per structure, but from manual inspection of a few entries, most of the time the first organism mentioned is the most relevant (e.g. a human protein in complex with synthetic DNA will have organism = Homo sapiens, Synthetic construct). So here I chose to always keep only the first organism value.

To normalise the organism field I kept only the first two words in the field. For example, "Escherichia coli K-12" becomes just "Escherichia coli". There will still be non-standard organism names (e.g. "Saccharomyces sp."), but hopefully that will be a minority in a fairly large dataset.
