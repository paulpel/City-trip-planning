import copy
import json
import logging
import sys
from typing import Dict

import geopy.distance


class CityTrip:

    def __init__(self) -> None:
        """Init function
        """
        logging.basicConfig(
            format="[%(asctime)s] [%(levelname)s] [%(filename)s %(funcName)s:%(lineno)d] Msg: %(message)s")

        self.distances = {}
        self.choosen_city = "rome"

        self.data = self.load_data()
        self.cities = list(self.data.keys())

    def main(self) -> None:
        """Main function of City Planning App
        """
        self.calc_distances()

    def load_data(self) -> Dict:
        """Load data from json

        :return: attractions mapped to cities
        :rtype: Dict
        """
        with open("attractions.json") as jf:
            data = json.load(jf)

        if data:
            return data
        else:
            logging.error("Data empty!")
            sys.exit(-1)

    def calc_distances(self):
        """Calculate distances beetween all attraction combination
        """
        all_attractions = list(self.data[self.choosen_city].keys())

        copy_all_attractions = copy.deepcopy(all_attractions)

        while copy_all_attractions:
            attraction_a = copy_all_attractions.pop()
            self.distances[attraction_a] = {}
            cords_a = (
                self.data[self.choosen_city][attraction_a]["cords"]["latitude"],
                self.data[self.choosen_city][attraction_a]["cords"]["longitude"]
                )

            for attraction_b in all_attractions:
                if attraction_a != attraction_b:
                    cords_b = (
                        self.data[self.choosen_city][attraction_b]["cords"]["latitude"],
                        self.data[self.choosen_city][attraction_b]["cords"]["longitude"]
                        )
                    self.distances[attraction_a][attraction_b] = \
                        geopy.distance.geodesic(cords_a, cords_b).km


if __name__ == "__main__":

    ct_obj = CityTrip()
    ct_obj.main()
