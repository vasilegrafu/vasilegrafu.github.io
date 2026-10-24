"""An explainer: a page that teaches how something works, with a contents bar and a process the
reader steps through. Here, how a read-through cache answers: a miss, the fill, then a hit -- the
same diagram three times, each step marking what moves. One self-contained file, explainer.html:

    .venv\\Scripts\\python.exe .claude\\skills\\rich-content\\examples\\explainer\\build.py
"""
from tools.html import Page
from tools.svgkit import Canvas

page = Page("How a read-through cache answers", eyebrow="Explainer", contents=True,
            lead="The first read of a key misses and goes to the database; it leaves a copy in the cache, "
                 "and every read after it is answered from memory until the copy expires.")


def cache(step: int) -> Canvas:
    """The same three boxes each time; what takes part in this step is in focus, the rest dimmed."""
    c = Canvas(700, 150)
    taking_part = {1: ("app", "cache", "db"), 2: ("cache", "db"), 3: ("app", "cache")}[step]

    def state(name: str) -> str:
        return "focus" if name in taking_part else "dim"
    app = c.node(10, 30, 150, 58, "compute", "App", sub="reads key 42", icon="server", state=state("app"))
    mem = c.node(275, 30, 150, 58, "cache", "Cache", sub="in memory", icon="zap", state=state("cache"))
    db = c.node(540, 30, 150, 58, "data", "Database", icon="database", shape="cylinder", state=state("db"))
    if step == 1:
        c.arrow(app.right, mem.left, label="get 42", step=1, label_dy=-20)
        c.arrow(mem.right, db.left, label="miss: read it", step=2, label_dy=-20, color=c.th.signal["warn"])
        c.chip(350, 124, "1 read, 38 ms", tone="warn", anchor="middle")
    elif step == 2:
        c.arrow(db.left, mem.right, label="the row", step=3, label_dy=-20)
        c.chip(350, 124, "kept for 5 minutes", tone="info", anchor="middle")
    else:
        c.arrow(app.right, mem.left, label="get 42", step=4, label_dy=-20)
        c.arrow(mem.left, app.right, label="hit", label_dy=22, color=c.th.signal["good"])
        c.chip(350, 124, "answered from memory, 1 ms", tone="good", anchor="middle")
    return c


page.h2("The three steps")
page.steps([
    (cache(1), "A miss", "The app asks the cache for key 42. The cache has no copy, so it reads the row from the "
                         "database: the slow path, paid once."),
    (cache(2), "The fill", "The cache keeps the row it read, with a time to live. The database is not asked again "
                           "for this key until the copy expires."),
    (cache(3), "A hit", "The next read of key 42 is answered from memory. Every read until the copy expires takes "
                        "this path."),
], "One key read three times. Step through with the buttons or the arrow keys; printed, the steps stand one "
   "under the other.")

page.h2("When it goes wrong")
page.callout("Stale reads", "A row changed in the database is still served from the cache until its copy expires. "
             "Keep the time to live as short as the data's tolerance for being out of date.", tone="warn")
page.p("A miss on a key no row has goes to the database every time. Cache the absence too, for a shorter time, "
       "so a flood of reads for a missing key does not reach the database.")

page.h2("What to measure")
page.table(["Measure", "Healthy", "Means"],
           [["Hit rate", "above 90 %", "most reads never reach the database"],
            ["Miss latency", "the database's own", "the slow path, paid once per key and expiry"],
            ["Evictions", "near zero", "the cache is big enough for what is read"]])

page.save(__file__.replace("build.py", "explainer.py"))
