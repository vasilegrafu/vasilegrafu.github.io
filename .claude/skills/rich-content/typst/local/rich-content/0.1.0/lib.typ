// The rich-content house style for PDFs. A document imports it and wraps itself in `report`:
//
//   #import "@local/rich-content:0.1.0": *
//   #show: report.with(title: "How the orders service serves a read", eyebrow: "Design note · week 42",
//                      footer: "Orders service · design note")
//
// `python -m tools.render pdf` passes the skill's typst/ folder as the package path, so the import
// resolves wherever the document sits, and passes the theme -- colours, fonts, corners -- the
// diagrams and charts are drawn in, so the document is set in it too.

#let theme = {
  let given = sys.inputs.at("rich-content-theme", default: none)
  if given == none {
    panic("compile with `python -m tools.render pdf`, which passes the rich-content theme")
  }
  json(bytes(given))
}
#let tokens = theme
#let colour(key) = rgb(theme.colour.at(key))
#let signal(key) = rgb(theme.signal.at(key))

#let sans = theme.fonts.label
#let serif = theme.fonts.text
#let heading-font = theme.fonts.heading
#let mono = theme.fonts.mono
#let heading-weight = theme.fonts.at("heading_weight", default: 700)
// a family with a small x-height is set larger than its nominal size, so it reads as large as the rest
#let scale-of(family) = theme.at("font_scale", default: (:)).at(family, default: 1)
#let radius = theme.shape.radius * 1pt

/// The page, type and headings. `eyebrow` is the small capitals line above the title; `footer`
/// the text at the foot of every page, beside the page number. `dense: true` tightens margins,
/// type and spacing for a page that must hold a lot -- a one-pager -- while keeping the look.
#let report(title: none, eyebrow: none, footer: none, paper: "a4", dense: false, body) = {
  let d(normal, tight) = if dense { tight } else { normal }
  set document(title: title, date: none)    // no creation time: a rebuilt PDF is the same file
  set page(paper: paper, margin: d((x: 22mm, top: 20mm, bottom: 18mm), (x: 17mm, top: 14mm, bottom: 14mm)),
    fill: if theme.at("dark", default: false) { colour("paper") } else { auto },
    footer: context {
      set text(font: sans, size: 8pt, fill: colour("muted"))
      if footer != none { footer }
      h(1fr)
      counter(page).display()
      " / "
      str(counter(page).final().first())
    })
  let hs = scale-of(heading-font)
  set text(font: serif, size: d(10.5pt, 9.8pt) * scale-of(serif), fill: colour("ink"))
  set par(justify: true, leading: d(0.68em, 0.6em), spacing: d(1.1em, 0.85em))
  show heading: set text(font: heading-font, fill: colour("heading"))
  show heading.where(level: 1): set text(size: d(20pt, 17pt) * hs, weight: heading-weight)
  // a heading is kept on the page of what follows it (sticky), never left alone at a page's foot
  show heading.where(level: 2): it => block(above: d(1.6em, 1.1em), below: d(0.7em, 0.5em), sticky: true,
                                            text(size: d(12.5pt, 11.5pt) * hs, weight: heading-weight, it.body))
  show heading.where(level: 3): it => block(above: d(1.3em, 0.9em), below: d(0.6em, 0.4em), sticky: true,
                                            text(size: d(10.5pt, 10pt) * hs, weight: heading-weight, it.body))
  // a link is told from the text around it, in the accent colour
  show link: set text(fill: colour("accent"))
  // code shows the characters one types: no ligatures turning -> into an arrow
  show raw: set text(font: mono, size: d(8.8pt, 8.4pt), ligatures: false, features: (calt: 0))
  // code in the theme's colours: render.pdf passes a TextMate theme made from them (tools.code)
  let code-theme = sys.inputs.at("rich-content-code", default: none)
  set raw(theme: if code-theme == none { auto } else { bytes(code-theme) })
  show raw.where(block: true): it => block(fill: colour("paper"), stroke: 0.5pt + colour("rule"),
    radius: calc.min(4pt, radius), inset: (x: 9pt, y: 7pt), width: 100%, it)
  // any table -- one from Markdown, or written by hand -- in the house style; data-table adds alignment
  set table(stroke: (x, y) => if y == 0 { (bottom: 0.7pt + colour("rule")) } else { (bottom: 0.4pt + colour("rule")) },
            inset: (x: 8pt, y: 6pt))
  show table: set text(font: sans, size: 9pt, number-type: "lining", number-width: "tabular")
  show table.cell.where(y: 0): set text(size: 8.5pt, weight: "semibold", fill: colour("muted"))
  show figure.caption: set text(font: sans, size: d(8.5pt, 8pt), fill: colour("muted"))
  set figure(gap: d(0.8em, 0.55em))
  if eyebrow != none {
    text(font: sans, size: 8.5pt, weight: "semibold", fill: colour("muted"), tracking: 0.08em, upper(eyebrow))
  }
  if title != none { heading(level: 1, title) }
  body
}

/// Blocks side by side -- a chart beside the text that explains it, two figures -- top-aligned.
///   #beside(figure(image("chart.svg"), caption: […]), [text and a callout], widths: (1.2fr, 1fr))
#let beside(..blocks, widths: auto, gutter: 14pt) = {
  let items = blocks.pos()
  grid(columns: if widths == auto { (1fr,) * items.len() } else { widths }, gutter: gutter,
       align: top, ..items)
}

/// A coloured aside with a title: tone is info | good | warn | bad.
#let callout(title, tone: "info", body) = block(
  fill: signal(tone + "_fill"), stroke: (left: 2pt + signal(tone)), inset: (x: 12pt, y: 10pt),
  radius: (right: calc.min(4pt, radius)), width: 100%, above: 1.3em, below: 1.3em,
)[
  #text(font: sans, size: 9.5pt, weight: "semibold", fill: signal(tone))[#title] \
  #body
]

/// A table in the house style: header in small capitals, rules between rows, and the columns
/// named in `numeric` right-aligned with figures that line up.
///   #data-table(([Endpoint], [p99]), (([`GET /x`], [212 ms]),), numeric: (1,))
#let data-table(header, rows, numeric: (), columns: auto) = {
  let n = header.len()
  let cols = if columns == auto { (1fr,) + (auto,) * (n - 1) } else { columns }
  table(
    columns: cols,
    align: (x, y) => if x in numeric { right } else { left },
    stroke: (x, y) => if y == 0 { (bottom: 0.7pt + colour("rule")) } else { (bottom: 0.4pt + colour("rule")) },
    inset: (x: 8pt, y: 6pt),
    table.header(..header.map(h => text(font: sans, size: 8.5pt, weight: "semibold", fill: colour("muted"), h))),
    ..rows.flatten().map(x => text(font: sans, size: 9pt, number-type: "lining", number-width: "tabular", x)),
  )
}

/// Figures that matter at a glance, as a row of tiles: each item is (label, value, note, tone), tone
/// being good | warn | bad | info | neutral (the note's colour). Four to a row; more wrap.
///   #kpis(("Requests", "1.24 M", "+8 % on week 41", "good"), ("p99", "212 ms", "over budget", "bad"))
#let kpis(..items) = {
  let tone-colour(tone) = if tone in ("good", "warn", "bad", "info") { signal(tone) } else { colour("muted") }
  let all = items.pos()
  block(above: 1em, below: 1.2em, grid(
    columns: (1fr,) * calc.min(calc.max(all.len(), 1), 4), gutter: 8pt,
    ..all.map(it => block(width: 100%, inset: (x: 10pt, y: 9pt), radius: calc.min(4pt, radius),
                          stroke: 0.5pt + colour("rule"), fill: colour("wash"))[
      #set par(justify: false, leading: 0.5em, spacing: 0pt)
      #set text(hyphenate: false)
      #text(font: sans, size: 7.5pt, weight: "semibold", fill: colour("muted"), tracking: 0.05em, upper(it.at(0)))
      #v(5pt)
      #text(font: sans, size: 15pt, weight: "bold", fill: colour("heading"), number-type: "lining", it.at(1))
      #v(6pt)
      #text(font: sans, size: 8pt, weight: "medium", fill: tone-colour(it.at(3)), it.at(2))
    ])))
}
