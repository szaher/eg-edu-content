# Egyptian Education Content

Structured, source-linked educational content for the Egyptian curriculum.

## Grade 3

This repository starts with **Egyptian Primary Grade 3 / الصف الثالث الابتدائي**.

Official source:

- Ministry of Education and Technical Education e-learning portal
- Grade 3 portal: https://moe.gov.eg/ar/elearningenterypage/e-learning/?pageIndex=-4&schoolStageId=1582&schoolYearId=1933

Subjects currently exposed by the Ministry Grade 3 portal include:

- اللغة العربية
- اللغة الإنجليزية
- الرياضيات
- Mathematics in English
- Mathematics in French
- اكتشف
- Discover in English
- التربية الدينية الإسلامية
- التربية الدينية المسيحية

## Copyright / redistribution

The Ministry states that the intellectual-property rights in the curricula are owned by the Egyptian state, and Ministry portals mark the material as all rights reserved.

For that reason, this repository **does not republish Ministry textbook PDFs**. Instead it contains:

1. official-source manifests;
2. scripts for fetching official material for local use;
3. curriculum indexes and metadata;
4. original, structured learning material that can be built from curriculum objectives without copying textbook pages.

Downloaded Ministry files go under `downloads/`, which is intentionally ignored by Git.

## Fetch Grade 3 files locally

```bash
python3 scripts/fetch_grade3.py
```

The script only follows Ministry-hosted links and stores any discovered PDFs under:

```
downloads/grade-3/
```

If the Ministry changes the portal HTML or blocks automated access, open the official Grade 3 portal above and download the files manually into that directory.

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

## Next step

The next useful layer is a normalized curriculum model:

```
grade -> subject -> term -> unit -> lesson -> learning objectives -> concepts
      -> examples -> practice -> assessment -> answers -> teacher/parent notes
```

That structured layer should be original and source-referenced rather than a transcription of copyrighted textbook pages.
