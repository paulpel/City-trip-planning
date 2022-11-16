import json
import logging
import configparser
import sys
import os
import random
import time
from datetime import datetime, timedelta
from itertools import tee

import openrouteservice
import numpy as np
import ahpy


class CityTrip:

    def __init__(self, choosen_c, start_t, end_t, bud, start_p, forbidden, preferences, comparisons):
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
        self.money_pref_c = comparisons[0]
        self.money_pop_c = comparisons[1]
        self.money_amount_c = comparisons[2]
        self.pref_pop_c = comparisons[3]
        self.pref_amount_c = comparisons[4]
        self.pop_amount_c = comparisons[5]

        self.attration_path = os.path.join("data", "attractions.json")
        self.distances_city = os.path.join("data", f"distances_{self.choosen_city}.json")
        self.test_dist = os.path.join("data", "start.json")

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

        self.amount_of_ants = 100
        self.iterations = 100
        self.divide_pheromones = 2  # 1: (0, 1), 2: (0, 0.5)
        self.maximum_weight = 20
        self.minimum_weight = 1
        self.decay_value = 0.1
        self.amount_of_solutions = 3

        self.dominant_solutions = []
        self.dominant_solutions_criteria = []

    def main(self):
        self.check_time_start()
        self.check_budget_start()

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
            pheromones = self.get_pheromones(normalized_epoch_criteraia)
            self.update_pheromones(pheromones, epoch_solutions)
            self.decay_pheromones()
            self.get_dominant(epoch_solutions, epoch_criteria)

        final_normalized = self.normalize_criteria(self.dominant_solutions_criteria)
        index_best_solutions = self.ahp_sort_solutions(final_normalized)

        best_sol = []
        for ind in index_best_solutions:
            best_sol.append(self.dominant_solutions[ind])
        best_sol.reverse()

        prepared_sol = self.prep_final_data(best_sol)

        return prepared_sol

    def prep_final_data(self, data):
        trips = []
        for sol in data:

            trip = {
                "path": sol,
            }

            pairs = self.pairwise(sol)
            times_dep = [datetime.strftime(self.start_time, "%H:%M")]
            times_arr = ["-"]
            times_spent = ["-"]
            money_spend = ["-"]
            categories = ["-"]
            total_time = self.start_time
            for pair in pairs:
                if pair[1] != 'start':
                    travel_time = self.distances[pair[0]][pair[1]]["duration"]
                    total_time += timedelta(0, travel_time)
                    times_arr.append(datetime.strftime(total_time, "%H:%M"))

                    time_spend = self.data[pair[1]]["timespend"]
                    times_spent.append(time_spend)
                    total_time += timedelta(0, time_spend*60)
                    times_dep.append(datetime.strftime(total_time, "%H:%M"))
                    money_spend.append(self.data[pair[1]]["price"])
                    categories.append(self.data[pair[1]]["category"])
                else:
                    travel_time = self.distances[pair[1]][pair[0]]["duration"]
                    total_time += timedelta(0, travel_time)
                    times_arr.append(datetime.strftime(total_time, "%H:%M"))

            times_dep.append("-")
            categories.append("-")
            money_spend.append("-")
            times_spent.append('-')
            trip['times'] = (times_arr, times_dep, times_spent)
            trip["money"] = money_spend
            trip["categories"] = categories
            trips.append(trip)

        return trips

    def ahp_sort_solutions(self, criteria_values):
        criteria_sum = []
        criteria_comparisons = {
            ("money", "preferences"): self.money_pref_c,
            ("money", "popular"): self.money_pop_c,
            ("money", "amount"): self.money_amount_c,
            ("preferences", "popular"): self.pref_pop_c,
            ("preferences", "amount"): self.pref_amount_c,
            ("popular", "amount"): self.pop_amount_c
        }

        criteria = ahpy.Compare(
            name="Criteria",
            comparisons=criteria_comparisons,
            precision=3,
            random_index="saaty")

        money_weight = criteria.target_weights["money"]
        pref_weight = criteria.target_weights["preferences"]
        popular_weight = criteria.target_weights["popular"]
        amount_weight = criteria.target_weights["amount"]

        for solution in criteria_values:
            total = solution[0]*money_weight\
                + solution[1]*pref_weight\
                + solution[2]*popular_weight\
                + solution[3]*amount_weight
            criteria_sum.append(total)
        from_worst_to_best = np.argsort(criteria_sum)
        return from_worst_to_best[-self.amount_of_solutions:]

    def get_dominant(self, epoch_solutions, epoch_criteria):
        self.dominant_solutions_criteria.extend(epoch_criteria)
        self.dominant_solutions.extend(epoch_solutions)
        temp_criteria = self.dominant_solutions_criteria.copy()
        temp_solutions = self.dominant_solutions.copy()

        paretoPoints, _ = self.simple_cull(temp_criteria, self.dominates)

        sol = []
        crit = []
        for p in paretoPoints:
            index = self.dominant_solutions_criteria.index(list(p))
            sol.append(temp_solutions[index])
            crit.append(list(p))
        self.dominant_solutions = sol
        self.dominant_solutions_criteria = crit

    def dominates(self, row, candidateRow):
        return sum([row[x] >= candidateRow[x] for x in range(len(row))]) == len(row)

    def simple_cull(self, inputPoints, dominates):
        paretoPoints = set()
        candidateRowNr = 0
        dominatedPoints = set()
        while True:
            candidateRow = inputPoints[candidateRowNr]
            inputPoints.remove(candidateRow)
            rowNr = 0
            nonDominated = True
            while len(inputPoints) != 0 and rowNr < len(inputPoints):
                row = inputPoints[rowNr]
                if dominates(candidateRow, row):
                    inputPoints.remove(row)
                    dominatedPoints.add(tuple(row))
                elif dominates(row, candidateRow):
                    nonDominated = False
                    dominatedPoints.add(tuple(candidateRow))
                    rowNr += 1
                else:
                    rowNr += 1

            if nonDominated:
                paretoPoints.add(tuple(candidateRow))

            if len(inputPoints) == 0:
                break
        return paretoPoints, dominatedPoints

    def decay_pheromones(self):
        for i in range(len(self.probability_matrix)):
            for j in range(len(self.probability_matrix[i])):
                if self.probability_matrix[i][j] != 0:
                    self.probability_matrix[i][j] -= self.decay_value
                    if self.probability_matrix[i][j] <= self.minimum_weight:
                        self.probability_matrix[i][j] = self.minimum_weight

    def update_pheromones(self, pheromones, paths):
        for path, pheromone in zip(paths, pheromones):
            for pair in self.pairwise(path):
                indx_1 = self.attractions_list.index(pair[0])
                indx_2 = self.attractions_list.index(pair[1])
                self.probability_matrix[indx_1][indx_2] += pheromone
                self.probability_matrix[indx_2][indx_1] += pheromone

                if self.probability_matrix[indx_1][indx_2] > self.maximum_weight:
                    self.probability_matrix[indx_1][indx_2] = self.maximum_weight
                    self.probability_matrix[indx_2][indx_1] = self.maximum_weight

    def get_pheromones(self, normalized_epoch_criteria):
        random_criteria = random.randint(0, 3)
        criteria_list = [i[random_criteria] for i in normalized_epoch_criteria]
        for index, item in enumerate(criteria_list):
            criteria_list[index] = item/self.divide_pheromones
        return criteria_list

    def normalize_criteria(self, epoch_criteria):
        money_list = [item[0] for item in epoch_criteria]
        pref_list = [item[1] for item in epoch_criteria]
        pop_list = [item[2] for item in epoch_criteria]
        amount_list = [item[3] for item in epoch_criteria]
        if money_list.count(money_list[0]) == len(money_list):
            norm_money_list = [0.5 for i in money_list]
        else:
            norm_money_list = [
                (i - min(money_list))/(max(money_list)-min(money_list)) for i in money_list]
        if pref_list.count(pref_list[0]) == len(pref_list):
            norm_pref_list = [0.5 for i in pref_list]
        else:
            norm_pref_list = [
                (i - min(pref_list))/(max(pref_list)-min(pref_list)) for i in pref_list]
        if pop_list.count(pop_list[0]) == len(pop_list):
            norm_pop_list = [0.5 for i in pop_list]
        else:
            norm_pop_list = [
                (i - min(pop_list))/(max(pop_list)-min(pop_list)) for i in pop_list]
        if amount_list.count(amount_list[0]) == len(amount_list):
            norm_amount_list = [0.5 for i in amount_list]
        else:
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
            money -= money_spend
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
        close_open_time = self.data[destination]["openinghours"]
        if close_open_time[0] != "all day":
            opening_hour = datetime.strptime(close_open_time[0], "%H:%M")
            closing_hour = datetime.strptime(close_open_time[1], "%H:%M")
            if (self.start_time + timedelta(0, total_time)) < opening_hour:
                return False
        total_time += float(self.data[destination]["timespend"])*60

        if close_open_time[0] != "all day":
            if (self.start_time + timedelta(0, total_time)) > closing_hour:
                return False
        total_time += float(
                    self.distances["start"][destination]["duration"])
        total_money = 0
        for attraction in path:
            if attraction != "start":
                money_spend = float(self.data[attraction]["price"])
                total_money += money_spend

        money_dest = float(self.data[destination]["price"])
        total_money += money_dest

        if total_time > self.time_left.total_seconds() or total_money > self.budget:
            return False
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
            with open(self.test_dist) as jf:
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
        with open(self.attration_path) as jf:
            data = json.load(jf)

        if data:
            return data[self.choosen_city]
        else:
            logging.error(f"Attracions data empty! City: {self.choosen_city}")
            sys.exit(-1)

    def load_distances(self):
        with open(self.distances_city) as jf:
            dist = json.load(jf)

        if dist:
            return dist
        else:
            logging.error(f"Distance data empty! City: {self.choosen_city}")
            sys.exit(-1)

    def config(self):
        config = configparser.ConfigParser()
        config.read(os.path.join("config", "config.cfg"))
        logging.basicConfig(format=config["logging"]["format"], level=logging.INFO)
        self.api_key = config["ORS"]["api_key"]
        np.set_printoptions(threshold=sys.maxsize, suppress=True)


if __name__ == "__main__":

    ct_obj = CityTrip(
        "rome",
        "9:00",
        "19:00",
        20,
        (12.48224, 41.8948958),
        ["Koloseum"],
        [3, 3, 3, 4, 3, 4],
        [1, 2, 1, 3, 1, 1])

    sol = ct_obj.main()
    print(sol)
