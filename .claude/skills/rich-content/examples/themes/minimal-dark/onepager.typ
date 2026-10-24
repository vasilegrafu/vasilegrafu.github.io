#import "@local/rich-content:0.1.0": *
#show: report.with(title: "How the orders service serves a read", eyebrow: "Design note · minimal-dark",
                   footer: "The minimal-dark theme", dense: true)

A read of one order, `GET /orders/42`, is answered from Redis when it can be and from Postgres
when it cannot. This note shows the path, what a miss costs, and where the time goes.

#figure(image("system.svg", width: 100%), caption: [Three API instances behind one address;
Postgres only on a miss (the dashed arrow).])

#beside(widths: (1.2fr, 1fr),
  figure(image("latency.svg", width: 100%), caption: [p99 crosses the budget three times a day.]),
  [
    #callout("Key idea", tone: "info")[A miss is a slower read, not an error: the API fills the
    cache on its way back.]
    #data-table(([Read], [p50], [p99]), (([Hit], [9~ms], [13~ms]), ([Miss], [41~ms], [48~ms])),
                numeric: (1, 2))
  ],
)

```python
def get_order(order_id: int) -> Order:
    cached = redis.get(f"order:{order_id}")
    if cached is not None:              # a hit: 13 ms at p99
        return Order.parse(cached)
    return db.fetch_order(order_id)     # a miss: Postgres
```
