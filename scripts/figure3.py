import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Patch

REACHABILITY_FILE = "../dataset/reachability.csv"

# ------------------------------------------------------------------
# Publication-quality plotting style (HotNets / SIGCOMM / NSDI)
# ------------------------------------------------------------------
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],

    "font.size": 12,
    "axes.labelsize": 14,
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "axes.labelweight": "bold",

    "xtick.labelsize": 11,
    "ytick.labelsize": 11,
    "legend.fontsize": 11,

    "axes.linewidth": 0.8,

    "pdf.fonttype": 42,
    "ps.fonttype": 42,

    "figure.dpi": 600,
    "savefig.dpi": 600,
})

df = pd.read_csv(REACHABILITY_FILE)

# ------------------------------------------------------------------
# IP -> Prefix mapping
# ------------------------------------------------------------------
ip_to_prefix = {
    # High Visibility
    "103.21.244.8": "103.21.244.0/24",
    "104.17.230.6": "104.17.224.0/20",
    "2606:4700:7000::6715:f409": "2606:4700:7000::/48",
    "2606:4700::6811:e706": "2606:4700::/44",
    "188.164.158.1": "188.164.158.0/23",
    "45.202.113.1": "45.202.113.0/24",
    "213.219.247.1": "213.219.247.0/24",
    "91.124.127.1": "91.124.127.0/24",
    "216.198.53.1": "216.198.53.0/24",

    # Unicast
    "154.207.88.1": "154.207.88.0/24",
    "203.95.192.1": "203.95.192.0/24",

    # Medium Visibility
    "2605:59c0:5020::1": "2605:59c0:5020::/48",
    "2401:e320:1000::1": "2401:e320:1000::/48",
    "46.16.33.10": "46.16.33.0/24",
    "193.228.162.10": "193.228.162.0/24",

    # Low Visibility
    "193.43.75.5": "193.43.75.0/24",
    "185.247.167.79": "185.247.167.0/24",
}

# ------------------------------------------------------------------
# Keep only invalid targets
# ------------------------------------------------------------------
invalid_df = df[df["prefix_status"] == "invalid"].copy()

# Convert IPs to prefixes
invalid_df["prefix"] = invalid_df["target"].map(ip_to_prefix)

# Exclude one target
invalid_df = invalid_df[
    invalid_df["target"] != "45.202.113.1"
]

invalid_df = invalid_df[
    invalid_df["target"] != "154.207.88.1"
]

# ------------------------------------------------------------------
# Compute reachability
# ------------------------------------------------------------------
results = []

for prefix, group in invalid_df.groupby("prefix"):

    total_asns = group["source_asn"].nunique()

    reached_asns = (
        group[group["reached"] == 1]["source_asn"]
        .nunique()
    )

    reachability = (
        100 * reached_asns / total_asns
        if total_asns > 0 else 0
    )

    protocol = "IPv6" if ":" in prefix else "IPv4"

    results.append({
        "Prefix": prefix,
        "Reachability": reachability,
        "Reached_ASNs": reached_asns,
        "Total_ASNs": total_asns,
        "Protocol": protocol
    })

plot_df = pd.DataFrame(results)

plot_df = plot_df.sort_values(
    "Reachability",
    ascending=True
)

PUBLIC_PREFIXES = {
    "103.21.244.0/24",
    "2606:4700:7000::/48",
}

SHADOW_PREFIXES = {
    "188.164.158.0/23",
    "213.219.247.0/24",
    "91.124.127.0/24",
}

ROVISTA_PREFIXES = {
    "193.43.75.0/24",
}

# --------------------------------------------------
# Add symbols to prefix labels
# --------------------------------------------------
def format_prefix(prefix):
    if prefix in PUBLIC_PREFIXES:
        return "† " + prefix
    elif prefix in SHADOW_PREFIXES:
        return "‡ " + prefix
    elif prefix in ROVISTA_PREFIXES:
        return "§ " + prefix
    return prefix

plot_df["DisplayPrefix"] = plot_df["Prefix"].apply(format_prefix)

# ------------------------------------------------------------------
# Colors (colorblind friendly)
# ------------------------------------------------------------------
colors = {
    "IPv4": "#4C78A8",
    "IPv6": "#F58518",
}

# ------------------------------------------------------------------
# Figure
# ------------------------------------------------------------------
fig, ax = plt.subplots(
    figsize=(7.2, 4.0),
    constrained_layout=True,
)

bars = ax.barh(
    plot_df["DisplayPrefix"],   # <-- Use the formatted labels
    plot_df["Reachability"],
    color=plot_df["Protocol"].map(colors),
    edgecolor="black",
    linewidth=0.5,
    height=0.65,
)

# ------------------------------------------------------------------
# Labels (always outside bars)
# ------------------------------------------------------------------
for bar, pct, reached, total in zip(
    bars,
    plot_df["Reachability"],
    plot_df["Reached_ASNs"],
    plot_df["Total_ASNs"],
):

    ax.text(
        pct + 1.5,
        bar.get_y() + bar.get_height() / 2,
        f"{pct:.1f}% ({reached}/{total})",
        va="center",
        ha="left",
        fontsize=9,
        color="black",
    )

# ------------------------------------------------------------------
# Legend
# ------------------------------------------------------------------
legend_handles = [
    Patch(
        facecolor=colors["IPv4"],
        edgecolor="black",
        label="IPv4",
    ),
    Patch(
        facecolor=colors["IPv6"],
        edgecolor="black",
        label="IPv6",
    ),
]

ax.legend(
    handles=legend_handles,
    frameon=False,
    ncol=2,
    loc="lower center",
    bbox_to_anchor=(0.5, 1.02),
)

# ------------------------------------------------------------------
# Axes
# ------------------------------------------------------------------
ax.set_xlim(0, 110)

ax.set_xlabel("Reachable ASes (%)", fontweight="bold")
ax.set_ylabel("Invalid Prefix", fontweight="bold")

# Caption should explain the figure.
# ax.set_title("Reachability of Invalid Targets")

# ------------------------------------------------------------------
# Grid
# ------------------------------------------------------------------
ax.set_axisbelow(True)
ax.grid(
    axis="x",
    linestyle="--",
    linewidth=0.6,
    color="0.85",
)

# ------------------------------------------------------------------
# Clean spines
# ------------------------------------------------------------------
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_color("0.65")
ax.spines["bottom"].set_color("0.65")

# ------------------------------------------------------------------
# Save
# ------------------------------------------------------------------
plt.savefig(
    "../hotnets26/figures/reachability.pdf",
    bbox_inches="tight",
)
