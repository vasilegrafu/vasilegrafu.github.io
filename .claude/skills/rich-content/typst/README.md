# typst/ — the house style for PDFs, as a Typst package

```
typst/                          the package path render.pdf gives Typst
└── local/                      the namespace: a package of this machine, not from Typst Universe
    └── rich-content/           the package's name
        └── 0.1.0/              its version
            ├── typst.toml      what declares the package: name, version, entry point
            └── lib.typ         the house style: report, beside, callout, data-table, code and tables
```

The nesting is Typst's, not ours: a local package must sit at
`<package path>/<namespace>/<name>/<version>/`. That is what lets a document anywhere in the
checkout begin with

```typst
#import "@local/rich-content:0.1.0": *
```

with no path to the skill in it.

`python -m tools.render pdf` (and `render.pdf()`, `render.markdown_pdf()`) passes this folder as
the package path, together with the theme the document is set in -- `lib.typ` reads its colours,
fonts and corners from that, and stops with a message if a document is compiled any other way.
The packages the house style itself imports from Typst Universe (cmarker, for Markdown) are not
here: `scripts/setup.py` puts them in the venv, in `<venv>/share/typst/packages/`.

To change the house style, edit `lib.typ` and rebuild an example (`examples/pdf/build.py`); a
change that would break documents written for it goes into a new version folder, `0.2.0/`, beside
this one.
