"""Flat, bright, light design system for SafeBridge AI.
Light neutral base with a small, purposeful color system layered on top:
role cards each get their own identity color, status/priority badges use
real semantic colors (not one flat accent for everything), while cards and
surfaces stay flat with hairline borders — no gradients, no drop shadows.
"""

def apply_styles():
    import streamlit as st
    st.markdown("""<style>
    :root {
        --sb-bg: #FFFFFF;
        --sb-surface: #F9FAFB;
        --sb-surface-hover: #F3F4F6;
        --sb-border: #E5E7EB;
        --sb-border-subtle: #F3F4F6;
        --sb-ink: #111827;
        --sb-muted: #6B7280;
        --sb-faint: #9CA3AF;

        /* Role identity colors — each section of the app gets its own tone */
        --sb-blue: #2563EB;       --sb-blue-tint: #EFF6FF;   --sb-blue-border: #BFDBFE;  --sb-blue-text: #1D4ED8;
        --sb-purple: #7C3AED;     --sb-purple-tint: #F5F3FF; --sb-purple-border: #DDD6FE; --sb-purple-text: #6D28D9;
        --sb-amber: #D97706;      --sb-amber-tint: #FFFBEB;  --sb-amber-border: #FDE68A; --sb-amber-text: #B45309;
        --sb-green: #639922;      --sb-green-hover: #55831C; --sb-green-tint: #EAF3DE;  --sb-green-border: #97C459; --sb-green-text: #27500A; --sb-green-dark: #173404;

        /* Semantic status colors */
        --sb-red: #DC2626;   --sb-red-tint: #FEF2F2;   --sb-red-border: #FECACA;
        --sb-orange: #EA580C; --sb-orange-tint: #FFF7ED; --sb-orange-border: #FED7AA;
        --sb-teal: #0D9488;   --sb-teal-tint: #F0FDFA;  --sb-teal-border: #99F6E4;
    }

    .stApp {
        background: #FFFFFF !important;
        color: var(--sb-ink) !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
    }
    .block-container { max-width: 1140px; padding-top: 1.8rem; padding-bottom: 3rem; }
    .stApp p, .stApp label, .stApp li, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp span {
        color: var(--sb-ink);
    }

    [data-testid="stSidebar"] { background: #F9FAFB !important; border-right: 1px solid var(--sb-border) !important; }
    [data-testid="stSidebar"] hr { border-color: var(--sb-border) !important; }

    .sb-page-header {
        background: #FFFFFF; border-bottom: 1px solid var(--sb-border);
        padding: 1.5rem 0 1.2rem 0; margin-bottom: 1.5rem;
    }
    .sb-page-header h1 { font-size: 1.85rem; font-weight: 700; letter-spacing: -0.02em; margin: 0 0 0.35rem 0; color: var(--sb-ink) !important; }
    .sb-page-header p { font-size: 0.95rem; color: var(--sb-muted) !important; margin: 0; line-height: 1.45; }

    /* ── Base flat card ── */
    .card, .sb-card {
        background: #FFFFFF !important; color: var(--sb-ink) !important;
        padding: 1.25rem 1.4rem; border-radius: 12px !important;
        border: 1px solid var(--sb-border) !important; box-shadow: none !important;
        transition: border-color 0.15s ease !important; transform: none !important; margin-bottom: 1rem;
    }
    .card:hover, .sb-card:hover { border-color: #D1D5DB !important; transform: none !important; box-shadow: none !important; }
    .card h2, .card h3, .sb-card h3 { font-size: 1.05rem; font-weight: 600; margin: 0.5rem 0 0.25rem 0; color: var(--sb-ink) !important; }
    .card p.muted, .sb-card p.muted { font-size: 0.85rem; color: var(--sb-muted) !important; margin: 0 0 0.5rem 0; line-height: 1.4; }

    /* ── Icon chip inside a card — carries the color, card itself stays flat ── */
    .sb-icon-chip {
        display: inline-flex; align-items: center; justify-content: center;
        width: 40px; height: 40px; border-radius: 10px; margin-bottom: 0.6rem;
    }
    .sb-icon-chip.blue   { background: var(--sb-blue-tint);   color: var(--sb-blue); }
    .sb-icon-chip.purple { background: var(--sb-purple-tint); color: var(--sb-purple); }
    .sb-icon-chip.amber  { background: var(--sb-amber-tint);  color: var(--sb-amber); }
    .sb-icon-chip.green  { background: var(--sb-green-tint);  color: var(--sb-green); }
    .sb-icon-chip.teal   { background: var(--sb-teal-tint);   color: var(--sb-teal); }

    /* ── Anonymous / highlighted card keeps its tint background ── */
    .sb-card-highlight {
        background: var(--sb-green-tint) !important; border: 1px solid var(--sb-green-border) !important;
        border-radius: 12px !important; padding: 1.25rem 1.4rem; margin-bottom: 1rem;
        box-shadow: none !important; transform: none !important;
    }
    .sb-card-highlight h3 { color: var(--sb-green-dark) !important; font-size: 1.05rem; font-weight: 600; margin: 0.5rem 0 0.25rem 0; }
    .sb-card-highlight p { color: var(--sb-green-text) !important; font-size: 0.85rem; margin: 0 0 0.5rem 0; }

    [data-testid="stMetric"] {
        background: #FFFFFF !important; border: 1px solid var(--sb-border) !important;
        border-radius: 12px !important; padding: 0.9rem 1.1rem !important; box-shadow: none !important;
    }
    [data-testid="stMetricLabel"] p { font-size: 0.82rem !important; font-weight: 500 !important; color: var(--sb-muted) !important; text-transform: capitalize; }
    [data-testid="stMetricValue"] div { font-size: 1.6rem !important; font-weight: 700 !important; color: var(--sb-ink) !important; }

    /* ── Primary buttons: blue is the default primary action color; the
         anonymous-report / speak-up button uses green specifically (see
         .sb-btn-green helper class applied via markdown wrapper) ── */
    button[kind="primary"], .stButton > button[kind="primary"] {
        background: var(--sb-blue) !important; color: #FFFFFF !important; border: 1px solid var(--sb-blue) !important;
        border-radius: 8px !important; padding: 0.55rem 1rem !important; font-weight: 600 !important;
        font-size: 0.9rem !important; box-shadow: none !important; transition: background 0.15s ease !important;
    }
    button[kind="primary"]:hover, .stButton > button[kind="primary"]:hover {
        background: #1D4ED8 !important; border-color: #1D4ED8 !important; color: #FFFFFF !important; transform: none !important; filter: none !important;
    }

    .stButton > button:not([kind="primary"]) {
        background: #FFFFFF !important; color: var(--sb-ink) !important; border: 1px solid var(--sb-border) !important;
        border-radius: 8px !important; padding: 0.55rem 1rem !important; font-weight: 500 !important;
        font-size: 0.9rem !important; box-shadow: none !important; transition: background 0.15s ease, border-color 0.15s ease !important; transform: none !important;
    }
    .stButton > button:not([kind="primary"]):hover {
        background: var(--sb-surface) !important; border-color: #D1D5DB !important; color: var(--sb-ink) !important; transform: none !important; filter: none !important;
    }

    /* Force green specifically for anonymous-report / sign-in-style calls to action */
    div[data-testid="stVerticalBlock"]:has(> .sb-anon-marker) .stButton > button[kind="primary"] {
        background: var(--sb-green) !important; border-color: var(--sb-green) !important;
    }
    div[data-testid="stVerticalBlock"]:has(> .sb-anon-marker) .stButton > button[kind="primary"]:hover {
        background: var(--sb-green-hover) !important; border-color: var(--sb-green-hover) !important;
    }

    .sb-notice-block { background: #F9FAFB; border: 1px solid var(--sb-border); border-radius: 10px; padding: 1.1rem 1.3rem; margin: 1rem 0 1.25rem 0; }
    .sb-notice-title { font-size: 0.9rem; font-weight: 600; color: var(--sb-ink); margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.45rem; }
    .sb-notice-body { font-size: 0.83rem; color: var(--sb-muted); line-height: 1.5; }

    .sb-ai-disclaimer { background: #F9FAFB; border-left: 3px solid #9CA3AF; padding: 0.6rem 0.9rem; margin: 0.75rem 0; font-size: 0.82rem; color: var(--sb-muted); border-radius: 0 6px 6px 0; }

    /* ── Semantic badges — priority / status now carry real meaning-based color ── */
    .sb-badge { display: inline-flex; align-items: center; gap: 0.35rem; font-size: 0.78rem; font-weight: 500; padding: 0.2rem 0.55rem; border-radius: 6px; border: 1px solid transparent; }
    .sb-badge-neutral { background: #F3F4F6; color: #374151; border-color: #E5E7EB; }
    .sb-badge-low      { background: var(--sb-teal-tint);   color: #115E59; border-color: var(--sb-teal-border); }
    .sb-badge-medium    { background: var(--sb-amber-tint);  color: var(--sb-amber-text); border-color: var(--sb-amber-border); }
    .sb-badge-high      { background: var(--sb-red-tint);    color: #991B1B; border-color: var(--sb-red-border); }
    .sb-badge-accent    { background: var(--sb-green-tint);  color: var(--sb-green-dark); border-color: var(--sb-green-border); }

    .sb-content-original { background: #FFFFFF; border: 1px solid var(--sb-border); border-radius: 8px; padding: 1rem; margin-bottom: 0.75rem; }
    .sb-content-ai { background: var(--sb-purple-tint); border: 1px dashed var(--sb-purple-border); border-radius: 8px; padding: 1rem; margin-bottom: 0.75rem; }
    .sb-content-notes { background: var(--sb-blue-tint); border-left: 3px solid var(--sb-blue); padding: 0.85rem 1rem; margin-bottom: 0.75rem; border-radius: 0 8px 8px 0; }

    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        border-radius: 8px !important; border-color: var(--sb-border) !important; color: var(--sb-ink) !important; background: #FFFFFF !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus { border-color: var(--sb-blue) !important; box-shadow: 0 0 0 1px var(--sb-blue) !important; }
    </style>""", unsafe_allow_html=True)
