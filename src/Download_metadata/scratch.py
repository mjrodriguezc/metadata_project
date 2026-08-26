from dl_metadata.api.ssbd import SSBD


ssbd = SSBD()

data = ssbd.get_records()

print(len(data))
print(data[0].keys())

