"""Charts and a table from data: a week of the orders service's requests, hour by hour, read from
requests.csv with pandas, drawn with seaborn in the theme, and summed up in a table. Writes
spread.svg, heatmap.svg and report.html beside itself:

    .venv\\Scripts\\python.exe .claude\\skills\\rich-content\\examples\\data\\build.py

An Excel file reads the same way: pd.read_excel("book.xlsx", sheet_name="…") (openpyxl).
"""
from pathlib import Path

import pandas as pd
import seaborn as sns

from tools.chartstyle import C_SERIES, plt, save_chart, sequential
from tools.html import Page

HERE = Path(__file__).resolve().parent
df = pd.read_csv(HERE / "requests.csv")
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# 1 -- how p99 spreads, endpoint by endpoint (a box per endpoint: the middle half, the whiskers, outliers)
fig, ax = plt.subplots(figsize=(6.4, 2.4))
sns.boxplot(data=df, x="p99_ms", y="endpoint", hue="endpoint", palette=C_SERIES[:3], legend=False, ax=ax,
            width=0.55, fliersize=2.5, linewidth=1)
ax.set_title("How p99 spreads over the week's hours")
ax.set_xlabel("p99, ms")
ax.set_ylabel("")
spread = save_chart(fig, HERE / "spread.svg")

# 2 -- when the slow hours are: p99 of the busiest read, day by hour
busiest = df[df["endpoint"] == "GET /orders/{id}"].pivot(index="day", columns="hour", values="p99_ms").loc[DAYS]
fig, ax = plt.subplots(figsize=(6.4, 2.5))
sns.heatmap(busiest, cmap=sequential("async"), ax=ax, linewidths=0.5, linecolor=plt.rcParams["grid.color"],
            cbar_kws={"label": "p99, ms", "pad": 0.02})
ax.set_title("GET /orders/{id}: p99 by day and hour")
ax.set_xlabel("hour")
ax.set_ylabel("")
ax.tick_params(axis="y", rotation=0)
heatmap = save_chart(fig, HERE / "heatmap.svg")

# 3 -- the week in a table
by = df.groupby("endpoint")
summary = pd.DataFrame({"Requests": by["requests"].sum(), "p50 median, ms": by["p50_ms"].median(),
                        "p99 median, ms": by["p99_ms"].median()})
summary = summary.sort_values(by="Requests", ascending=False).rename_axis("Endpoint").reset_index()

total = f"{int(df['requests'].to_numpy().sum()):,}".replace(",", chr(0x202F))   # 1 234 567, narrow spaces
page = Page("Orders service: the week in data", eyebrow="Weekly report",
            lead=f"{total} requests over {len(DAYS)} days, read hour by hour from the service's logs.")
page.h2("Where the time goes")
page.figure(spread, "Writes are slowest and spread widest; the busiest read is the steadiest.")
page.figure(heatmap, "Slow hours come at lunchtime on weekdays, and Friday's are the slowest.")
page.h2("The week, by endpoint")
page.frame(summary)
page.save(HERE / "report.html")
print(f"html: {HERE / 'report.html'}")
