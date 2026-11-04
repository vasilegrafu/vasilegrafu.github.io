// A row of cards, each headed by the thing it speaks for: a benefit, an
// interface, a role. Two or three to a row, one on a phone.
export interface Card {
  kicker: string;
  title: string;
  body: string;
}

export default function CardsPart({ cards, cols = 3 }: { cards: Card[]; cols?: 2 | 3 }) {
  return (
    <div
      className={`my-8 grid gap-4 ${cols === 2 ? 'sm:grid-cols-2' : 'sm:grid-cols-2 lg:grid-cols-3'}`}
    >
      {cards.map((c) => (
        <div key={c.title} className="card flex flex-col p-5">
          <p className="kicker">{c.kicker}</p>
          <p className="title-card mt-2">{c.title}</p>
          <p className="text-muted mt-2 text-xs">{c.body}</p>
        </div>
      ))}
    </div>
  );
}
