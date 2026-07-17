from dataclasses import dataclass

@dataclass(frozen=True)
class Study:
    accession: str
    data: dict

    @property
    def attributes(self):
        return self.data.get('section', {}).get('attributes', [])

    @property
    def subsections(self):
        return self.data.get('section', {}).get('subsections', [])

    @property
    def title(self) -> str:
        return next((a.get('value', '') for a in self.attributes if a.get('name', '') == 'Title'), '')

    @property
    def description(self) -> str:
        return next((a.get('value', '') for a in self.attributes if a.get('name', '') == 'Description'), '')

    @property
    def organisms(self) -> set[str]:
        return {
            a.get('value')
            for sub in self.subsections
            for a in sub.get('attributes', [])
            if a.get('name') == 'Organism' and a.get('value')
        }

