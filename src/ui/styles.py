"""Global CSS for the Discovery Agent. Injected once at app start."""
from src.ui import tokens as T

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"], .stApp, .stMarkdown, p, h1, h2, h3, h4, label {{
  font-family: {font} !important;
}}
.stApp {{ background: {page}; color: {ink}; }}
header[data-testid="stHeader"] {{
  background: {page};
}}
[data-testid="stDecoration"],
.stAppDeployButton {{ display: none !important; }}
footer {{ visibility: hidden; }}
[data-testid="stToolbar"] {{
  display: flex !important;
  visibility: visible !important;
}}
[data-testid="stExpandSidebarButton"] {{
  display: inline-flex !important;
  visibility: visible !important;
  opacity: 1 !important;
  background: {surface} !important;
  border: 1px solid {line} !important;
  border-radius: 8px !important;
  color: {ink} !important;
  box-shadow: none !important;
  margin: 6px 0 0 8px;
}}
[data-testid="stExpandSidebarButton"] span,
[data-testid="stExpandSidebarButton"] svg {{
  color: {ink} !important;
  fill: {ink} !important;
}}
.block-container {{
  padding: 1.35rem 2.1rem 3.2rem 2.1rem;
  max-width: 1180px;
}}
section[data-testid="stSidebar"] {{
  background: {sidebar};
  border-right: 1px solid {line};
}}
section[data-testid="stSidebar"] > div {{ padding-top: 1rem; padding-left: 0.55rem; padding-right: 0.55rem; }}
section[data-testid="stSidebar"] .stRadio {{ margin-bottom: 0.1rem; }}
section[data-testid="stSidebar"] label p {{ font-size: 0.84rem !important; }}

section[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"],
section[data-testid="stSidebar"] [data-testid="stBaseButton-primary"],
section[data-testid="stSidebar"] button[kind="secondary"],
section[data-testid="stSidebar"] button[kind="primary"] {{
  background: transparent !important;
  color: {ink2} !important;
  border: none !important;
  box-shadow: none !important;
  justify-content: flex-start !important;
  text-align: left !important;
  font-weight: 500 !important;
  font-size: 0.84rem !important;
  padding: 0.38rem 0.7rem !important;
  border-radius: 8px !important;
  min-height: 0 !important;
  line-height: 1.25 !important;
}}
section[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:hover,
section[data-testid="stSidebar"] button[kind="secondary"]:hover {{
  background: {blue_soft} !important;
  color: {blue} !important;
}}
section[data-testid="stSidebar"] [data-testid="stBaseButton-primary"],
section[data-testid="stSidebar"] button[kind="primary"] {{
  background: {blue_soft} !important;
  color: {blue} !important;
  font-weight: 600 !important;
}}
section[data-testid="stSidebar"] .stButton {{ margin-bottom: 2px; }}
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {{
  font-size: 0.72rem !important; color: {muted} !important;
}}

.brand-mark {{
  font-size: 0.95rem; font-weight: 700; color: {ink}; letter-spacing: -0.02em;
  padding: 0 0.35rem;
}}
.brand-sub {{ color: {muted}; font-size: 0.75rem; margin: 2px 0 10px 0; padding: 0 0.35rem; }}
.nav-group {{
  color: {muted2}; font-size: 0.66rem; font-weight: 600; letter-spacing: 0.08em;
  text-transform: uppercase; margin: 12px 0 3px 6px;
}}

.page-kicker {{
  color: {muted}; font-size: 0.75rem; font-weight: 500; margin-bottom: 4px;
}}
.page-title {{
  font-size: 1.68rem; font-weight: 700; letter-spacing: -0.03em;
  color: {ink}; margin: 0 0 4px 0; line-height: 1.2;
}}
.page-lead {{ color: {ink2}; font-size: 0.95rem; margin: 0 0 1.15rem 0; max-width: 46rem; }}
.section-label {{
  font-size: 0.72rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase;
  color: {muted}; margin: 1.35rem 0 0.55rem 0;
}}

.metric-row {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }}
.metric {{
  background: {surface}; border: 1px solid {line}; border-radius: 14px; padding: 16px 18px;
}}
.metric .kicker {{ font-size: 0.7rem; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; }}
.metric .value {{ font-size: 1.85rem; font-weight: 700; letter-spacing: -0.03em; line-height: 1.1; margin: 6px 0 4px 0; color: {ink}; }}
.metric .hint {{ color: {muted}; font-size: 0.8rem; }}
.metric.a .kicker {{ color: {blue}; }}
.metric.b .kicker {{ color: {teal}; }}
.metric.s .kicker {{ color: #5B4B8A; }}
.metric.i .kicker {{ color: {amber}; }}

.pill {{
  display: inline-block; font-size: 0.72rem; font-weight: 600; padding: 3px 9px;
  border-radius: 999px; margin-top: 8px;
}}
.pill-amber {{ background: {amber_soft}; color: {amber}; }}
.pill-green {{ background: {green_soft}; color: {green}; }}
.pill-blue {{ background: {blue_soft}; color: {blue}; }}
.pill-teal {{ background: {teal_soft}; color: {teal}; }}
.pill-muted {{ background: {line_soft}; color: {muted}; }}

.pipeline {{ display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 10px; }}
.pipe {{
  background: {surface}; border: 1px solid {line}; border-radius: 12px; padding: 12px 12px 10px 12px;
}}
.pipe .n {{ font-size: 0.7rem; font-weight: 700; color: {muted2}; }}
.pipe .t {{ font-size: 0.86rem; font-weight: 600; color: {ink}; margin: 4px 0 2px 0; }}
.pipe .d {{ font-size: 0.75rem; color: {muted}; line-height: 1.35; }}
.pipe.done {{ border-color: {teal}33; background: {teal_soft}; }}
.pipe.active {{ border-color: {amber_line}; background: {amber_soft}; }}
.pipe.hi {{ border-color: {amber_line}; background: {amber_soft}; }}

.stream-grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }}
.stream {{
  background: {surface}; border: 1px solid {line}; border-radius: 14px; padding: 16px 18px;
}}
.stream h4 {{ margin: 0 0 6px 0; font-size: 0.92rem; letter-spacing: 0.02em; }}
.stream p {{ margin: 0; color: {ink2}; font-size: 0.84rem; line-height: 1.45; }}
.stream .tiny {{ margin-top: 10px; color: {muted}; font-size: 0.75rem; }}

.signal-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
.signal {{
  background: {surface}; border: 1px solid {line}; border-radius: 14px; padding: 16px 18px;
}}
.signal .idx {{ font-size: 0.75rem; font-weight: 700; color: {blue}; letter-spacing: 0.04em; }}
.signal h4 {{ margin: 4px 0 6px 0; font-size: 0.95rem; }}
.signal p {{ margin: 0; color: {ink2}; font-size: 0.84rem; line-height: 1.45; }}

.journey {{ display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 8px; }}
.jstep {{
  background: {surface}; border: 1px solid {line}; border-radius: 12px; padding: 12px 10px;
  min-height: 108px;
}}
.jstep .n {{ font-size: 0.68rem; font-weight: 700; color: {muted2}; }}
.jstep .t {{ font-size: 0.82rem; font-weight: 700; color: {ink}; margin: 3px 0 4px 0; }}
.jstep .d {{ font-size: 0.74rem; color: {muted}; line-height: 1.35; }}
.jstep.hi {{ border-color: {amber_line}; background: {amber_soft}; }}
.jstep.ok {{ border-color: {green}33; background: {green_soft}; }}

.stage-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
.stage-card {{
  background: {surface}; border: 1px solid {line}; border-radius: 14px; padding: 14px 16px;
}}
.stage-card.hi {{ border-color: {amber_line}; background: {amber_soft}; }}
.stage-card .n {{ font-size: 0.72rem; font-weight: 700; color: {muted}; }}
.stage-card h4 {{ margin: 4px 0 6px 0; font-size: 0.95rem; color: {ink}; }}
.stage-card p {{ margin: 0; color: {ink2}; font-size: 0.84rem; line-height: 1.45; }}
.stage-card .count {{ margin-top: 10px; font-size: 0.78rem; color: {muted}; font-weight: 600; }}

.ev-card {{
  background: {surface}; border: 1px solid {line}; border-radius: 14px; padding: 14px 16px; margin: 0 0 10px 0;
}}
.ev-card .meta {{ color: {muted}; font-size: 0.75rem; margin-bottom: 6px; }}
.ev-card .body {{ color: {ink2}; font-size: 0.88rem; line-height: 1.45; }}
.ev-card .foot {{ margin-top: 8px; font-size: 0.75rem; color: {muted}; }}
.ev-card.public {{ border-left: 3px solid {teal}; }}
.ev-card.survey {{ border-left: 3px solid #5B4B8A; }}
.ev-card.interview {{ border-left: 3px solid {amber}; }}
.ev-card.ok {{ border-left: 3px solid {green}; background: {green_soft}; }}
.quote {{
  font-size: 0.92rem; color: {ink}; margin: 8px 0 4px 0; line-height: 1.4;
}}
.ev-card a {{ color: {blue}; text-decoration: none; font-weight: 600; }}

.jcard {{
  background: {surface}; border: 1px solid {line}; border-radius: 14px;
  padding: 14px 16px; margin: 0 0 12px 0;
}}
.jcard.interview {{ border-left: 3px solid {amber}; }}
.jcard.ok {{ border-left: 3px solid {green}; background: {green_soft}; }}
.jcard-head {{
  display: flex; justify-content: space-between; align-items: flex-start; gap: 12px;
  margin-bottom: 8px;
}}
.jcard-head .pid {{ font-weight: 700; color: {ink}; margin-right: 8px; }}
.jcard-head .tgt {{ color: {ink2}; font-size: 0.88rem; }}
.jcard-label {{
  font-size: 0.68rem; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase;
  color: {muted}; margin: 4px 0 2px 0;
}}
.jcard-remember {{ color: {ink2}; font-size: 0.86rem; margin-bottom: 10px; }}
.jgrid {{
  display: grid; grid-template-columns: 1fr 1fr; gap: 6px 16px; margin-bottom: 8px;
}}
.jgrid .k {{ display: block; font-size: 0.68rem; color: {muted}; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; }}
.jgrid .v {{ display: block; font-size: 0.84rem; color: {ink}; }}
.jcard .quote {{
  background: {surface_soft}; border-radius: 8px; padding: 8px 10px; margin: 8px 0;
}}
.jcard .foot {{ font-size: 0.75rem; color: {muted}; }}

.hbar {{
  display: grid; grid-template-columns: minmax(110px, 30%) 1fr 42px; gap: 8px; align-items: center;
  margin: 5px 0;
}}
.hbar .lab {{ font-size: 0.78rem; color: {ink2}; line-height: 1.25; }}
.hbar .track {{ background: {line_soft}; border-radius: 6px; height: 8px; overflow: hidden; }}
.hbar .fill {{ height: 8px; border-radius: 6px; }}
.hbar .n {{ font-size: 0.8rem; font-weight: 600; color: {ink}; text-align: right; }}

.callout {{
  border: 1px solid {line}; background: {surface_soft}; border-radius: 12px;
  padding: 10px 14px; font-size: 0.82rem; color: {ink2}; margin: 8px 0 14px 0;
}}
.callout.warn {{ background: {amber_soft}; border-color: {amber_line}; color: {amber}; }}
.callout.note {{ background: {blue_soft}; border-color: {blue_line}; }}

.chip-row {{ display: flex; flex-wrap: wrap; gap: 6px; margin: 4px 0 10px 0; }}
.chip-row .pill {{ margin-top: 0; }}

.ask-brief {{
  background: {surface}; border: 1px solid {line}; border-radius: 14px;
  padding: 16px 18px; margin: 0 0 14px 0;
}}
.ask-q {{
  font-size: 0.92rem; font-weight: 600; color: {ink}; margin: 0 0 12px 0;
}}
.ask-label {{
  font-size: 0.68rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase;
  color: {muted}; margin: 12px 0 6px 0;
}}
.ask-body {{ color: {ink2}; font-size: 0.9rem; line-height: 1.5; }}

div[data-testid="stChatInput"] {{
  background: {surface}; border: 1px solid {line}; border-radius: 14px;
}}
.stTabs [data-baseweb="tab-list"] {{ gap: 6px; }}
.stTabs [data-baseweb="tab"] {{
  background: {surface_soft}; border-radius: 999px; padding: 6px 14px;
}}
.stTabs [aria-selected="true"] {{ background: {blue_soft} !important; color: {blue} !important; }}

@media (max-width: 1100px) {{
  .metric-row, .stream-grid, .pipeline, .journey, .stage-grid, .jgrid, .signal-grid {{
    grid-template-columns: 1fr 1fr;
  }}
  .block-container {{ padding: 1rem 1.1rem 2.4rem 1.1rem; }}
}}
.stElementContainer:has(a.ask-launcher) {{
  position: fixed !important;
  right: 24px !important;
  bottom: 24px !important;
  z-index: 1000002 !important;
  width: auto !important;
  height: auto !important;
  margin: 0 !important;
  padding: 0 !important;
  overflow: visible !important;
  background: transparent !important;
  border: none !important;
  pointer-events: none;
}}
a.ask-launcher {{
  pointer-events: auto;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background-color: {blue};
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='white' d='M5 4.5A2.5 2.5 0 0 1 7.5 2h9A2.5 2.5 0 0 1 19 4.5v8A2.5 2.5 0 0 1 16.5 15H10l-4.2 3.2c-.5.4-1.3 0-1.3-.7V15H7.5A2.5 2.5 0 0 1 5 12.5v-8z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: center;
  background-size: 26px 26px;
  box-shadow: 0 8px 20px rgba(17, 24, 39, 0.16);
  text-decoration: none;
  color: #ffffff;
}}
a.ask-launcher:hover,
a.ask-launcher:focus-visible {{
  transform: scale(1.05);
  outline: 3px solid {blue_line};
  outline-offset: 3px;
}}
.ask-launcher-label {{
  position: absolute;
  right: calc(100% + 10px);
  top: 50%;
  transform: translateY(-50%);
  background: {ink};
  color: #ffffff;
  font-size: 0.78rem;
  font-weight: 600;
  line-height: 1;
  padding: 7px 10px;
  border-radius: 8px;
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
}}
a.ask-launcher:hover .ask-launcher-label,
a.ask-launcher:focus-visible .ask-launcher-label {{
  opacity: 1;
}}

@media (max-width: 720px) {{
  .metric-row, .stream-grid, .pipeline, .journey, .stage-grid, .jgrid, .signal-grid {{
    grid-template-columns: 1fr;
  }}
  .stElementContainer:has(a.ask-launcher) {{
    right: 16px !important;
    bottom: 16px !important;
  }}
  a.ask-launcher {{
    width: 46px;
    height: 46px;
    background-size: 22px 22px;
  }}
}}
</style>
""".format(
    font=T.FONT,
    page=T.PAGE,
    surface=T.SURFACE,
    surface_soft=T.SURFACE_SOFT,
    sidebar=T.SIDEBAR,
    line=T.LINE,
    line_soft=T.LINE_SOFT,
    ink=T.INK,
    ink2=T.INK_2,
    muted=T.MUTED,
    muted2=T.MUTED_2,
    blue=T.BLUE,
    blue_soft=T.BLUE_SOFT,
    blue_line=T.BLUE_LINE,
    teal=T.TEAL,
    teal_soft=T.TEAL_SOFT,
    amber=T.AMBER,
    amber_soft=T.AMBER_SOFT,
    amber_line=T.AMBER_LINE,
    green=T.GREEN,
    green_soft=T.GREEN_SOFT,
)
