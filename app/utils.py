import configparser
import json
import time
import os

import openrouteservice


def calc_distances(city):
    config = configparser.ConfigParser()
    config.read('config.cfg')
    api_key = config["ORS"]["api_key"]

    client = openrouteservice.Client(key=api_key)

    dist_path = os.path.join(os.getcwd(), 'data', f'distances_{city}.json')
    attractions_path = os.path.join(os.getcwd(), 'data', f'attractions_{city}.json')

    with open(dist_path) as jf:
        dist = json.load(jf)

    with open(attractions_path) as jf:
        data = json.load(jf)

    all_attractions = list(data.keys())

    for attraction_a in all_attractions:
        if attraction_a not in dist:
            dist[attraction_a] = {}

            cords_a = (
                data[attraction_a]["cords"]["longitude"],
                data[attraction_a]["cords"]["latitude"]
                )

            for attraction_b in all_attractions:
                if attraction_a != attraction_b:
                    cords_b = (
                        data[attraction_b]["cords"]["longitude"],
                        data[attraction_b]["cords"]["latitude"]
                        )
                    try:
                        res = client.directions(
                            (cords_a, cords_b),
                            profile="foot-walking")["routes"][0]["summary"]
                    except Exception:
                        print("Something wrong. Check API limit!")

                    dist[attraction_a][attraction_b] = res
                    time.sleep(1.5)
        else:
            continue
        break

    with open(dist_path, "w") as jf:
        json.dump(dist, jf, indent=4)
