# Grade 3 / الصف الثالث الابتدائي

This directory documents the official Egyptian Grade 3 curriculum sources and the normalized content model we will build from them.

## Official source

Ministry of Education and Technical Education Grade 3 e-learning portal:

https://moe.gov.eg/ar/elearningenterypage/e-learning/?pageIndex=-4&schoolStageId=1582&schoolYearId=1933

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

## Important

Do not copy textbook pages or substantial passages into this repository. Create original explanatory and assessment material aligned with the curriculum and retain references to the official source.
