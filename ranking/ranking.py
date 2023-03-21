from pydantic import BaseModel
from typing import Optional
import json


class Rank(BaseModel):
    label: str
    minimum: float
    maximum: float


class Ranking:
    ranks = []

    @staticmethod
    def get_valutation_from_area(area) -> Optional[str]:
        if Ranking.ranks:
            for rank in Ranking.ranks:
                if rank.minimum <= area < rank.maximum:
                    return rank.label
            return None
        else:
            Ranking.load_ranks_from_json()
            return Ranking.get_valutation_from_area(area)

    @staticmethod
    def load_ranks_from_json():
        if not Ranking.ranks:
            json_ranks = Ranking.get_decoded_json()
            for json_rank in json_ranks:
                minimum = json_ranks[json_rank]["min"]
                maximum = json_ranks[json_rank]["max"]
                rank = Rank(label=json_rank, minimum=minimum, maximum=maximum)
                Ranking.ranks.append(rank)

    @staticmethod
    def get_decoded_json():
        with open(f'ranking/ranking.json', 'r') as file:
            return json.load(file)