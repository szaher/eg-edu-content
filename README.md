# Egyptian Education Content

Structured, source-linked educational content for the Egyptian national curriculum.

## Scope

The repository now covers the currently indexed **2026/2027 curriculum across all discovered school levels**, not only Grade 3.

The source index currently exposes:

- Kindergarten: KG1–KG2
- Primary: Grades 1–6
- Preparatory: Grades 1–3
- Secondary: Grades 1–3
- Community Education: Grades 1–6

That is **20 discovered curriculum levels** in total.

## Source status

The Ministry of Education electronic library remains the authoritative source, but its public endpoint currently returns blank/403 responses for some clients.

For practical access, this repository distinguishes between:

- **official source** — Ministry electronic library;
- **verified discovery/access source** — a reachable index exposing the Ministry-issued curriculum files.

The current all-level source manifest is:

```
sources/2026-2027.yaml
```

The older Grade 3-specific manifest remains available at:

```
sources/grade-3.yaml
```

## Fetch every available level

```bash
python3 scripts/fetch.py
```

This discovers all currently available curriculum levels and downloads their PDFs under:

```
downloads/
├── kg-1/
├── kg-2/
├── primary-1/
├── primary-2/
├── primary-3/
├── primary-4/
├── primary-5/
├── primary-6/
├── preparatory-1/
├── preparatory-2/
├── preparatory-3/
├── secondary-1/
├── secondary-2/
├── secondary-3/
├── community-1/
├── community-2/
├── community-3/
├── community-4/
├── community-5/
└── community-6/
```

Each directory also receives a generated `manifest.json` recording the discovered subject pages and PDF URLs.

## Useful fetch modes

List discovered levels:

```bash
python3 scripts/fetch.py --list-levels
```

Discover everything and generate manifests without downloading PDFs:

```bash
python3 scripts/fetch.py --manifest-only
```

Fetch only the mainstream school system, excluding community education:

```bash
python3 scripts/fetch.py --mainstream-only
```

Fetch one specific level:

```bash
python3 scripts/fetch.py --level primary-3
```

Fetch several selected levels:

```bash
python3 scripts/fetch.py \
  --level primary-1 \
  --level primary-2 \
  --level primary-3
```

Re-download existing files:

```bash
python3 scripts/fetch.py --overwrite
```

Change download concurrency:

```bash
python3 scripts/fetch.py --workers 8
```

## Copyright / redistribution

Downloaded textbook PDFs are intentionally excluded from Git.

The Ministry states that intellectual-property rights in the curricula belong to the Egyptian state. This public repository therefore does **not** act as a mirror of the textbook PDFs.

Instead it stores:

1. source metadata;
2. acquisition/fetch tooling;
3. curriculum indexes;
4. normalized metadata;
5. original structured educational material aligned with the curriculum.

## Repository layout

```
.
├── README.md
├── .gitignore
├── sources/
│   ├── 2026-2027.yaml
│   └── grade-3.yaml
├── docs/
│   └── grade-3.md
└── scripts/
    ├── fetch.py
    └── fetch_grade3.py
```

`fetch_grade3.py` is retained for compatibility; new work should use the generic `fetch.py`.

## Planned structured content

The next layer is normalized curriculum content:

```
stage
  -> grade
    -> subject
      -> term
        -> unit
          -> lesson
            -> learning objectives
            -> concepts
            -> vocabulary
            -> examples
            -> practice
            -> assessment
            -> answers/rubric
            -> teacher/parent notes
```

The structured layer should be original and source-referenced rather than a transcription of copyrighted textbook pages.
