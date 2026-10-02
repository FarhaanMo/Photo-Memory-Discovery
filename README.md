# Photo Memory Discovery

The Discovery Agent is a research app for one question: how people try to find a photo they remember, but cannot precisely describe.

It brings together four research sources:

- Broad Public Research: 225 public conversations about photo retrieval
- Targeted Vague-Memory Research: 18 public examples collected, 12 included in structured analysis
- Survey: 15 responses
- Interviews: 5 observed retrieval tasks

Counts are calculated in code. Ask the Research can phrase an answer only from retrieved evidence and those counts. It does not estimate how common a problem is across all Google Photos users, and it does not recommend a product on its own.

## Run locally

From the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

On macOS or Linux, activate with `source .venv/bin/activate` and use the same `streamlit run app.py` command.

Deployment entry point: `app.py`

## Secret

Ask the Research needs:

```text
GROQ_API_KEY
```

Put it in a local `.env` file (see `.env.example`) or in Streamlit secrets as `GROQ_API_KEY`. The key is never written into the app.

The Research Overview, Retrieval Landscape, What People Remember, Where Retrieval Breaks, Retrieval Behaviour, Survey & Interviews, Evidence Explorer, and Methodology pages work without the API key. Ask the Research requires `GROQ_API_KEY`. If the key is missing or the model is unavailable, Ask the Research shows a short message and the rest of the app still works.

## Deploy on Streamlit Community Cloud

1. Put this project in a Git repository. The entry file is `app.py`.
2. Open [share.streamlit.io](https://share.streamlit.io) and choose **Create app**.
3. Select the repository and branch. Set **Main file path** to `app.py`.
4. Under **Advanced settings → Secrets**, add:

```toml
GROQ_API_KEY = "your-key"
```

5. Deploy. Streamlit installs `requirements.txt` on its own.

Structured targeted analysis uses the 12 examples that already passed extraction and quality checks. The other 6 collected examples stay in the source file and are not labelled. Do not run `scripts/run_corpus_b.py` as part of deployment.
