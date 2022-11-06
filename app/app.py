from flask import Flask, render_template, redirect, request, flash
import os
import sys
import json


app = Flask(__name__)
app.config["SECRET_KEY"] = "mykey"

form_data = {}

"""TO DO
- data validation func
- ahp sliders page
- loading page
- final page
"""


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/planstart', methods=['GET', 'POST'])
def planstart():
    if request.method == "POST":
        city = request.form["city_select"]
        adress = request.form['adress']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        budget = request.form['budget']

        form_data["city"] = city
        form_data["adress"] = adress
        form_data["start_time"] = start_time
        form_data["end_time"] = end_time
        form_data["budget"] = budget
        if not city:
            flash("Please choose city")
        if not adress:
            flash("Please fill adress")
        if not start_time:
            flash("Please fill start_time")
        if not end_time:
            flash("Please fill end_time")
        if not budget:
            flash("Please fill budget")

        if city and adress and start_time and end_time and budget:
            return redirect("preferences")

    list_cities = cities.copy()
    return render_template("planstart.html", list_cities=list_cities)


@app.route('/preferences', methods=['GET', 'POST'])
def preferences():
    if request.method == "POST":
        preferences = [
            request.form['architecture'],
            request.form['churches'],
            request.form['museums'],
            request.form['parks'],
            request.form['recreation'],
            request.form['viewpoints']
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
        return redirect("/remove")  # next page

    return render_template("remove.html", attractions=sorted(attractions))


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
