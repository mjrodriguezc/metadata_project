import requests

from dl_metadata.domain.biostudies import Study


class BioStudies():
    API_ENDPOINT = 'https://www.ebi.ac.uk/biostudies/api/v1'        

    def get_all_biostudies(self) -> dict:
        studies = []
        are_more = True
        params = {
            'page': 1,
            'pageSize': 100
        }
        while are_more:
            r = requests.get(f'{self.API_ENDPOINT}/search', params = params)
            r.raise_for_status()
            hits = r.json().get('hits', [])
            studies += hits
            are_more = len(hits) == 100
            if are_more:
                params['page'] += 1
        return studies

    def get_all_bioimage(self) -> dict:
        studies = []
        are_more = True
        params = {
            'page': 1,
            'pageSize': 100
        }
        while are_more:
            r = requests.get(f'{self.API_ENDPOINT}/BioImages/search', params = params)
            r.raise_for_status()
            hits = r.json().get('hits', [])
            studies += hits
            are_more = len(hits) == 100
            if are_more:
                params['page'] += 1
        return studies

    def get_study(self, accession) -> Study:
        r = requests.get(f'{self.API_ENDPOINT}/studies/{accession}')
        r.raise_for_status()
        return Study(accession, r.json())
