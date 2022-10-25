import configparser
import copy
import json
import logging
import profile
import sys
import time
from typing import Dict

import geopy.distance
import openrouteservice


class CityTrip:

    def __init__(self) -> None:
        """Init function
        """
        self.config()
        self.connect_ors()
        self.distances = {}
        self.choosen_city = "rome"

        self.data = self.load_data()
        self.cities = list(self.data.keys())

    def main(self) -> None:
        """Main function of City Planning App
        """
        self.calc_distances()

    def config(self):
        """Configure logging and get config
        """
        logging.basicConfig(
            format="[%(asctime)s] [%(levelname)s] [%(filename)s %(funcName)s:%(lineno)d] Msg: %(message)s")
        config = configparser.ConfigParser()
        config.read('config.cfg')
        self.api_key = config["ORS"]["api_key"]

    def connect_ors(self):
        self.client = openrouteservice.Client(key=self.api_key)

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
        with open("distances.json") as jf:
            dist = json.load(jf)

        all_attractions = list(self.data[self.choosen_city].keys())

        for attraction_a in all_attractions:
            if attraction_a not in dist:
                dist[attraction_a] = {}

                cords_a = (
                    self.data[self.choosen_city][attraction_a]["cords"]["longitude"],
                    self.data[self.choosen_city][attraction_a]["cords"]["latitude"]
                    )

                for attraction_b in all_attractions:
                    if attraction_a != attraction_b:
                        cords_b = (
                            self.data[self.choosen_city][attraction_b]["cords"]["longitude"],
                            self.data[self.choosen_city][attraction_b]["cords"]["latitude"]
                            )
                        print(attraction_a, cords_a)
                        print(attraction_b, cords_b)
                        try:
                            res = self.client.directions((cords_a, cords_b), profile="foot-walking")["routes"][0]["summary"]
                            print(res)
                        except:
                            print("Something wrong")

                        dist[attraction_a][attraction_b] = res
                        time.sleep(1.5)
            else:
                continue
            break
    
        with open("distances.json", "w") as jf:
            json.dump(dist, jf, indent=4)


if __name__ == "__main__":

    ct_obj = CityTrip()
    ct_obj.main()
