import requests


class SSBD():
    API_ENDPOINT = 'http://ssbd.qbic.riken.jp/SSBD/api/v3'

    def get_records(self):
        records = []
        are_more = True
        params = {
            'format': 'json',
            'limit': 1000,
            'offset': 0
        }
        while are_more:
            r = requests.get(f'{self.API_ENDPOINT}/data', params=params)
            r.raise_for_status()

            records += r.json().get('objects', [])
            meta = r.json().get('meta', {})

            are_more = meta.get('total_count') > meta.get('limit') + meta.get('offset')
            if are_more:
                params['offset'] += params['limit']
            
        return records
