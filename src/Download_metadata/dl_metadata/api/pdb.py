import requests


class PDB():
    REST_ENDPOINT = 'https://data.rcsb.org/rest/v1'
    GRAPHQL_ENDPOINT = 'https://data.rcsb.org/graphql'

    def get_all_ids(self) -> list:
        r = requests.get(f'{self.REST_ENDPOINT}/holdings/current/entry_ids')
        r.raise_for_status()
        return r.json()

    def get_metadata(self, ids: list) -> list:
        offset = 0
        are_more = True
        results = []
        while are_more:
            batch = ids[offset:min(offset + 1000, len(ids))]
            ids_str = '["' + '","'.join(batch) + '"]'
            query = f"""
{{
  entries(entry_ids: {ids_str}) {{
    rcsb_id
    struct {{
      title
    }}
    polymer_entities {{
      rcsb_entity_source_organism {{
        ncbi_scientific_name
      }}
    }}
  }}
}}
"""
            
            r = requests.post(f'{self.GRAPHQL_ENDPOINT}', json={'query': query})
            r.raise_for_status()

            results += r.json().get('data', {}).get('entries', [])

            are_more = offset + 1000 < len(ids)
            if are_more:
                offset += 1000
        return results
