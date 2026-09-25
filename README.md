# This readme file was generated on 2026-09-21 by Maria Juliana Rodriguez-Cubillos

GENERAL INFORMATION

- Date of data collection: June 2025
- Information about funding sources that supported the collection of the data: UK Research and Innovation - EASTBIO DTPBB/J01446X/1


SHORT DESCRIPTION

Ensuring the availability and accessibility of research data is fundamental to advancing knowledge. This goal has been codified in the FAIR principles (Findable, Accessible, Interoperable, and Reusable) for scientific data management. Accurate documentation of studies—commonly referred to as metadata—is indispensable for meeting these principles. However, entries in deposition databases that secure the research record often contain inadequate, repetitive, or incomplete descriptions.

Much of this metadata is captured in free-text boxes rather than structured fields, motivating the need for scalable, repository-agnostic methods to quantify descriptive metadata richness in databases that contain different types of information. Here, we quantify free-text metadata richness across three deposition repositories and compare patterns using Natural Language Processing (NLP) methods: BioDare2, an experimental circadian rhythm database; DataShare, a domain-agnostic database for the University of Edinburgh; and Image Data Resource (IDR), a public repository of biological image datasets from published scientific studies.

In general, repositories exhibit distinct distributions of word count and information density, consistent with differences in scope (agnostic vs specialist). The named-entity recognition approach and information-density metric detected significant category-level differences in BioDare2 (species) and DataShare (communities). In contrast, the method also identified greater consistency in the more curated repository IDR. Finally, the most frequent entities reflected each repository’s focus (circadian terminology in BioDare2, microscopy-related entities in IDR, and community-driven terms in DataShare).

We develop a scalable analysis framework that utilises word counts, named-entity recognition, and entity-derived information density to examine the current state of metadata in multiple repositories, creating a broadly applicable framework for metadata assessment and evaluation. This is the dataset from the three listed repositories associated with the paper. 



SHARING/ACCESS INFORMATION

- Licenses/restrictions placed on the data: CC BY 4.0
- Links to publications that cite or use the data: https://www.biorxiv.org/content/10.64898/2026.09.08.749906v1
- Links to other publicly accessible locations of the data: DOI 10.5281/zenodo.22229073
- Recommended citation for this dataset: Rodriguez-Cubillos, M. J., Zieliński, T., Swedlow, J., Simpson, I., & Millar, A. (2026). Dataset from the Paper: "The Shape of Biological Metadata: Measuring Repository Richness with Entity-Based NLP Metrics" [Data set]. Zenodo. https://doi.org/10.5281/zenodo.22229074


DATA & FILE OVERVIEW

File List: 

- Dataset from BioDare: "df_biodare2_ratio_entities_20250504.csv"
- Dataset from DataShare: "df_datashare_ratio_entities_20260504.csv"
- Dataset from IDR: "df_IDR_ratio_entities_20260504.csv"

The columns used for the analysis were: 

- "*_word_count": Word count on the listed field. Please replace * with the name of the file evaluated. 
- "*_clean_lemmatize": Free-text after lemmatization. Please replace * with the name of the file evaluated. 
- "*_clean_entities": List of entities after lemmatization and entity recognition. Please replace * with the name of the file evaluated. 
- "all_entities": All entities per every evaluated field.
- "entities": List of unique entities in all the evaluated fields.
- "global_counts": Total counts in all the free text description fields evaluated.
- "ratio_entites_per_word": Number of entities per word from the list of all entities.


METHODOLOGICAL INFORMATION

Description of methods used for collection/generation of data:
Three independent datasets were used during the study: BioDare2 with 20,471 entries, DataShare with 7,754 entries and IDR with 132 entries. Each one was processed separately, but the same processing steps were applied to each. First, the files were acquired from the repositories. Then, the stop words and special characters were removed, all capital letters were replaced with lowercase, and the words were lemmatised.

Instrument- or software-specific information needed to interpret the data:
Language: Python.
Packages: pandas, nltk, scispacy, spacy.
Code available: https://github.com/mjrodriguezc/metadata_project/tree/main/src/Repositories_analysis

