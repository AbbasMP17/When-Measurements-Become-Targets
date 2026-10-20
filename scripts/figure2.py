import os
import json
from collections import Counter
from datetime import datetime

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

DATA_DIR = "../dataset/rovista/"

prefix_dates = {}
prefix_origin = {}
all_dates = set()

START_DATE = "20230101"
END_DATE = "20260707"

# ----------------------------------------------------------
# Load data
# ----------------------------------------------------------
for file in os.listdir(DATA_DIR):
    if not file.startswith("rovista_prefix_"):
        continue

    date = file.split("_")[-1].replace(".json", "")

    if not (START_DATE <= date <= END_DATE):
        continue

    all_dates.add(date)

    with open(os.path.join(DATA_DIR, file), "r") as f:
        data = json.load(f)

    for entry in data:
        prefix = entry["prefix"]
        asn = entry["targetAsn"]

        prefix_dates.setdefault(prefix, set()).add(date)
        prefix_origin.setdefault(prefix, []).append(asn)

# ----------------------------------------------------------
# Prefix labels
# ----------------------------------------------------------
PUBLIC_PREFIXES = {
    "103.21.244.0/24",        # Is BGP Safe Yet?
    "2606:4700:7000::/48",    # Is BGP Safe Yet? (IPv6)
    #"193.43.75.0/24",         # RoVista
}

SHADOW_PREFIXES = {
     "193.43.75.0/24",         # RoVista
    "188.164.158.0/23",
    "213.219.247.0/24",
    "91.124.127.0/24",
}

prefix_label = {}

for prefix, asns in prefix_origin.items():
    most_common_asn = Counter(asns).most_common(1)[0][0]

    if prefix in PUBLIC_PREFIXES:
        prefix_label[prefix] = "† " + prefix 

    elif prefix in SHADOW_PREFIXES:
        prefix_label[prefix] = "§ " + prefix 

    else:
        prefix_label[prefix] = prefix

# ----------------------------------------------------------
# Sort dates
# ----------------------------------------------------------
sorted_dates = sorted(all_dates)

# ----------------------------------------------------------
# Keep top prefixes
# ----------------------------------------------------------
TOP_N = 10

prefix_items = sorted(
    prefix_dates.items(),
    key=lambda x: len(x[1]),
    reverse=True,
)[:TOP_N]

print(f"Plotting Top {len(prefix_items)} prefixes:")

for prefix, dates in prefix_items:
    print(f"{prefix}: {len(dates)} days")

# ----------------------------------------------------------
# Build matrix
# ----------------------------------------------------------
matrix = np.zeros((len(prefix_items), len(sorted_dates)))

for i, (prefix, dates) in enumerate(prefix_items):
    for j, d in enumerate(sorted_dates):
        if d in dates:
            matrix[i, j] = 1

# ----------------------------------------------------------
# Plot style
# ----------------------------------------------------------
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],

    "font.size": 11,
    "axes.labelsize": 13,
    "axes.titlesize": 13,

    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,

    "axes.linewidth": 0.8,

    "pdf.fonttype": 42,
    "ps.fonttype": 42,

    "figure.dpi": 600,
    "savefig.dpi": 600,
})

fig, ax = plt.subplots(
    figsize=(7.2, 4.0),
    constrained_layout=True,
)

# ----------------------------------------------------------
# Binary colormap
# ----------------------------------------------------------
cmap = ListedColormap([
    "#F2F2F2",   # Not visible
    "#4C78A8",   # Visible
])

im = ax.imshow(
    matrix,
    cmap=cmap,
    aspect="auto",
    interpolation="nearest",
    vmin=0,
    vmax=1,
)

# ----------------------------------------------------------
# Dates
# ----------------------------------------------------------
date_objs = [
    datetime.strptime(d, "%Y%m%d")
    for d in sorted_dates
]

step = max(1, len(date_objs) // 10)

ax.set_xticks(range(0, len(date_objs), step))
ax.set_xticklabels(
    [
        date_objs[i].strftime("%Y-%m")
        for i in range(0, len(date_objs), step)
    ],
    rotation=45,
    ha="right",
)

# ----------------------------------------------------------
# Year separators
# ----------------------------------------------------------
previous_year = None

for i, d in enumerate(date_objs):

    if previous_year is None:
        previous_year = d.year
        continue

    if d.year != previous_year:
        ax.axvline(
            i - 0.5,
            color="white",
            linewidth=1.2,
        )
        previous_year = d.year

# ----------------------------------------------------------
# Y labels
# ----------------------------------------------------------
ax.set_yticks(range(len(prefix_items)))
ax.set_yticklabels(
    [prefix_label[p] for p, _ in prefix_items]
)

# ----------------------------------------------------------
# Axis labels
# ----------------------------------------------------------
ax.set_xlabel("Date", fontweight="bold")
ax.set_ylabel("Invalid Prefix", fontweight="bold")

# No title
# The paper caption explains the figure.

# ----------------------------------------------------------
# Ticks
# ----------------------------------------------------------
ax.tick_params(
    axis="both",
    which="major",
    length=4,
    width=0.8,
)

# ----------------------------------------------------------
# Spines
# ----------------------------------------------------------
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

ax.spines["left"].set_color("0.6")
ax.spines["bottom"].set_color("0.6")

# ----------------------------------------------------------
# Legend
# ----------------------------------------------------------
legend = ax.legend(
    handles=[
        Patch(
            facecolor="#F2F2F2",
            edgecolor="black",
            label="Not visible",
        ),
        Patch(
            facecolor="#4C78A8",
            edgecolor="black",
            label="Visible",
        ),
    ],
    frameon=False,
    ncol=2,
    loc="lower center",
    bbox_to_anchor=(0.5, 1.02),
)

# ----------------------------------------------------------
# Save
# ----------------------------------------------------------
plt.savefig(
    "../hotnets26/figures/rovista_visibility.pdf",
    bbox_inches="tight",
)

