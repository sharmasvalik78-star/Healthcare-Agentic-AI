# TODO - Healthcare Agentic AI App

- [x] Create full Streamlit app in `app.py` (single-page UI, calls agent functions, renders final report).

- [x] Implement CrewAI agents in:
  - [x] `agents/symptom_agent.py`
  - [x] `agents/diet_agent.py`
  - [x] `agents/medicine_agent.py`
  - [x] `agents/report_agent.py`

- [x] Recreate `requirements.txt` with working dependency versions.

- [x] Update `README.txt` with setup/run instructions (using `.env`, not `env.txt`).

- [ ] Smoke-test by running `python -m streamlit run app.py`.

- [ ] (Scope B) Add negation-aware trigger detection and expose rationale.

- [ ] (Scope B) Update report consolidation to include trigger-based rationale.

- [ ] (Scope B) Add “Copy summary” button to the UI.

- [ ] (Scope B) Run `python -m compileall .` and then `python -m streamlit run app.py`.

- [x] Add “Symptom Severity Level” with color-coded display in UI.


