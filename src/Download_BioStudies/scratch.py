from dl_biostudies.api.biostudies import BioStudies


bs = BioStudies()

study = bs.get_study("S-BIAD3320")

print(study.title)

print(study.description)

print(study.organisms)
