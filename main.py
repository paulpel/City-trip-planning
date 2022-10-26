import json
import logging
import configparser
import sys
import time
from datetime import datetime

import openrouteservice
import numpy as np


class CityTrip:

    def __init__(self, choosen_c, start_t, end_t, bud, start_p, forbidden):
        self.config()

        self.choosen_city = choosen_c
        self.start_time = datetime.strptime(start_t, "%H:%M")
        self.end_time = datetime.strptime(end_t, "%H:%M")
        self.budget = bud
        self.start_point = start_p
        self.forbidden_attractions = forbidden

        if self.end_time > self.start_time:
            self.time_left = self.end_time - self.start_time
        else:
            logging.error("Wrong time windows entered!")
            sys.exit(-1)

        self.current_atraction = "Koloseum"

        self.data = self.load_data()
        self.distances = self.load_distances()

        self.prob_matrix()
        self.calc_distance_start_end_point()

    def main(self):
        self.check_time()

    def check_time(self):
        pass

    def prob_matrix(self):
        all_nodes = list(self.data[self.choosen_city].keys())
        all_nodes.append("start")
        prob_m = np.ones((len(all_nodes), len(all_nodes)))
        np.fill_diagonal(prob_m, 0)

        for attr in self.forbidden_attractions:
            indx = all_nodes.index(attr)
            for row in prob_m:
                row[indx] = 0

        self.probability_matrix = prob_m
        self.attractions_list = all_nodes

    def calc_distance_start_end_point(self, test=True):
        if test:
            with open("start.json") as jf:
                self.distances["start"] = json.load(jf)
        else:
            client = openrouteservice.Client(key=self.api_key)
            start = {}

            all_attractions = list(self.data[self.choosen_city].keys())
            i = 1
            for attraction in all_attractions:
                logging.info(f"Calculating distances... {i/len(all_attractions)*100} %")
                cords_a = (
                    self.data[self.choosen_city][attraction]["cords"]["longitude"],
                    self.data[self.choosen_city][attraction]["cords"]["latitude"]
                    )
                distance = client.directions(
                    (cords_a, self.start_point),
                    profile="foot-walking")["routes"][0]["summary"]
                start[attraction] = distance
                time.sleep(1.5)
                i += 1

            self.distances["start"] = start

    def load_data(self):
        with open("attractions.json") as jf:
            data = json.load(jf)

        if data:
            return data
        else:
            logging.error(f"Attracions data empty! City: {self.choosen_city}")
            sys.exit(-1)

    def load_distances(self):
        file_name = f"distances_{self.choosen_city}.json"
        with open(file_name) as jf:
            dist = json.load(jf)

        if dist:
            return dist
        else:
            logging.error(f"Distance data empty! City: {self.choosen_city}")
            sys.exit(-1)

    def config(self):
        config = configparser.ConfigParser()
        config.read('config.cfg')
        logging.basicConfig(format=config["logging"]["format"], level=logging.INFO)
        self.api_key = config["ORS"]["api_key"]


if __name__ == "__main__":

    ct_obj = CityTrip(
        "rome",
        "9:00",
        "19:00",
        "100",
        (12.490514900515363, 41.90862361898305),
        ["Koloseum"])

    ct_obj.main()
