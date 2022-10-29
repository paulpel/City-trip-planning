import json
import logging
import configparser
import sys
import random
import time
from datetime import datetime
from itertools import tee

import openrouteservice
import numpy as np


class CityTrip:

    def __init__(self, choosen_c, start_t, end_t, bud, start_p, forbidden, preferences):
        self.config()

        self.choosen_city = choosen_c
        self.start_time = datetime.strptime(start_t, "%H:%M")
        self.end_time = datetime.strptime(end_t, "%H:%M")
        self.budget = bud
        self.start_point = start_p
        self.forbidden_attractions = forbidden
        self.preferences = preferences
        self.preferences_order = [
            "Architektura",
            "Koscioly i katedry",
            "Muzea",
            "Parki i ogrody",
            "Rekreacja",
            "Punkt widokowy"
        ]

        if self.end_time > self.start_time:
            self.time_left = self.end_time - self.start_time
        else:
            logging.error("Wrong time windows entered!")
            sys.exit(-1)

        self.current_atraction = "start"

        self.data = self.load_data()
        self.distances = self.load_distances()

        self.prob_matrix_f()
        self.calc_distance_start_end_point()

        self.amount_of_ants = 10
        self.iterations = 1

    def main(self):
        self.check_time_start()
        self.check_budget_start()

        all_solutions = []
        for i in range(self.iterations):
            epoch_solutions = []
            epoch_criteria = []
            for ant in range(self.amount_of_ants):
                one_ant_solution = ["start"]

                attracions_left = self.attractions_list.copy()
                temp_prob = self.probability_matrix.copy()

                while attracions_left:
                    indx = self.attractions_list.index(self.current_atraction)
                    probability = temp_prob[indx]
                    if sum(probability) == 0:
                        break
                    destination = random.choices(self.attractions_list, weights=probability)[0]

                    indx_dest = self.attractions_list.index(destination)
                    attracions_left.remove(destination)
                    for row in temp_prob:
                        row[indx_dest] = 0

                    if self.check_limitations(one_ant_solution, destination):
                        one_ant_solution.append(destination)
                one_ant_solution.append("start")
                one_ant_criteria = self.calc_criteria(one_ant_solution)

                epoch_solutions.append(one_ant_solution)
                epoch_criteria.append(one_ant_criteria)
            normalized_epoch_criteraia = self.normalize_criteria(epoch_criteria)

    def normalize_criteria(self, epoch_criteria):
        money_list = [item[0] for item in epoch_criteria]
        pref_list = [item[1] for item in epoch_criteria]
        pop_list = [item[2] for item in epoch_criteria]
        amount_list = [item[3] for item in epoch_criteria]

        norm_money_list = [
            (i - min(money_list))/(max(money_list)-min(money_list)) for i in money_list]
        norm_pref_list = [
            (i - min(pref_list))/(max(pref_list)-min(pref_list)) for i in pref_list]
        norm_pop_list = [
            (i - min(pop_list))/(max(pop_list)-min(pop_list)) for i in pop_list]
        norm_amount_list = [
            (i - min(amount_list))/(max(amount_list)-min(amount_list)) for i in amount_list]
        array_normalized = np.array([norm_money_list, norm_pref_list, norm_pop_list, norm_amount_list])
        array_normalized = array_normalized.transpose()

        return array_normalized

    def calc_criteria(self, path):
        criteria = []
        only_attractions = [item for item in path if item != "start"]

        # money
        money = 0
        for atr in only_attractions:
            money_spend = float(self.data[atr]["price"])
            money += money_spend
        criteria.append(money)

        # preferences
        preferences = 0
        for atr in only_attractions:
            categories = self.data[atr]["category"]
            time_spend = self.data[atr]["timespend"]
            for cat in categories:
                preferences += time_spend * self.preferences[
                    self.preferences_order.index(cat)]
        preferences = preferences/len(categories)
        criteria.append(preferences)

        # popular, highly reviewed
        popular = 0
        for atr in only_attractions:
            time_spend = self.data[atr]["timespend"]
            popular += time_spend * self.data[atr]["rating"]*self.data[atr]["popularity"]
        criteria.append(popular)

        # amount seen
        criteria.append(len(only_attractions))
        return criteria

    def check_limitations(self, path, destination):
        total_time = 0
        for attr in path:
            if attr != "start":
                time_spend = float(self.data[attr]["timespend"])*60
                total_time += time_spend
        
        for elem in self.pairwise(path):
            time_travel = float(
                    self.distances[elem[0]][elem[1]]["duration"])
            total_time += time_travel
        
        total_time += float(
                    self.distances[path[-1]][destination]["duration"])
        total_time += float(
                    self.distances["start"][destination]["duration"])
        total_time +=  float(self.data[destination]["timespend"])*60

        total_money = 0
        for attraction in path:
            if attraction != "start":
                money_spend = float(self.data[attraction]["price"])
                total_money += money_spend

        money_dest = float(self.data[destination]["price"])
        total_money += money_dest

        if total_time > self.time_left.total_seconds() or total_money > self.budget:
            return False
        else:
            return True
    
    def pairwise(self, iterable):
        a, b = tee(iterable)
        next(b, None)
        return zip(a, b)

    def check_time_start(self):
        for attraction in self.attractions_list:
            if attraction != "start":
                time_travel = float(
                    self.distances["start"][attraction]["duration"])
                time_spend = float(self.data[attraction]["timespend"])*60

                if self.time_left.total_seconds() - (time_travel*2 + time_spend) < 0:
                    indx = self.attractions_list.index(attraction)
                    for row in self.probability_matrix:
                        row[indx] = 0

    def check_budget_start(self):
        for attraction in self.attractions_list:
            if attraction != "start":
                money_spend = float(self.data[attraction]["price"])
                if money_spend > self.budget:
                    indx = self.attractions_list.index(attraction)
                    for row in self.probability_matrix:
                        row[indx] = 0

    def prob_matrix_f(self):
        all_nodes = list(self.data.keys())
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

            all_attractions = list(self.data.keys())
            i = 1
            for attraction in all_attractions:
                logging.info(f"Calculating distances... {i/len(all_attractions)*100} %")
                cords_a = (
                    self.data[attraction]["cords"]["longitude"],
                    self.data[attraction]["cords"]["latitude"]
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
            return data[self.choosen_city]
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
        np.set_printoptions(threshold=sys.maxsize)


if __name__ == "__main__":

    ct_obj = CityTrip(
        "rome",
        "9:00",
        "19:00",
        20,
        (12.490514900515363, 41.90862361898305),
        ["Koloseum"],
        [3, 3, 3, 4, 3, 4])

    ct_obj.main()
