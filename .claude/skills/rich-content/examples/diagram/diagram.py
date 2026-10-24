"""An architecture diagram: a request through an API to its cache and database, with a queue on the side.
Run it, and diagram.svg appears beside it; render it to see it with its fonts:

    .venv\\Scripts\\python.exe .claude\\skills\\rich-content\\examples\\diagram\\diagram.py
    .venv\\Scripts\\python.exe -m tools.render png .claude\\skills\\rich-content\\examples\\diagram\\diagram.svg
"""
from tools.svgkit import Canvas, save

c = Canvas(720, 250)
c.region(240, 14, 290, 222, "Our service", icon="cloud")
user = c.node(4, 98, 130, 56, "client", "Browser", icon="monitor")
api = c.node(262, 98, 150, 56, "compute", "API", sub="FastAPI", icon="server")
cache = c.node(570, 22, 144, 56, "cache", "Cache", icon="zap")
db = c.node(570, 174, 144, 56, "data", "Database", icon="database", shape="cylinder")
queue = c.node(262, 174, 150, 50, "async", "Email queue", icon="mail")
c.arrow(user.right, api.left, label="GET /orders")
c.arrow(api.right, cache.left, label="1 · look up")
c.arrow(api.right, db.left, label="2 · on a miss", dash="5 4")
c.arrow(api.bottom, queue.top)
save(c, __file__)
