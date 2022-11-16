from flask import Flask, render_template, redirect, request, flash
import os
import sys
import json
from main import CityTrip


app = Flask(__name__)
app.config["SECRET_KEY"] = "mykey"

form_data = {}

ahp_dict = {
    "1": 9,
    "2": 7,
    "3": 5,
    "4": 3,
    "5": 1,
    "6": 1/3,
    "7": 1/5,
    "8": 1/7,
    "9": 1/9,
    }

"""TO DO
- data validation func
- loading page
- export to excel
- time form change
"""


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/map', methods=['GET', 'POST'])
def map():
    if request.method == "POST":
        adress = request.form["adress"]
        adress = adress.split(",")
        form_data["adress"] = (adress[1], adress[0])
        return redirect("preferences")
    return render_template("map.html")


@app.route('/planstart', methods=['GET', 'POST'])
def planstart():
    if request.method == "POST":
        city = request.form["city_select"]
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        budget = request.form['budget']

        if not city:
            flash("Please choose city")
        if not start_time:
            flash("Please fill start_time")
        if not end_time:
            flash("Please fill end_time")
        if not budget:
            flash("Please fill budget")

        if city and start_time and end_time and budget:
            form_data["city"] = city
            form_data["start_time"] = start_time
            form_data["end_time"] = end_time
            form_data["budget"] = float(budget)
            return redirect("map")

    list_cities = cities.copy()
    return render_template("planstart.html", list_cities=list_cities)


@app.route('/preferences', methods=['GET', 'POST'])
def preferences():
    if request.method == "POST":
        preferences = [
            int(request.form['architecture']),
            int(request.form['churches']),
            int(request.form['museums']),
            int(request.form['parks']),
            int(request.form['recreation']),
            int(request.form['viewpoints'])
        ]
        form_data["preferences"] = preferences
        return redirect('/remove')

    return render_template("preferences.html")


@app.route('/remove', methods=['GET', 'POST'])
def remove():
    attractions = list(data[form_data["city"]].keys())

    if request.method == "POST":
        forbidden_attr = list(request.form)
        form_data["forbidden_attr"] = forbidden_attr
        return redirect("/ahp")  # next page

    return render_template("remove.html", attractions=sorted(attractions))


@app.route('/ahp', methods=['GET', 'POST'])
def ahp():

    if request.method == "POST":
        money_pref = ahp_dict[request.form["money_pref"]]
        money_popular = ahp_dict[request.form["money_popular"]]
        money_amount = ahp_dict[request.form["money_amount"]]
        pref_popular = ahp_dict[request.form["pref_popular"]]
        pref_amount = ahp_dict[request.form["pref_amount"]]
        popular_amount = ahp_dict[request.form["popular_amount"]]

        form_data["ahp"] = [money_pref, money_popular, money_amount, pref_popular, pref_amount, popular_amount]
        return redirect("/final")  # next page

    return render_template("ahp.html")


@app.route('/final', methods=['GET', 'POST'])
def final():
    for key, value in form_data.items():
        print(type(value), value)
    city_obj = CityTrip(
        form_data["city"],
        form_data["start_time"],
        form_data["end_time"],
        form_data["budget"],
        form_data["adress"],
        form_data["forbidden_attr"],
        form_data["preferences"],
        form_data["ahp"]
    )
    solutions = city_obj.main()
    for sol in solutions:
        print(sol)

    return render_template("final.html", solutions=solutions)


@app.route('/git')
def github():
    return redirect("https://github.com/paulpel/City-trip-planning", code=302)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


def load_data(path):
    with open(path) as jf:
        data = json.load(jf)

    if data:
        return data
    else:
        sys.exit(-1)


if __name__ == "__main__":
    attration_path = os.path.join("data", "attractions.json")
    data = load_data(attration_path)
    cities = list(data.keys())
    app.run(debug=True)
