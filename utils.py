import json
from collections import Counter
import matplotlib.pyplot as plt


def load_data():
    with open("attractions.json") as jf:
        data = json.load(jf)
    return data


def calc_attr_cat(data):
    cat_list = []

    for attr, charac in data["rome"].items():
        for elem in charac["category"]:
            cat_list.append(str(elem))

    k = Counter(cat_list).keys()
    v = Counter(cat_list).values()

    print(k)
    print(v)


def plot_coord(data):
    x = []
    y = []
    labels = []

    for k, val in data["rome"].items():
        x.append(val["cords"]["latitude"])
        y.append(val["cords"]["longitude"])
        labels.append(k)

    plt.scatter(x, y)
    for i, txt in enumerate(labels):
        plt.annotate(txt, (x[i], y[i]))
    plt.show()


def calc(data):
    print(len(data["rome"].keys()))


if __name__ == "__main__":
    data = load_data()
    calc(data)
