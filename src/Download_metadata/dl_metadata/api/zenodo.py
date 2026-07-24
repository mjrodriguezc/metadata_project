import requests
from time import sleep


class Zenodo():
    API_ENDPOINT = 'https://zenodo.org/api'

    def __init__(self, token_file: str):
        with open(token_file) as f:
            token = f.readline().strip()
        
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }

    def get_organism_records(self, name: str) -> list:
        records = []
        are_more = True
        params = {
            'q': f'keywords:"{name}"',
            'page': 1,
            'size': 100,
            'allversions': False
        }
        retries = 0
        while are_more:
            r = requests.get(f'{self.API_ENDPOINT}/records', params=params, headers=self.headers)

            if r.status_code == 504:
                retries += 1
                if retries > 5:
                    print('Hit max retries')
                    r.raise_for_status()
                sleep(5 * retries)

            r.raise_for_status()
            hits = r.json().get('hits', {}).get('hits', [])
            records += hits
            
            if r.headers.get('X-RateLimit-Remaining') == '0':
                sleep(60)
                    
            are_more = len(hits) == params['size']
            if are_more:
                params['page'] += 1
        return records
