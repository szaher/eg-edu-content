# Egyptian Education Content

Structured, source-linked educational content for the Egyptian curriculum.

## Grade 3

This repository starts with **Egyptian Primary Grade 3 / الصف الثالث الابتدائي** for academic year **2026/2027**.

## Source status

The Ministry of Education Grade 3 e-learning catalog is still discoverable in search results, but the live page currently returns blank/403 responses in normal browser/automated access. For that reason this repository distinguishes between:

- **official catalog reference** — the Ministry source of record;
- **verified access mirror** — a reachable page that exposes the same Ministry textbook files for practical access.

The source manifest is in:

```
sources/grade-3.yaml
```

## Current subjects

- اللغة العربية
- اللغة الإنجليزية
- الرياضيات
- Mathematics in English
- Mathematics in French
- اكتشف
- Discover in English
- التربية الدينية الإسلامية
- التربية الدينية المسيحية

## Fetch Grade 3 files locally

```bash
python3 scripts/fetch_grade3.py
```

The script uses the verified source manifest and stores downloaded files under:

```
downloads/grade-3/
```

Downloaded textbook PDFs are intentionally excluded from Git.

## Copyright / redistribution

The Ministry states that intellectual-property rights in the curricula belong to the Egyptian state. This public repository therefore does **not** act as a mirror of the textbook PDFs.

Instead it stores source metadata, fetch tooling, curriculum indexes, and original structured educational material aligned to the curriculum.

## Repository layout

```
.
├── README.md
├── .gitignore
├── sources/
│   └── grade-3.yaml
├── docs/
│   └── grade-3.md
└── scripts/
    └── fetch_grade3.py
```

## Planned structured content

```
grade -> subject -> term -> unit -> lesson -> learning objectives -> concepts
      -> examples -> practice -> assessment -> answers -> teacher/parent notes
```

The structured layer should be original and source-referenced rather than a transcription of copyrighted textbook pages.
