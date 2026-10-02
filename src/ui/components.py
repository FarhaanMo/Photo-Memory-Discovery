"""Reusable presentation pieces. Counts are passed in; this file does not compute research."""
import html

import plotly.graph_objects as go
import streamlit as st

from src.ui import tokens as T


def inject_css():
    from src.ui.styles import CSS
    st.markdown(CSS, unsafe_allow_html=True)


def esc(value):
    return html.escape("" if value is None else str(value))


def html_block(markup):
    st.markdown(markup, unsafe_allow_html=True)


def floating_ask_button():
    """Fixed bottom-right launcher. Navigation is a same-app query link, not a new tab."""
    html_block(
        "<a class='ask-launcher' href='?ask=1' title='Ask the Research' aria-label='Ask the Research'>"
        "<span class='ask-launcher-label' aria-hidden='true'>Ask the Research</span>"
        "</a>"
    )


def page_header(kicker, title, lead):
    html_block(
        "<div class='page-kicker'>{k}</div><div class='page-title'>{t}</div>"
        "<p class='page-lead'>{l}</p>".format(k=esc(kicker), t=esc(title), l=esc(lead))
    )


def section(label):
    html_block("<div class='section-label'>{l}</div>".format(l=esc(label)))


def callout(text, kind=""):
    klass = "callout warn" if kind == "warn" else ("callout note" if kind == "note" else "callout")
    html_block("<div class='{k}'>{t}</div>".format(k=klass, t=esc(text)))


def pill(text, kind="muted"):
    return "<span class='pill pill-{k}'>{t}</span>".format(k=esc(kind), t=esc(text))


def metric_card(kicker, value, hint, kind="a", extra_html=""):
    return (
        "<div class='metric {kind}'><div class='kicker'>{k}</div>"
        "<div class='value'>{v}</div><div class='hint'>{h}</div>{x}</div>"
    ).format(kind=esc(kind), k=esc(kicker), v=esc(value), h=esc(hint), x=extra_html)


def metric_row(*cards):
    html_block("<div class='metric-row'>{c}</div>".format(c="".join(cards)))


def source_tag(kind):
    labels = {
        "corpus_a": ("Broad Public Research", "blue"),
        "corpus_b": ("Targeted Vague-Memory Research", "teal"),
        "survey": ("Survey · Primary research", "blue"),
        "interview": ("Interviews · Observed tasks", "amber"),
    }
    text, tone = labels[kind]
    html_block(pill(text, tone))


def pipeline(steps, columns=None):
    """steps: iterable of (number, title, detail, kind)."""
    items = []
    for number, title, detail, kind in steps:
        items.append(
            "<div class='pipe {k}'><div class='n'>{n}</div><div class='t'>{t}</div>"
            "<div class='d'>{d}</div></div>".format(
                k=esc(kind), n=esc(number), t=esc(title), d=esc(detail)
            )
        )
    style = "" if not columns else " style='grid-template-columns:repeat({c},1fr)'".format(c=int(columns))
    html_block("<div class='pipeline'{s}>{h}</div>".format(s=style, h="".join(items)))


def journey_strip(steps):
    """steps: iterable of (number, title, detail, kind)."""
    items = []
    for number, title, detail, kind in steps:
        items.append(
            "<div class='jstep {k}'><div class='n'>{n}</div><div class='t'>{t}</div>"
            "<div class='d'>{d}</div></div>".format(
                k=esc(kind), n=esc(number), t=esc(title), d=esc(detail)
            )
        )
    html_block("<div class='journey'>{h}</div>".format(h="".join(items)))


def hbars(counts, color, hide_zero=False, max_n=None):
    items = [(k, int(v)) for k, v in counts.items() if int(v) > 0 or not hide_zero]
    if not items:
        callout("No data yet.")
        return
    ceiling = max_n if max_n else max(v for _, v in items) or 1
    rows = []
    for label, value in items:
        width = 0 if ceiling == 0 else int(100 * value / ceiling)
        rows.append(
            "<div class='hbar'><div class='lab'>{l}</div><div class='track'>"
            "<div class='fill' style='width:{w}%;background:{c}'></div></div>"
            "<div class='n'>{n}</div></div>".format(
                l=esc(label), w=width, c=color, n=value
            )
        )
    html_block("".join(rows))


def bar(counts, kind, title, denominator_label, hide_zero=False):
    """Plotly fallback when a labelled chart is useful. Counts only."""
    items = [(k, v) for k, v in counts.items() if v > 0 or not hide_zero]
    if not items:
        callout("No data yet.")
        return
    st.caption("{t} · {d}".format(t=title, d=denominator_label))
    hbars(dict(items), T.STREAM.get(kind, T.BLUE), hide_zero=hide_zero)


def evidence_card(record_id, meta, body, footer, kind="public", href="", chips=None):
    link = ""
    if href:
        link = " · <a href='{u}' target='_blank' rel='noopener noreferrer'>View source ↗</a>".format(u=esc(href))
    chip_html = ""
    if chips:
        chip_html = "<div class='chip-row'>{c}</div>".format(
            c="".join(pill(item, "muted") for item in chips)
        )
    html_block(
        "<div class='ev-card {k}'><div class='meta'><b>{rid}</b> · {m}</div>"
        "{chips}<div class='body'>{b}</div><div class='foot'>{f}{l}</div></div>".format(
            k=esc(kind), rid=esc(record_id), m=esc(meta), chips=chip_html,
            b=esc(body), f=esc(footer), l=link
        )
    )


def journey_card(
    pid, target, remembered, first_action, searched, first_result,
    refine, workaround, time_min, attempts, stage, quote, path, kind="interview",
):
    badge = "Low friction" if kind == "ok" else ("Moderate friction" if stage == "evaluation" else "High friction")
    tone = "green" if kind == "ok" else "amber"
    html_block(
        "<div class='jcard {k}'>"
        "<div class='jcard-head'><div><span class='pid'>{pid}</span>"
        "<span class='tgt'>Target: {tgt}</span></div>{badge}</div>"
        "<div class='jcard-label'>What they remember</div>"
        "<div class='jcard-remember'>{rem}</div>"
        "<div class='jgrid'>"
        "<div><span class='k'>First action</span><span class='v'>{fa}</span></div>"
        "<div><span class='k'>Searched</span><span class='v'>{sq}</span></div>"
        "<div><span class='k'>First result</span><span class='v'>{fr}</span></div>"
        "<div><span class='k'>Refinement</span><span class='v'>{rf}</span></div>"
        "<div><span class='k'>Workaround</span><span class='v'>{w}</span></div>"
        "<div><span class='k'>Time to target</span><span class='v'>about {tm} min · {a} attempt(s)</span></div>"
        "</div>"
        "<div class='quote'>“{q}”</div>"
        "<div class='foot'>Stage: {st} · {path}</div>"
        "</div>".format(
            k=esc(kind), pid=esc(pid), tgt=esc(target), badge=pill(badge, tone),
            rem=esc(remembered), fa=esc(first_action), sq=esc(searched),
            fr=esc(first_result), rf=esc(refine), w=esc(workaround),
            tm=esc(time_min), a=esc(attempts), q=esc(quote), st=esc(stage), path=esc(path),
        )
    )


def plotly_bar(counts, color, title, denominator_label, hide_zero=False):
    items = [(k, int(v)) for k, v in counts.items() if int(v) > 0 or not hide_zero]
    if not items:
        callout("No data yet.")
        return
    labels = [k for k, _ in items][::-1]
    values = [v for _, v in items][::-1]
    fig = go.Figure(
        go.Bar(
            x=values, y=labels, orientation="h", marker_color=color,
            text=values, textposition="outside", cliponaxis=False,
            hovertemplate="%{y}: %{x}<extra></extra>",
        )
    )
    fig.update_layout(
        title=dict(text="{t}<br><sup>{d}</sup>".format(t=title, d=denominator_label), x=0, font=dict(size=14, color=T.INK)),
        height=88 + 32 * len(items),
        margin=dict(l=8, r=36, t=52, b=8),
        xaxis=dict(visible=False, range=[0, max(values) * 1.18 if max(values) else 1]),
        yaxis=dict(tickfont=dict(size=12, color=T.INK_2)),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        font=dict(family=T.FONT),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
