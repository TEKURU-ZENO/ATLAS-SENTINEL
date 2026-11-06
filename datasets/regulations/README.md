# Regulation Sources

The checked-in `seed_chunks.json` contains short, sourced summaries for the current Occupational Safety, Health and Working Conditions Code, 2020 and bibliographic metadata for OISD-STD-105. It is deliberately not presented as a full-text copy of either instrument.

India's Ministry of Labour announced the OSH Code effective from 21 November 2025. Section 143 repeals the Factories Act, 1948 from the relevant commencement date, so Factories Act material belongs in a clearly marked historical collection, not as current law. The current-Code seed cites the official India Code PDF. OISD's official catalogue lists OISD-STD-105, Work Permit System, August 2023; its operative text is not in this repository because the authorized full document was unavailable in this environment.

Official references:

- OSH Code 2020: https://www.indiacode.nic.in/bitstream/123456789/22041/1/2020-37.pdf
- OSH Code commencement: https://www.pib.gov.in/PressReleasePage.aspx?PRID=2194018&lang=2&reg=48
- OISD standards catalogue: https://oisd.gov.in/oisd-standards
- Historical Factories Act text: https://www.indiacode.nic.in/bitstream/123456789/1530/1/A1948-63.pdf

The retriever abstains below a minimum relevance score of 0.08. This is a guard against clearly unrelated queries, not a calibrated confidence threshold. The hand-written 50-question set measures retrieval/context behavior against the small seed corpus and is not an independent legal-answer evaluation.

Place authorized PDFs or permitted text copies under `datasets/regulations/source/`, then run:

```powershell
$env:PYTHONPATH = "apps/backend"
python -m app.rag.ingest datasets/regulations/source
python -m app.rag.evaluate
```

PDF chunks retain the file name, printed section heading, and PDF page for citation. Search is local TF-IDF plus lexical overlap. The included 50-question set evaluates retrieval hit rate, top citation accuracy, and expected-fact coverage in retrieved context. Context coverage is not a model answer correctness score. Add an answer-generation layer and expert-reviewed expected answers before reporting end-to-end answer correctness.
