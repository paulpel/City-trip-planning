import configparser
import json
import time

import openrouteservice


def calc_distances(data, choosen_city, file_name):
    config = configparser.ConfigParser()
    config.read('config.cfg')
    api_key = config["ORS"]["api_key"]

    client = openrouteservice.Client(key=api_key)

    with open(file_name) as jf:
        dist = json.load(jf)

    all_attractions = list(data[choosen_city].keys())

    for attraction_a in all_attractions:
        if attraction_a not in dist:
            dist[attraction_a] = {}

            cords_a = (
                data[choosen_city][attraction_a]["cords"]["longitude"],
                data[choosen_city][attraction_a]["cords"]["latitude"]
                )

            for attraction_b in all_attractions:
                if attraction_a != attraction_b:
                    cords_b = (
                        data[choosen_city][attraction_b]["cords"]["longitude"],
                        data[choosen_city][attraction_b]["cords"]["latitude"]
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

    with open(file_name, "w") as jf:
        json.dump(dist, jf, indent=4)
