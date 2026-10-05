# Grade 3 / الصف الثالث الابتدائي

Academic year: **2026/2027**

## Source status

The Egyptian Ministry of Education Grade 3 catalog remains the authoritative source, but its live e-learning endpoint currently returns blank/403 responses in normal access.

Because of that, `sources/grade-3.yaml` records both:

1. the Ministry catalog reference; and
2. a verified reachable access mirror for the Grade 3 textbook collection.

Do not assume that an HTTP failure from the Ministry catalog means the curriculum no longer exists.

## Local textbook acquisition

Run:

```bash
python3 scripts/fetch_grade3.py
```

The resulting files belong under:

```
downloads/grade-3/
```

That directory is ignored by Git.

## Planned normalized structure

Each subject will eventually follow:

```
subjects/<subject>/
  term-1/
    unit-01/
      lesson-01.yaml
      lesson-02.yaml
  term-2/
```

Each lesson record should contain:

- curriculum identifiers
- source reference
- title
- learning objectives
- prerequisite knowledge
- concepts
- vocabulary
- worked examples
- original practice questions
- assessment items
- answers/rubric
- misconceptions
- parent/teacher notes
- accessibility notes
- language metadata

## Copyright

Do not copy textbook pages or substantial passages into this public repository. Create original explanatory and assessment material aligned with the curriculum and retain references to source material.
