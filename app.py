"""Discovery Agent — research analytics UI.

All counts come from src/analytics_*.py. Ask the Research is the only page
that calls a model, and only to phrase retrieved evidence.
"""
from collections import OrderedDict

import pandas as pd
import streamlit as st

from src import analytics_corpus_a as A
from src import analytics_corpus_b as B
from src import analytics_interviews as I
from src import analytics_survey as S
from src.config import INTERVIEW_CSV_PATH, TARGETED_PROCESSED_CSV_PATH, TRIAGE_CSV_PATH, resolve_survey_csv_path
from src.ui import (
    callout,
    evidence_card,
    hbars,
    floating_ask_button,
    html_block,
    inject_css,
    journey_card,
    journey_strip,
    metric_card,
    metric_row,
    page_header,
    pill,
    pipeline,
    section,
    source_tag,
)
from src.ui.components import esc
from src.ui import tokens as T

st.set_page_config(
    page_title="Photo Memory Discovery",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()


def _mtime(path):
    if path is None or not path.is_file():
        return (0, 0)
    stat = path.stat()
    return (stat.st_mtime_ns, stat.st_size)


@st.cache_data
def load_a(_mtime_key):
    return A.load_corpus_a()


@st.cache_data
def load_b(_mtime_key):
    return B.load_corpus_b()


@st.cache_data
def load_s(_mtime_key):
    return S.load_survey()


@st.cache_data
def load_i(_mtime_key):
    return I.load_interviews()


interviews = load_i(_mtime(INTERVIEW_CSV_PATH))
corpus_a = load_a(_mtime(TRIAGE_CSV_PATH))
corpus_b, corpus_b_total = load_b(_mtime(TARGETED_PROCESSED_CSV_PATH))
survey_all, _survey_cols = load_s(_mtime(resolve_survey_csv_path()))

b_status = B.status_summary(corpus_b, corpus_b_total)
b_valid = B.valid(corpus_b)

NAV = OrderedDict([
    ("OVERVIEW", ["Research Overview"]),
    ("DISCOVERY", [
        "Retrieval Landscape",
        "What People Remember",
        "Where Retrieval Breaks",
        "Retrieval Behaviour",
    ]),
    ("PRIMARY RESEARCH", ["Survey & Interviews"]),
    ("EVIDENCE", ["Evidence Explorer"]),
    ("AI", ["Ask the Research"]),
    ("ABOUT", ["Methodology"]),
])
PAGE_LIST = [p for pages in NAV.values() for p in pages]
if "page" not in st.session_state:
    st.session_state.page = PAGE_LIST[0]
if st.query_params.get("ask") == "1":
    st.session_state.page = "Ask the Research"
    del st.query_params["ask"]

with st.sidebar:
    st.markdown(
        "<div class='brand-mark'>Photo Memory Discovery</div>"
        "<div class='brand-sub'>AI-powered retrieval research</div>",
        unsafe_allow_html=True,
    )
    index = 1
    for group, pages in NAV.items():
        st.markdown("<div class='nav-group'>{g}</div>".format(g=group), unsafe_allow_html=True)
        for name in pages:
            selected = st.session_state.page == name
            label = "{n} · {p}".format(n=index, p=name)
            if st.button(label, key="nav_{p}".format(p=name), type="primary" if selected else "secondary",
                         use_container_width=True):
                st.session_state.page = name
                st.rerun()
            index += 1
    st.markdown("<div class='nav-group'>Survey scope</div>", unsafe_allow_html=True)
    survey_scope = st.radio(
        "Survey respondents",
        ["All respondents", "Screened-in only"],
        label_visibility="collapsed",
        help="Screened-in excludes respondents who answered \"No, I don't remember\" on the screening question.",
    )
    st.caption("Counts are computed in Pandas. Ask the Research is the only page that calls a model.")
page = st.session_state.page

survey = survey_all
if survey is not None and survey_scope == "Screened-in only":
    survey = survey_all[survey_all["screening"] != S.SCREENING_NO]
n_survey = 0 if survey is None else len(survey)
survey_denominator = "n = {n} respondents{s} · multi-select, counts do not sum to n".format(
    n=n_survey, s=" (screened-in)" if survey_scope == "Screened-in only" else ""
)
survey_single_denominator = "n = {n} respondents{s}".format(
    n=n_survey, s=" (screened-in)" if survey_scope == "Screened-in only" else ""
)
survey_summary = S.summary(survey) if survey is not None else None


def b_denominator():
    return "n = {v} analysed examples".format(v=b_status["valid"])


def b_banner():
    callout(
        "{scope}. {limit}".format(
            scope=B.collection_phrase(b_status["valid"], b_status["source_total"]),
            limit=B.LIMITATION,
        ),
        kind="note",
    )


def b_statement(text):
    st.markdown("_{p}, {t}_".format(p=B.analysed_prefix(b_status["valid"]), t=text))


def top_items(counts, k=3):
    items = [(name, value) for name, value in counts.items() if value > 0]
    items.sort(key=lambda kv: -kv[1])
    return items[:k]


def remembered_true(row):
    return [label for field, label in I.CLUE_DISPLAY.items() if row.get(field) == "true"]


# ---------------------------------------------------------------- pages

def page_overview():
    page_header(
        "Overview · Executive brief",
        "Research Overview",
        "How people try to retrieve a photo they remember but cannot precisely describe.",
    )
    rel = A.relevance_counts(corpus_a) if corpus_a is not None else {}
    a_n = 0 if corpus_a is None else len(corpus_a)
    s_n = 0 if survey_all is None else len(survey_all)
    i_n = len(interviews)
    a_extra = pill("All screened", "blue") if corpus_a is not None and A.status_summary(corpus_a)["not_triaged"] == 0 else ""
    metric_row(
        metric_card("Broad Public Research", a_n, "Broad public conversations", "a", a_extra),
        metric_card(
            "Targeted Vague-Memory Research",
            b_status["valid"],
            "Targeted vague-memory examples analysed",
            "b",
            "<div class='tiny'>{t} public examples collected.</div>".format(t=b_status["source_total"]),
        ),
        metric_card("Survey", s_n, "Survey responses", "s"),
        metric_card("Interviews", i_n, "Observed retrieval tasks", "i"),
    )

    section("Research pipeline")
    pipeline([
        ("1", "Broad public research", "Complete", "done"),
        ("2", "Targeted evidence", "Complete", "done"),
        ("3", "Primary research", "Complete", "done"),
        ("4", "Problem synthesis", "Complete", "done"),
        ("5", "Product opportunity", "Defined", "done"),
    ])

    section("Three evidence-stream panels")
    html_block(
        "<div class='stream-grid'>"
        "<div class='stream'><h4>Public landscape</h4>"
        "<p>Broad public retrieval conversations used to distinguish vague-memory retrieval from general platform bugs and storage issues.</p>"
        "<div class='tiny'>{d} direct · {adj} adjacent · {ir} not retrieval-related · n = {n}</div></div>"
        "<div class='stream'><h4>Targeted evidence</h4>"
        "<p>Purpose-sampled examples where the person has a target in mind, with incomplete memory, and retrieval is hard.</p>"
        "<div class='tiny'>{scope}.</div></div>"
        "<div class='stream'><h4>Primary research</h4>"
        "<p>Directional survey plus five observed retrieval tasks, unscripted, on real photo libraries.</p>"
        "<div class='tiny'>n = {sn} survey · {tasks} observed tasks. Convenience sample.</div></div>"
        "</div>".format(
            d=rel.get("Direct vague-memory retrieval", 0),
            adj=rel.get("Retrieval-adjacent", 0),
            ir=rel.get("Not retrieval-related", 0),
            n=a_n,
            scope=B.collection_phrase(b_status["valid"], b_status["source_total"]),
            sn=s_n,
            tasks=i_n,
        )
    )
    callout("The three streams use different sampling frames and units. Counts are never pooled into one denominator.")

    section("Key signals so far")
    st.markdown(
        "<div class='signal-grid'>"
        "<div class='signal'><div class='idx'>01</div><h4>Memory can be richer than the first query</h4>"
        "<p>People often retain people, occasion, look or era, and still start with one coarse word or folder. Directional, not a population rate.</p></div>"
        "<div class='signal'><div class='idx'>02</div><h4>Broad first actions crowd the candidate set</h4>"
        "<p>Event or category starts can return many similar or unrelated items before the target is isolated.</p></div>"
        "<div class='signal'><div class='idx'>03</div><h4>Refinement, then browsing, in hard tasks</h4>"
        "<p>Observed difficult tasks added a second clue and still ended in scrolling. Survey answers also name scrolling as an eventual path.</p></div>"
        "<div class='signal'><div class='idx'>04</div><h4>A strong temporal anchor can make existing navigation enough</h4>"
        "<p>INT005 found a graduation photo in about two minutes with year/month browsing and no failed query. Counter-evidence, kept visible.</p></div>"
        "</div>",
        unsafe_allow_html=True,
    )
    callout(B.LIMITATION)


def page_landscape():
    page_header(
        "Discovery · Broad public research",
        "Retrieval Landscape",
        "What public conversations about photo retrieval contain, before the targeted examples.",
    )
    source_tag("corpus_a")
    if corpus_a is None:
        st.error("Broad public research file not found.")
        return
    status = A.status_summary(corpus_a)
    rel = A.relevance_counts(corpus_a)
    metric_row(
        metric_card("Public conversations", status["total"], "Screened conversations", "a"),
        metric_card("Direct vague-memory", rel["Direct vague-memory retrieval"], "Exact scenario", "b"),
        metric_card("Retrieval-adjacent", rel["Retrieval-adjacent"], "Search-quality issues", "s"),
        metric_card("Not retrieval-related", rel["Not retrieval-related"], "Outside the scenario", "i"),
    )
    callout("Broad public landscape — not a prevalence estimate for Google Photos users.", kind="note")
    section("Distribution")
    hbars(rel, T.STREAM["corpus_a"], max_n=status["triaged"])
    section("By public source")
    hbars(A.source_counts(corpus_a), T.STREAM["corpus_a"])
    section("Supporting evidence · direct vague-memory conversations")
    for _, row in A.direct_records(corpus_a).iterrows():
        evidence_card(
            row["record_id"],
            "{s} · {d}".format(s=row["source"], d=row["date"] or "date not recorded"),
            row["raw_text"],
            "Paraphrased public evidence — not a verbatim quote",
            kind="public",
            href=row["url"],
        )


def page_remember():
    page_header(
        "Discovery · Memory",
        "What People Remember",
        "Remembered clues from two independent samples. Denominators are never combined.",
    )
    b_banner()
    callout("The memory can be richer than the initial query. That is a directional research signal, not a population claim.", kind="note")
    left, right = st.columns(2)
    with left:
        source_tag("corpus_b")
        st.caption("Targeted qualitative research · " + b_denominator())
        hbars(B.clue_counts(corpus_b), T.STREAM["corpus_b"])
        top = top_items(B.clue_counts(corpus_b))
        if top:
            b_statement("the most frequently evidenced clues are {t}.".format(
                t=", ".join("{k} ({v})".format(k=k.lower(), v=v) for k, v in top)))
    with right:
        source_tag("survey")
        st.caption("Survey · " + survey_denominator)
        if survey_summary is not None:
            hbars(survey_summary["remembered"], T.STREAM["survey"], max_n=n_survey)
    section("Forgotten information · targeted examples only")
    source_tag("corpus_b")
    hbars(B.forgotten_counts(corpus_b), T.STREAM["corpus_b"])
    callout("Only information an example explicitly says the person does not remember is counted. A clue that is not evidenced is not the same as a forgotten clue.")


def page_breaks():
    page_header(
        "Discovery · Friction",
        "Where Retrieval Breaks",
        "The path from an episodic memory to one photograph, and where that path stalls.",
    )
    b_banner()
    section("Observed retrieval journey")
    journey_strip([
        ("01", "Memory", "What the person already knows.", ""),
        ("02", "Expression", "The person remembers useful details but struggles to turn them into a useful search.", "hi"),
        ("03", "Retrieval", "The person gives useful clues, but the target does not surface.", ""),
        ("04", "Evaluation", "The right or similar photos may be present, but identifying the exact one is difficult.", "hi"),
        ("05", "Recovery", "The first attempt does not work, and the person struggles to make progress.", ""),
        ("06", "Outcome", "Found, not found, or fallback.", "ok"),
    ])
    section("Where the targeted examples break")
    source_tag("corpus_b")
    stages = B.failure_stage_counts(corpus_b)
    hbars(stages, T.STREAM["corpus_b"])
    top = top_items(stages, 1)
    if top:
        b_statement("the most frequent first observed break is {s} ({c} of {n} analysed examples).".format(
            s=top[0][0].lower(), c=top[0][1], n=b_status["valid"]))
    callout("{p}. These counts are directional. They are not a prevalence estimate.".format(
        p=B.analysed_prefix(b_status["valid"])
    ))
    stage_copy = [
        ("Expression", "The person remembers useful details but struggles to turn them into a useful search.", "hi"),
        ("Retrieval", "The person gives useful clues, but the target does not surface.", ""),
        ("Evaluation", "The right or similar photos may be present, but identifying the exact one is difficult.", "hi"),
        ("Recovery", "The first attempt does not work, and the person struggles to make progress.", ""),
    ]
    html_block(
        "<div class='stage-grid'>{h}</div>".format(
            h="".join(
                "<div class='stage-card {k}'><div class='n'>Stage</div><h4>{t}</h4>"
                "<p>{d}</p><div class='count'>{c} of {n} analysed examples</div></div>".format(
                    k=kind, t=title, d=detail, c=stages.get(title, 0), n=b_status["valid"]
                )
                for title, detail, kind in stage_copy
            )
        )
    )
    section("Survey difficulty signals · separate stream")
    source_tag("survey")
    if survey_summary is not None:
        hbars(survey_summary["difficulty"], T.STREAM["survey"], max_n=n_survey)
        st.caption(survey_denominator)
    callout("Survey items are multi-select and are not mapped onto failure stages.")


def page_behaviour():
    page_header(
        "Discovery · Behaviour",
        "Retrieval Behaviour",
        "What people do after a coarse first action, including five observed journeys.",
    )
    b_banner()
    source_tag("corpus_b")
    c1, c2 = st.columns(2)
    with c1:
        st.caption("Initial search strategy · " + b_denominator())
        hbars(B.strategy_counts(corpus_b), T.STREAM["corpus_b"])
        st.caption("Refinement attempt")
        hbars(B.refinement_counts(corpus_b), T.STREAM["corpus_b"])
    with c2:
        st.caption("Workaround after difficulty")
        hbars(B.workaround_counts(corpus_b), T.STREAM["corpus_b"])
        st.caption("Retrieval outcome")
        hbars(B.outcome_counts(corpus_b), T.STREAM["corpus_b"])
    strategies = B.strategy_counts(corpus_b)
    b_statement("{u} of {n} analysed examples do not state the search behaviour.".format(
        u=strategies.get("unknown", 0), n=b_status["valid"]))

    section("Survey methods and outcomes")
    source_tag("survey")
    callout(S.METHODS_NOTE, kind="note")
    c3, c4 = st.columns(2)
    if survey_summary is not None:
        with c3:
            st.caption(S.METHODS_LABEL)
            hbars(survey_summary["methods"], T.STREAM["survey"], hide_zero=True, max_n=n_survey)
        with c4:
            st.caption("Did they eventually find the photo?")
            hbars(survey_summary["outcome"], T.STREAM["survey"], max_n=n_survey)

    section("Five observed journeys")
    source_tag("interview")
    callout("These are five real tasks, not a typical path. INT005 is low-friction counter-evidence.")
    _interview_journey_cards()


ACTION_LABEL = {
    "search": "search",
    "folder_browsing": "folder browsing",
    "chronological_browsing": "year/month browsing",
}


def _interview_journey_cards():
    if interviews.empty:
        callout("No interview observations recorded yet.")
        return
    for _, row in interviews.iterrows():
        stage = row["failure_stage_observed"]
        kind = "ok" if stage == "no_failure" else "interview"
        action = ACTION_LABEL.get(row["first_observed_action"], str(row["first_observed_action"]).replace("_", " "))
        searched = row["first_query"] if row["first_query"] not in ("", "unknown") else action
        refine = row["refinement_description"] if row["refinement_attempted"] == "yes" else "none"
        fallback = row["fallback_or_workaround"] or "none"
        if fallback in ("none", "") and row["manual_scrolling"] == "yes" and stage == "no_failure":
            path = "{f} → found".format(f=action)
        elif refine != "none" and "scroll" in fallback:
            path = "{f} → {r} → scrolling → found".format(f=searched, r=refine)
        elif refine != "none":
            path = "{f} → {r} → found".format(f=action if searched == "unknown" else searched, r=refine)
        else:
            path = "{f} → found".format(f=action)
        remembered = row["remembered_before_retrieval"] or ", ".join(remembered_true(row)) or "none coded true"
        journey_card(
            pid=row["participant_id"],
            target=row["target_description"],
            remembered=remembered,
            first_action=action,
            searched=searched,
            first_result=row["first_result_quality"],
            refine=refine,
            workaround=fallback,
            time_min=row["time_to_target_minutes"],
            attempts=row["attempts_to_target"],
            stage=stage,
            quote=row["hardest_moment_quote"],
            path=path,
            kind=kind,
        )


def page_primary():
    page_header(
        "Primary research",
        "Survey & Interviews",
        "Primary evidence from 15 survey respondents and 5 observed retrieval tasks.",
    )
    if survey_all is None:
        st.error("Survey file not found.")
        return
    tab_s, tab_i = st.tabs(["Survey", "Interviews"])
    with tab_s:
        _survey_tab()
    with tab_i:
        _interview_tab()


def _survey_tab():
    d = survey_summary["difficulty"]
    o = survey_summary["outcome"]
    screened = S.screened_out_ids(survey_all)
    metric_row(
        metric_card("Didn't know what words", "{k} / {n}".format(k=d["Didn't know what words to search"], n=n_survey), "On the recalled attempt", "s"),
        metric_card("Didn't know how to refine", "{k} / {n}".format(k=d["Didn't know how to refine"], n=n_survey), "Recovery friction", "s"),
        metric_card("Found after browsing", "{k} / {n}".format(k=o["Yes, after manual scrolling / browsing"], n=n_survey), "Eventual outcome", "i"),
        metric_card("Gave up", "{k} / {n}".format(k=o["Gave up"], n=n_survey), "Did not find the photo", "a"),
    )
    callout("Directional convenience sample; not population-representative. Showing {d}.".format(d=survey_single_denominator), kind="note")
    callout("The retrieval-method question allowed multiple selections and cannot determine true first action.")
    c1, c2 = st.columns(2)
    with c1:
        st.caption("Remembered clues")
        hbars(survey_summary["remembered"], T.STREAM["survey"], max_n=n_survey)
        st.caption("Difficulty signals")
        hbars(survey_summary["difficulty"], T.STREAM["survey"], max_n=n_survey)
    with c2:
        st.caption(S.METHODS_LABEL)
        hbars(survey_summary["methods"], T.STREAM["survey"], hide_zero=True, max_n=n_survey)
        st.caption("Eventual outcome")
        hbars(survey_summary["outcome"], T.STREAM["survey"], max_n=n_survey)
    st.caption("Screened-in: {s} of {n}.".format(s=len(survey_all) - len(screened), n=len(survey_all)))
    section("Open-text descriptions")
    texts = S.open_text_responses(survey)
    if texts.empty:
        callout("No open-text answers in this scope.")
    else:
        for _, row in texts.iterrows():
            evidence_card(row["respondent_id"], "Survey · optional description", row["open_text"], "Respondent's own words", kind="survey")
    section("Survey quality")
    for item in S.quality_warnings(survey_all):
        st.markdown("- " + item)


def _interview_tab():
    if interviews.empty:
        callout("No interview observations recorded yet.")
        return
    summ = I.summary(interviews)
    n = summ["interviews"]
    metric_row(
        metric_card("Observed tasks", n, "Real retrieval sessions", "i"),
        metric_card("Refined", "{k} / {n}".format(k=summ["refined"], n=n), "After the first action", "s"),
        metric_card("Manual scrolling", "{k} / {n}".format(k=summ["manual_scrolling"], n=n), "Includes INT005's intended method", "a"),
        metric_card("Median time", "{m:g} min".format(m=summ["median_time"]) if summ["median_time"] is not None else "—", "Approximate", "b"),
    )
    st.caption("Individual times: " + ", ".join("{k} {v:g} min".format(k=k, v=v) for k, v in summ["times"].items()))
    callout("Across the five observed retrieval tasks… counts are not population percentages. Names are not shown.")
    _interview_journey_cards()
    unknowns = I.unknown_clues(interviews)
    if unknowns:
        st.caption("Clues left unknown: " + "; ".join("{p} ({f})".format(p=pid, f=", ".join(fields)) for pid, fields in unknowns))
    section("Recurring observations")
    for item in I.recurring_observations(interviews):
        st.markdown("- " + item)


def page_explorer():
    page_header(
        "Evidence",
        "Evidence Explorer",
        "Public evidence, one example at a time. Paraphrases are not quotes.",
    )
    stream = st.radio(
        "Evidence stream",
        ["Targeted Vague-Memory Research", "Broad Public Research"],
        horizontal=True,
    )
    query = st.text_input("Search evidence...", placeholder="Search paraphrased evidence")
    if stream.startswith("Targeted"):
        _explorer_b(query)
    else:
        _explorer_a(query)


def _explorer_b(query):
    b_banner()
    df = b_valid.copy()
    if df.empty:
        callout("No analysed targeted examples yet.")
        return
    f1, f2, f3 = st.columns(3)
    sources = f1.multiselect("Source", sorted(df["source"].unique()))
    platforms = f2.multiselect("Platform", sorted(df["platform"].unique()))
    stages = f3.multiselect("Failure stage", [s for s in B.STAGE_DISPLAY if s in set(df["failure_stage"])])
    f4, f5, f6 = st.columns(3)
    clue_labels = list(B.CLUE_DISPLAY.values())
    clues = f4.multiselect("Remembered clue (all selected)", clue_labels)
    forgotten_options = sorted({t.strip() for v in df["forgotten_information"] for t in v.split(";") if t.strip()})
    forgotten = f5.multiselect("Forgotten information", forgotten_options)
    outcomes = f6.multiselect("Outcome", sorted(df["retrieval_outcome"].unique()))
    if sources:
        df = df[df["source"].isin(sources)]
    if platforms:
        df = df[df["platform"].isin(platforms)]
    if stages:
        df = df[df["failure_stage"].isin(stages)]
    label_to_field = {v: k for k, v in B.CLUE_DISPLAY.items()}
    for label in clues:
        df = df[df[label_to_field[label]] == "true"]
    if forgotten:
        df = df[df["forgotten_information"].apply(lambda v: any(f in [t.strip() for t in v.split(";")] for f in forgotten))]
    if outcomes:
        df = df[df["retrieval_outcome"].isin(outcomes)]
    if query:
        df = df[df["raw_text"].str.contains(query, case=False, regex=False)]
    st.caption("{m} of {n} examples match".format(m=len(df), n=len(b_valid)))
    for _, row in df.iterrows():
        remembered = B.remembered_list(row)
        evidence_card(
            row["record_id"],
            "{s} · {p}".format(s=row["source"], p=row["platform"]),
            row["raw_text"],
            "Paraphrased public evidence — not a verbatim quote",
            kind="public",
            href=row["url"],
            chips=[
                "Stage: {s}".format(s=row["failure_stage"]),
                "Remembered: {r}".format(r=", ".join(remembered) or "none evidenced"),
                "Strength: {e}".format(e=row["evidence_strength"]),
            ],
        )
        with st.expander("Structured analysis · {rid}".format(rid=row["record_id"])):
            st.markdown(
                "- Inclusion: {i}\n- Forgotten: {f}\n- Search: {ss}\n- Stage reason: {sr}\n"
                "- Refinement: {rf} · Workaround: {w} · Outcome: {o}\n- Audit: {a}\n- Sanitizer: {z}".format(
                    i=row["inclusion_reason"], f=row["forgotten_information"], ss=row["search_strategy"],
                    sr=row["failure_stage_reason"], rf=row["refinement_attempt"], w=row["workaround"],
                    o=row["retrieval_outcome"], a=row["audit_note"], z=row["sanitizer_changes"],
                )
            )


def _explorer_a(query):
    if corpus_a is None:
        st.error("Broad public research file not found.")
        return
    df = A.triaged(corpus_a).copy()
    f1, f2 = st.columns(2)
    sources = f1.multiselect("Source", sorted(df["source"].unique()))
    levels = f2.multiselect("Relevance", A.RELEVANCE_ORDER, format_func=lambda k: A.RELEVANCE_DISPLAY[k])
    if sources:
        df = df[df["source"].isin(sources)]
    if levels:
        df = df[df["relevance_level"].isin(levels)]
    if query:
        df = df[df["raw_text"].str.contains(query, case=False, regex=False)]
    st.caption("{m} of {n} conversations match. Broad public research was screened for relevance only, so it has no platform, failure-stage, clue or outcome fields.".format(
        m=len(df), n=len(A.triaged(corpus_a))))
    for _, row in df.head(40).iterrows():
        evidence_card(
            row["record_id"],
            "{s} · {d} · {r}".format(s=row["source"], d=row["date"] or "date not recorded", r=A.RELEVANCE_DISPLAY.get(row["relevance_level"], row["relevance_level"])),
            row["raw_text"],
            "Paraphrased public evidence — not a verbatim quote",
            kind="public",
            href=row["url"],
        )
    if len(df) > 40:
        st.caption("Showing the first 40 of {n} matches. Narrow the search or filters to see the rest.".format(n=len(df)))


def page_methodology():
    page_header(
        "About",
        "Methodology",
        "How the research sources were collected, screened, and kept separate.",
    )
    a_n = 0 if corpus_a is None else len(corpus_a)
    s_n = 0 if survey_all is None else len(survey_all)
    steps = [
        ("1", "Broad public research collection", "{n} public conversations with source URLs, stored as paraphrase.".format(n=a_n), "Not a sample of Google Photos users."),
        ("2", "AI relevance screening", "Each conversation is screened as vague-memory retrieval, a broader search issue, or unrelated.", "Screening labels still carry model uncertainty."),
        ("3", "Targeted vague-memory research", B.collection_phrase(b_status["valid"], b_status["source_total"]) + ".", "Purposefully selected. Not population prevalence."),
        ("4", "Structured AI extraction", "Photo type, remembered clues, forgotten information, stage, workaround, and outcome.", "The extractor can over-label. A quality check follows."),
        ("5", "AI quality review", "A second pass checks every field against the paraphrase.", "This is still a model judgment."),
        ("6", "Deterministic quality checks", "Code removes values the text does not support.", "Checks look for stated evidence. They do not invent new findings."),
        ("7", "Survey", "n = {n} convenience responses.".format(n=s_n), "Not population-representative. People could select more than one method, so order is unknown."),
        ("8", "Observed interviews", "{n} real tasks, shown only as INT001–INT005.".format(n=len(interviews)), "Times are approximate. A task with no failure is interview-only."),
        ("9", "Evidence triangulation", "Compare sources. Never combine their denominators.", "The targeted set is qualitative."),
    ]
    pipeline(
        [
            (n, t, "{d} Limitation: {l}".format(d=d, l=lim), "")
            for n, t, d, lim in steps
        ],
        columns=3,
    )
    left, right = st.columns(2)
    with left:
        section("What AI does")
        html_block(
            "<div class='stream'><p>Relevance screening<br>Structured extraction<br>"
            "Quality review<br>Grounded answers in Ask the Research</p></div>"
        )
    with right:
        section("What code does")
        html_block(
            "<div class='stream'><p>Statistics<br>Filters<br>"
            "Quality checks<br>Deterministic corrections<br>Citation validation</p></div>"
        )
    callout("A remembered clue is counted only when the text states it. A clue that is not evidenced is not the same as a forgotten one.")
    section("Targeted vague-memory research")
    callout(
        "{t} public examples were collected. {v} successfully completed the structured AI extraction, quality review and deterministic checks used in the final analysis. "
        "{e} collected examples were excluded from structured findings because their automated analysis did not complete reliably within the available model quota. "
        "No labels were fabricated for excluded examples. The analysed set is qualitative and purposefully selected, not representative of all Google Photos users.".format(
            v=b_status["valid"], e=b_status["excluded"], t=b_status["source_total"]
        )
    )


ASK_FEATURED = [
    "What are the main problems people face when trying to find an old photo?",
    "Where does the retrieval journey break most often?",
    "What do people remember when they forget the date?",
    "Do users remember more than they put into their first search?",
    "Why do people fall back to scrolling?",
    "Compare expression failure and evaluation failure.",
    "What did the five interviews reveal?",
    "What counter-evidence exists?",
]

ASK_GROUPS = OrderedDict([
    ("Understand the problem", [
        "What are the main problems people face when trying to find an old photo?",
        "What makes vague-memory retrieval difficult?",
        "Where does the retrieval journey break most often?",
        "What are the biggest barriers after the first search fails?",
    ]),
    ("Understand memory", [
        "What do people remember when they forget the date?",
        "Which clues do users remember most often?",
        "Do users remember more than they put into their first search?",
        "What kinds of contextual details survive when exact metadata is forgotten?",
    ]),
    ("Understand behaviour", [
        "Why do people fall back to scrolling?",
        "How do users refine after an unsuccessful first attempt?",
        "What workarounds do people use?",
        "What happens after a broad search returns too many photos?",
    ]),
    ("Compare failure types", [
        "Compare expression failure and evaluation failure.",
        "How is retrieval failure different from recovery failure?",
        "Which interview examples show evaluation friction?",
        "Which examples show expression friction?",
    ]),
    ("Primary research", [
        "What did the five interviews reveal?",
        "What did the survey reveal?",
        "Where do the interviews and survey agree?",
        "Where do they disagree?",
        "Which participant had the smoothest retrieval experience?",
    ]),
    ("Evidence and confidence", [
        "What evidence supports the idea that memory is richer than the initial query?",
        "What counter-evidence exists?",
        "Which findings are supported by more than one research source?",
        "Which findings are still uncertain?",
        "What are the biggest limitations of this research?",
    ]),
    ("Product opportunity", [
        "What user problem is most consistently supported?",
        "What behaviour should a product intervention try to improve?",
        "What does the research suggest about manual browsing?",
        "Where could Google Photos potentially help without requiring a perfect query?",
    ]),
])


def _research_bundle():
    return {
        "corpus_a": corpus_a,
        "corpus_b": corpus_b,
        "corpus_b_total": corpus_b_total,
        "survey": survey_all,
        "interviews": interviews,
    }


def _lookup_record(cite_id, records):
    for row in records:
        if row["id"] == cite_id:
            return row
    return None


def _queue_question(text):
    st.session_state.ask_question = (text or "").strip()
    st.session_state.ask_status = "queued"


def _render_ask_result(result):
    if not result:
        return
    if result.get("mode") == "invalid":
        callout(result.get("error") or "Enter a question.", kind="note")
        return
    html_block("<div class='ask-q'>{q}</div>".format(q=esc(result.get("question") or "")))
    if result.get("mode") == "scope":
        callout(result.get("answer") or "", kind="note")
        return
    label = "AI synthesis" if result.get("mode") == "ai" else "Evidence summary"
    html_block("<div class='ask-label'>{l}</div>".format(l=esc(label)))
    if result.get("fallback_note"):
        st.caption(result["fallback_note"])
    html_block("<div class='ask-label'>Answer</div>")
    st.markdown(result.get("answer") or "The current research does not contain enough evidence to answer that confidently.")
    streams = result.get("streams") or []
    if streams:
        html_block("<div class='ask-label'>Evidence streams used</div>")
        st.caption(" · ".join(streams))
    citations = result.get("citations") or []
    records = result.get("records") or []
    if citations or records:
        html_block("<div class='ask-label'>Supporting evidence</div>")
        chips = "".join(pill(cite["id"], "muted") for cite in citations)
        if chips:
            html_block("<div class='chip-row'>{c}</div>".format(c=chips))
        shown = 0
        for cite in citations:
            if str(cite["id"]).startswith("STAT_"):
                continue
            row = _lookup_record(cite["id"], records)
            if row is None:
                continue
            kind = {"public": "public", "survey": "survey", "interview": "interview"}.get(row["evidence_type"], "public")
            evidence_card(
                row["id"],
                "{k} · {l}".format(k=row["stream"], l=row["labels"]),
                row["excerpt"],
                "Paraphrased public evidence — not a verbatim quote"
                if row["stream"] in ("Broad Public Research", "Targeted Vague-Memory Research")
                else row["evidence_type"],
                kind=kind,
                href=row.get("url", ""),
            )
            shown += 1
            if shown >= 6:
                break
    if result.get("limitations"):
        html_block("<div class='ask-label'>Limitation</div>")
        callout(result["limitations"], kind="note")


def page_ask():
    from src.qa import run_research_query

    st.session_state.setdefault("ask_question", "")
    st.session_state.setdefault("ask_result", None)
    st.session_state.setdefault("ask_status", "idle")

    page_header(
        "AI · Grounded chat",
        "Ask the Research",
        "Ask questions across public evidence, surveys and observed retrieval tasks.",
    )
    callout("Answers stay inside this project's evidence. Counts come from the research data, not from the model.", kind="note")
    callout(B.QUALITATIVE_NOTE, kind="note")

    def _on_pill():
        value = st.session_state.get("ask_pills")
        if isinstance(value, str) and value.strip():
            _queue_question(value)

    st.pills("Suggested questions", ASK_FEATURED, key="ask_pills", on_change=_on_pill)
    with st.expander("More questions"):
        for group, prompts in ASK_GROUPS.items():
            st.caption(group)
            for index, prompt in enumerate(prompts):
                if prompt in ASK_FEATURED:
                    continue
                st.button(
                    prompt,
                    key="more_{g}_{i}".format(g=group, i=index),
                    on_click=_queue_question,
                    args=(prompt,),
                )
    with st.form("ask_form", clear_on_submit=False, border=False):
        typed = st.text_input(
            "Research question",
            placeholder="Ask a question about the research...",
            label_visibility="collapsed",
            key="ask_typed",
        )
        asked = st.form_submit_button("Ask", type="primary")
    if asked:
        if not (typed or "").strip():
            st.session_state.ask_status = "invalid"
            st.session_state.ask_question = ""
        else:
            _queue_question(typed)

    if st.session_state.ask_status == "invalid":
        callout("Enter a question.", kind="note")

    if st.session_state.ask_status == "queued":
        with st.status("Searching the research...", expanded=True) as ask_status:
            def _progress(label):
                ask_status.update(label=label)

            try:
                result = run_research_query(
                    st.session_state.ask_question,
                    _research_bundle(),
                    on_progress=_progress,
                )
            except Exception:
                result = {
                    "question": st.session_state.ask_question,
                    "mode": "evidence",
                    "answer": "The current research does not contain enough evidence to answer that confidently.",
                    "citations": [],
                    "records": [],
                    "sources": [],
                    "streams": [],
                    "limitations": "",
                    "fallback_note": "",
                    "error": "",
                    "insufficient_evidence": True,
                }
            ask_status.update(label="Answer ready", state="complete", expanded=False)
        st.session_state.ask_result = result
        st.session_state.ask_status = "done"

    if st.session_state.ask_status == "done":
        _render_ask_result(st.session_state.ask_result)


if page != "Ask the Research":
    floating_ask_button()
{
    "Research Overview": page_overview,
    "Retrieval Landscape": page_landscape,
    "What People Remember": page_remember,
    "Where Retrieval Breaks": page_breaks,
    "Retrieval Behaviour": page_behaviour,
    "Evidence Explorer": page_explorer,
    "Survey & Interviews": page_primary,
    "Methodology": page_methodology,
    "Ask the Research": page_ask,
}[page]()
