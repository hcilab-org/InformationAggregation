from flask import Flask
from flask import render_template, request, make_response

import os
import shutil
import json
import math
import csv
import uuid
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
from scipy.stats import norm
from collections import Counter

app = Flask(__name__, static_url_path='/static')
BASE_DIR = os.path.dirname(__file__)
DISCREPANCY_TABLE = [(0.1, 4.3, 11.4, "4"),
                     (0.2, 3, 8, "3"),
                     (0.3, 2.5, 6.7, "2"),
                     (0.4, 2.1, 5.7, "1"),
                     (0.5, 1.9, 5, "0"),
                     (0.6, 2.1, 5.7, "1"),
                     (0.7, 2.5, 6.7, "2"),
                     (0.8, 3, 8, "3"),
                     (0.9, 4.3, 11.4, "4")
                     ]


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    with open(os.path.join(BASE_DIR, "means.csv"), 'rb') as f:
        csv_data = csv.reader(f)

        data = json.loads(request.get_data())
        folder = os.path.join(BASE_DIR, "static", "img")
        response = {}

        var1 = float(data["var1"])
        var2 = float(data["var2"])
        val1 = float(data["val1"])
        val2 = float(data["val2"])

        weighting1 = var2 / (var1 + var2) if (var1 + var2) != 0 else 0
        weighting2 = var1 / (var1 + var2) if (var1 + var2) != 0 else 0
        estimate_optimal = weighting1 * val1 + weighting2 * val2

        if var1 <= var2:
            sd = math.sqrt(var1)
        else:
            sd = math.sqrt(var2)
        discrepancy = math.fabs(val1 - val2) / sd if sd != 0 else -1

        csv_discrepancy = "0"
        csv_weighting = "0"
        if weighting1 != 0:
            rounded_weighting1 = round(weighting1, 1)
            if rounded_weighting1 == 0:
                rounded_weighting1 = 0.1
            elif rounded_weighting1 == 1:
                rounded_weighting1 = 0.9
            table_tuple = ()
            for t in DISCREPANCY_TABLE:
                if rounded_weighting1 in t:
                    table_tuple = t
                    break
            if math.fabs(table_tuple[1] - discrepancy) <= math.fabs(table_tuple[2] - discrepancy):
                csv_discrepancy = "1"
            else:
                csv_discrepancy = "2"
            csv_weighting = table_tuple[3]

        chosen = []
        for i in range(1, 5):
            mean = 0
            for row in csv_data:
                if row[1] == csv_weighting and row[2] == csv_discrepancy and row[3] == str(i):
                    mean = row[4]
                    break
            weight_error = float(mean)
            if weighting1 >= weighting2:
                weighting1_pp = weighting1 - weight_error
                weighting2_pp = weighting2 + weight_error
            else:
                weighting1_pp = weighting1 + weight_error
                weighting2_pp = weighting2 - weight_error
            estimate_chosen = weighting1_pp * val1 + weighting2_pp * val2
            chosen.append(estimate_chosen)
            response["estimate_chosen_" + str(i)] = round(estimate_chosen, 2)
            response["distance_" + str(i)] = round(math.fabs(estimate_optimal - estimate_chosen), 2)
        response["estimate_optimal"] = round(estimate_optimal, 2)

    response["paragraph"] = "#text1" if 0.4 < weighting1 < 0.6 else "#text2"

    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.mkdir(folder)
    response["point1"] = point(val1, val2, var1, var2, estimate_optimal, chosen[0])
    response["point2"] = point(val2, val1, var2, var1, estimate_optimal, chosen[0])
    response["line1"] = line(val1, val2, var1, var2, estimate_optimal, chosen[1])
    response["line2"] = line(val2, val1, var2, var1, estimate_optimal, chosen[1])
    response["dot1"] = dot(val1, val2, var1, var2, estimate_optimal, chosen[2])
    response["dot2"] = dot(val2, val1, var2, var1, estimate_optimal, chosen[2])
    response["dist1"] = dist(val1, val2, var1, var2, estimate_optimal, chosen[3])
    response["dist2"] = dist(val2, val1, var2, var1, estimate_optimal, chosen[3])

    return make_response(json.dumps(response))


def point(val, val2, var, var2, estimate_optimal, estimate_chosen):
    lower1 = norm.ppf(q=0.001, loc=val, scale=var)
    upper1 = norm.ppf(q=0.999, loc=val, scale=var)
    lower2 = norm.ppf(q=0.001, loc=val2, scale=var2)
    upper2 = norm.ppf(q=0.999, loc=val2, scale=var2)
    lower = lower1 if lower1 <= lower2 else lower2
    upper = upper1 if upper1 >= upper2 else upper2

    fig_point = plt.figure(facecolor='white', figsize=(10, 4))
    ax_point = plt.axes(frameon=True)
    ax_point.spines['right'].set_visible(False)
    ax_point.spines['top'].set_visible(False)
    ax_point.spines['left'].set_visible(False)
    ax_point.spines['bottom'].set_color('#5d6778')
    ax_point.tick_params(axis='x', colors='#5d6778')
    ax_point.set_ylim(0, 2)
    ax_point.axes.get_yaxis().set_visible(False)
    ax_point.get_xaxis().tick_bottom()
    plt.axvline(x=val, zorder=-1, color="#98a4b8")
    plt.axvline(x=estimate_chosen, zorder=-1, color="#FF0000", label="estimate chosen")
    plt.axvline(x=estimate_optimal, zorder=-1, color="#0c8b00", label="estimate optimal")
    plt.legend(loc='upper right')
    plt.scatter([val], [1], color="#73A7E3", linewidth=4.0, marker='x', s=400)
    ax_point.set_xlim(lower, upper)
    plt.xticks(np.arange(round(lower), round(upper + 1), 5.0))
    fig_point.tight_layout()
    filename = str(uuid.uuid4()) + ".png"
    fig_point.savefig(os.path.join(BASE_DIR, "static", "img", filename), bbox_inches='tight')

    return filename


def line(val, val2, var, var2, estimate_optimal, estimate_chosen):
    lower1 = norm.ppf(q=0.001, loc=val, scale=var)
    upper1 = norm.ppf(q=0.999, loc=val, scale=var)
    lower2 = norm.ppf(q=0.001, loc=val2, scale=var2)
    upper2 = norm.ppf(q=0.999, loc=val2, scale=var2)
    lower = lower1 if lower1 <= lower2 else lower2
    upper = upper1 if upper1 >= upper2 else upper2

    left_dot = norm.ppf(q=0.05, loc=val, scale=var)
    right_dot = norm.ppf(q=0.95, loc=val, scale=var)

    fig_line = plt.figure(facecolor='white', figsize=(10, 4))
    ax_line = plt.axes(frameon=True)
    ax_line.spines['right'].set_visible(False)
    ax_line.spines['top'].set_visible(False)
    ax_line.spines['left'].set_visible(False)
    ax_line.spines['bottom'].set_color('#5d6778')
    ax_line.tick_params(axis='x', colors='#5d6778')
    ax_line.set_ylim(0, 2)
    ax_line.get_xaxis().tick_bottom()
    plt.axvline(x=val, zorder=-1, color="#98a4b8")
    plt.axvline(x=estimate_chosen, zorder=-1, color="#FF0000", label="estimate chosen")
    plt.axvline(x=estimate_optimal, zorder=-1, color="#0c8b00", label="estimate optimal")
    plt.legend(loc='upper right')
    plt.plot([left_dot, val, right_dot], [1, 1, 1], color="#73A7E3", linewidth=4.0)
    plt.scatter([left_dot, right_dot], [1, 1], color="#73A7E3", linewidth=4.0, marker='|', s=400)
    plt.scatter([val], [1], color="#73A7E3", linewidth=4.0, marker='x', s=400)
    ax_line.set_xlim(lower, upper)
    ax_line.axes.get_yaxis().set_visible(False)
    plt.xticks(np.arange(round(lower), round(upper + 1), 5.0))
    fig_line.tight_layout()
    filename = str(uuid.uuid4()) + ".png"
    fig_line.savefig(os.path.join(BASE_DIR, "static", "img", filename), bbox_inches='tight')

    return filename


def dot(val, val2, var, var2, estimate_optimal, estimate_chosen):
    lower1 = norm.ppf(q=0.001, loc=val, scale=var)
    upper1 = norm.ppf(q=0.999, loc=val, scale=var)
    lower2 = norm.ppf(q=0.001, loc=val2, scale=var2)
    upper2 = norm.ppf(q=0.999, loc=val2, scale=var2)
    lower = lower1 if lower1 <= lower2 else lower2
    upper = upper1 if upper1 >= upper2 else upper2

    temp_ppf1 = round(norm.ppf(q=0.05, loc=val, scale=var))  # 1
    temp_ppf2 = round(norm.ppf(q=0.10, loc=val, scale=var)) - 1 if var == math.sqrt(12) else round(
        norm.ppf(q=0.10, loc=val, scale=var))  # 1
    temp_ppf3 = round(norm.ppf(q=0.15, loc=val, scale=var))  # 1
    temp_ppf4 = round(norm.ppf(q=0.20, loc=val, scale=var))  # 2
    temp_ppf5 = round(norm.ppf(q=0.25, loc=val, scale=var))  # 2
    temp_ppf6 = round(norm.ppf(q=0.30, loc=val, scale=var))  # 3
    temp_ppf7 = round(norm.ppf(q=0.35, loc=val, scale=var))  # 3
    temp_ppf8 = round(norm.ppf(q=0.40, loc=val, scale=var)) - 1 if var == math.sqrt(4) else round(
        norm.ppf(q=0.40, loc=val, scale=var))  # 2
    temp_ppf9 = round(norm.ppf(q=0.45, loc=val, scale=var))  # 2
    temp_ppf10 = round(norm.ppf(q=0.50, loc=val, scale=var))  # 1
    temp_ppf11 = round(norm.ppf(q=0.55, loc=val, scale=var))  # 1
    temp_ppf12 = round(norm.ppf(q=0.60, loc=val, scale=var)) + 1 if var == math.sqrt(4) else round(
        norm.ppf(q=0.60, loc=val, scale=var))  # 1
    temp_ppf13 = round(norm.ppf(q=0.65, loc=val, scale=var))  # 1
    temp_ppf14 = round(norm.ppf(q=0.70, loc=val, scale=var))  # 2
    temp_ppf15 = round(norm.ppf(q=0.75, loc=val, scale=var))  # 2
    temp_ppf16 = round(norm.ppf(q=0.80, loc=val, scale=var))  # 3
    temp_ppf17 = round(norm.ppf(q=0.85, loc=val, scale=var))  # 3
    temp_ppf18 = round(norm.ppf(q=0.90, loc=val, scale=var)) + 1 if var == math.sqrt(12) else round(
        norm.ppf(q=.9, loc=val, scale=var))  # 2
    temp_ppf19 = round(norm.ppf(q=0.95, loc=val, scale=var))  # 2

    dotplot = []
    dotplot.extend([temp_ppf1, temp_ppf2, temp_ppf3, temp_ppf4, temp_ppf5, temp_ppf6,
                    temp_ppf7, temp_ppf8, temp_ppf9, temp_ppf10, temp_ppf11, temp_ppf12, temp_ppf13, temp_ppf14,
                    temp_ppf15, temp_ppf16,
                    temp_ppf17, temp_ppf18, temp_ppf19])
    counts = Counter(dotplot)

    dotplot_x = []
    dotplot_y = []
    for key, value in counts.iteritems():
        for i in range(1, value + 1):
            dotplot_x.append(key)
            dotplot_y.append(i)

    # doing the plotting
    fig_dot = plt.figure(facecolor='white', figsize=(10, 4))
    ax_dot = plt.axes(frameon=True)
    ax_dot.spines['right'].set_visible(False)
    ax_dot.spines['top'].set_visible(False)
    ax_dot.spines['left'].set_visible(False)
    ax_dot.spines['bottom'].set_color('#5d6778')
    ax_dot.tick_params(axis='x', colors='#5d6778')
    ax_dot.get_xaxis().tick_bottom()
    plt.axvline(x=val, zorder=-1, color="#98a4b8")
    plt.axvline(x=estimate_chosen, zorder=-1, color="#FF0000", label="estimate chosen")
    plt.axvline(x=estimate_optimal, zorder=-1, color="#0c8b00", label="estimate optimal")
    plt.legend(loc='upper right')
    plt.scatter(dotplot_x, dotplot_y, color="#73A7E3", s=100, zorder=100, clip_on=False)
    plt.ylim(1, 12)
    ax_dot.axes.get_yaxis().set_visible(False)
    ax_dot.set_xlim(lower, upper)
    plt.xticks(np.arange(round(lower), round(upper + 1), 5.0))
    fig_dot.tight_layout()
    filename = str(uuid.uuid4()) + ".png"
    fig_dot.savefig(os.path.join(BASE_DIR, "static", "img", filename), bbox_inches='tight')

    return filename


def dist(val, val2, var, var2, estimate_optimal, estimate_chosen):
    lower1 = norm.ppf(q=0.001, loc=val, scale=var)
    upper1 = norm.ppf(q=0.999, loc=val, scale=var)
    lower2 = norm.ppf(q=0.001, loc=val2, scale=var2)
    upper2 = norm.ppf(q=0.999, loc=val2, scale=var2)
    lower = lower1 if lower1 <= lower2 else lower2
    upper = upper1 if upper1 >= upper2 else upper2

    x = np.linspace(lower, upper, 100)
    y = mlab.normpdf(x, val, var) if var != 0 else np.linspace(0, 0, 100)
    y2 = mlab.normpdf(x, val2, var2) if var2 != 0 else np.linspace(0, 0, 100)

    fig_norm = plt.figure(facecolor='white', figsize=(10, 4))
    ax_norm = plt.axes(frameon=True)
    ax_norm.spines['right'].set_visible(False)
    ax_norm.spines['top'].set_visible(False)
    ax_norm.spines['left'].set_visible(False)
    ax_norm.spines['bottom'].set_color('#5d6778')
    ax_norm.tick_params(axis='x', colors='#5d6778')
    ax_norm.tick_params(axis='y', colors='#5d6778')
    ax_norm.get_xaxis().tick_bottom()
    ax_norm.set_autoscale_on(False)
    plt.axvline(x=val, zorder=-1, color="#98a4b8")
    plt.axvline(x=estimate_chosen, zorder=-1, color="#FF0000", label="estimate chosen")
    plt.axvline(x=estimate_optimal, zorder=-1, color="#0c8b00", label="estimate optimal")
    plt.legend(loc='upper right')
    ax_norm.axes.get_yaxis().set_visible(False)
    plt.plot(x, y, color="#73A7E3", linewidth=3.0)
    ax_norm.set_xlim(lower, upper)
    y_upper = y.max() + y.max() * 0.1 if y.max() >= y2.max() else y2.max() + y2.max() * 0.1
    ax_norm.set_ylim(0, y_upper)
    plt.xticks(np.arange(round(lower), round(upper + 1), 5.0))
    fig_norm.tight_layout()
    filename = str(uuid.uuid4()) + ".png"
    fig_norm.savefig(os.path.join(BASE_DIR, "static", "img", filename), bbox_inches='tight')

    return filename


if __name__ == '__main__':
    app.run()
