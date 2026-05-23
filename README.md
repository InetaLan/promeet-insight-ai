# ProMeet Insight AI — MVP Python Project

MVP tikslas: iš MS Teams susitikimo transkripto automatiškai ištraukti užduotis, sprendimus, atsakingus asmenis, terminus, prioritetus, source quote, confidence score ir paruošti Jira-ready JSON.

## Pipeline

1. Nuskaito `.docx` arba `.txt` transkriptus.
2. Ištraukia transkripto segmentus pagal formatą `[00:11] Vardas Pavardė: tekstas`.
3. Validuoja transkripto struktūrą.
4. GPT-4o režimu bando ištraukti užduotis į struktūruotą JSON.
5. Jei nėra `OPENAI_API_KEY`, veikia lokali taisyklių/pattern matching demo versija.
6. Validuoja JSON schemą su Pydantic.
7. Apskaičiuoja hibridinį confidence score.
8. Paruošia Jira issue payload.
9. Išsaugo rezultatus į `data/outputs`.

## Greitas paleidimas

```bash
cd promeet_insight_mvp
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Paleidimas su įkeltais transkriptais:

```bash
python -m promeet.cli --input-dir data/transcripts --output-dir data/outputs
```

Su GPT-4o:

```bash
cp .env.example .env
# įrašyk OPENAI_API_KEY
python -m promeet.cli --input-dir data/transcripts --output-dir data/outputs --use-openai
```

Streamlit demo UI:

```bash
streamlit run app.py
```

## MVP komponentai

| Komponentas | Realizacija |
|---|---|
| Main extraction | GPT-4o arba rule-based fallback |
| NER | XLM-R placeholder + regex/person resolver MVP |
| Similarity | Sentence-BERT, jei įdiegtas; fallback į TF-IDF |
| Confidence | Hybrid scoring |
| Governance | Human approval status laukai |
| JSON schema | Pydantic modelis |
| Jira | Payload mapper, real API mock |
