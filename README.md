# Metadata Accelerator

Ensuring the availability and accessibility of data is fundamental to advancing knowledge. This idea has been codified as the FAIR principles (Findable, Accessible, Interoperable, and Reusable) in scientific data management. Accurate documentation of studies, commonly known as metadata, is indispensable for achieving this goal. Regrettably, scientific records often fall short, providing inadequate, repetitive, or incomplete descriptions that hinder the seamless flow of knowledge. This project addresses the metadata challenge by identifying common failure points in descriptions and generating better-structured metadata using NLP and LLMs, with a focus on sustainability.

The Metadata Accelerator is a pipeline that aims to predict metadata using information from free-text descriptions. Based on initial user inputs, the pipeline suggests improvements that fit template-based schemas and provides feedback using quality metrics. Users can then refine the suggested changes before export, allowing us to engage users and explore whether richer interaction improves metadata quality.

The pilot version of the pipeline predicts “species” and “study type” for each entry from user-provided descriptions using a combination of NLP methods and LLMs, including Llama 3.2 and BioBERT. The Image Data Resource (IDR) and BioDare2, a repository for circadian and biological data, were selected to develop a pipeline that suggests metadata terms from existing free-text descriptions. For IDR, the system identified 97 species compared with 110 in a manual review and matched 130 of 132 study-type entries.

Ongoing work will evaluate performance on BioDare2 and other repositories, improve efficiency, and expand to additional categories.
