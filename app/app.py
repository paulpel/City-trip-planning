from flask import Flask, render_template, redirect
import os
import sys
import json


app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/planstart')
def planstart():
    return render_template("planstart.html")


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
