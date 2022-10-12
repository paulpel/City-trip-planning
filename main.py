import json
import logging
import sys
import pandas as pd
from typing import Dict


class CityTrip:

    def __init__(self) -> None:
        """Init function
        """
        logging.basicConfig(
            format="[%(asctime)s] [%(levelname)s] [%(filename)s %(funcName)s:%(lineno)d] Msg: %(message)s")

        self.cities = set()
        self.attractions = self.load_data()

    def main(self) -> None:
        """Main function of City Planning App
        """
        pass

    def load_data(self) -> Dict:
        """Load data from json

        :return: attractions mapped to cities
        :rtype: Dict
        """
        with open("attractions.json") as jf:
            data = json.load(jf)

        cities = {}
        for city in data:
            self.cities.add(city)

            cities[city] = pd.DataFrame.from_dict(
                data[city], orient='columns', dtype=None, columns=None)

        if cities:
            return cities
        else:
            logging.error("Data empty!")
            sys.exit(-1)


if __name__ == "__main__":

    ct_obj = CityTrip()
    ct_obj.main()
