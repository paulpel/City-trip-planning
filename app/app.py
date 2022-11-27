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

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/addcity', methods=['GET', 'POST'])
def addcity():
    if request.method == "POST":
        new_city = request.form["newcity"]
        path_attr = os.path.join(os.getcwd(), 'data', f'attractions_{new_city}.json')
        path_dist = os.path.join(os.getcwd(), 'data', f'distances_{new_city}.json')
        if os.path.isfile(path_attr):
            flash("Podaj inne miasto, albo zmodyfikuj plik z istniejącym miastem!")
        else:
            dictionary = {
                "attracion_name1": {
                    "category": [
                        "cat1",
                        "cat2"
                    ],
                    "popularity": 0,
                    "rating": 0,
                    "price": 0,
                    "timespend": 0,
                    "openinghours": [
                        "9:00",
                        "19:00"
                    ],
                    "cords": {
                        "latitude": 0,
                        "longitude": 0
                        }
                },
            }
            
            json_object = json.dumps(dictionary, indent=4)
            json_object2 = json.dumps({}, indent=4)
            
            with open(path_attr, "w") as outfile:
                outfile.write(json_object)

            with open(path_dist, "w") as outfile:
                outfile.write(json_object2)

            return redirect("addcity2")

    return render_template("addcity.html")

@app.route('/addcity2', methods=['GET', 'POST'])
def addcity2():
    return render_template("addcity2.html")

@app.route('/map', methods=['GET', 'POST'])
def map():
    if request.method == "POST":
        adress = request.form["adress"]
        adress = adress.split(",")
        form_data["adress"] = (float(adress[1]), float(adress[0]))
        return redirect("preferences")
    return render_template("map.html", city=form_data["city"])


@app.route('/planstart', methods=['GET', 'POST'])
def planstart():
    if request.method == "POST":
        city = request.form["city_select"]
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        budget = request.form['budget']

        if not city:
            flash("Proszę wybierz miasto")
        if not start_time:
            flash("Proszę podaj czas rozpoczęcia")
        if not end_time:
            flash("Proszę podaj czas zakończenia")
        if not budget:
            flash("Proszę podaj budżet")

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
    data = load_data(form_data["city"])
    attractions = list(data.keys())

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

    return render_template("final.html", solutions=solutions)


@app.route('/git')
def github():
    return redirect("https://github.com/paulpel/City-trip-planning", code=302)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


def load_data(city):
    path = os.path.join(os.getcwd(), 'data', f'attractions_{city}.json')
    with open(path) as jf:
        data = json.load(jf)

    if data:
        return data
    else:
        sys.exit(-1)


if __name__ == "__main__":
    mypath = os.path.join(os.getcwd(), 'data')
    onlyfiles = [f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]
    cities = [f.split('.')[0].split('_')[1] for f in onlyfiles if "attractions" in f]
    app.run(debug=True)
