"""Flat, bright, light design system for SafeBridge AI.
Zero dark themes, zero drop shadows, restrained green accent (#639922).
"""

def apply_styles():
    import streamlit as st
    st.markdown("""<style>
    /* ── Core Light Canvas & Typography ── */
    :root {
        --sb-bg: #FFFFFF;
        --sb-surface: #F9FAFB;
        --sb-surface-hover: #F3F4F6;
        --sb-border: #E5E7EB;
        --sb-border-subtle: #F3F4F6;
        --sb-ink: #111827;
        --sb-muted: #6B7280;
        --sb-faint: #9CA3AF;
        
        /* Green Accent Tokens */
        --sb-green: #639922;
        --sb-green-hover: #55831C;
        --sb-green-tint: #EAF3DE;
        --sb-green-border: #97C459;
        --sb-green-text: #27500A;
        --sb-green-dark: #173404;
    }

    .stApp {
        background: #FFFFFF !important;
        color: var(--sb-ink) !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
    }

    .block-container {
        max-width: 1140px;
        padding-top: 1.8rem;
        padding-bottom: 3rem;
    }

    /* Override any residual dark text colors */
    .stApp p, .stApp label, .stApp li, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp span {
        color: var(--sb-ink);
    }

    /* ── Sidebar: Flat Light Neutral ── */
    [data-testid="stSidebar"] {
        background: #F9FAFB !important;
        border-right: 1px solid var(--sb-border) !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: var(--sb-border) !important;
    }

    /* ── Header Area: Calm, White, No Colored Gradient Banner ── */
    .sb-page-header {
        background: #FFFFFF;
        border-bottom: 1px solid var(--sb-border);
        padding: 1.5rem 0 1.2rem 0;
        margin-bottom: 1.5rem;
    }
    .sb-page-header h1 {
        font-size: 1.85rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin: 0 0 0.35rem 0;
        color: var(--sb-ink) !important;
    }
    .sb-page-header p {
        font-size: 0.95rem;
        color: var(--sb-muted) !important;
        margin: 0;
        line-height: 1.45;
    }

    /* ── Flat Cards: Hairline Border, 12px Radius, No Shadows, No Lift ── */
    .card, .sb-card {
        background: #FFFFFF !important;
        color: var(--sb-ink) !important;
        padding: 1.25rem 1.4rem;
        border-radius: 12px !important;
        border: 1px solid var(--sb-border) !important;
        box-shadow: none !important;
        transition: border-color 0.15s ease !important;
        transform: none !important;
        margin-bottom: 1rem;
    }
    .card:hover, .sb-card:hover {
        border-color: #D1D5DB !important;
        transform: none !important;
        box-shadow: none !important;
    }
    .card h2, .card h3, .sb-card h3 {
        font-size: 1.05rem;
        font-weight: 600;
        margin: 0.5rem 0 0.25rem 0;
        color: var(--sb-ink) !important;
    }
    .card p.muted, .sb-card p.muted {
        font-size: 0.85rem;
        color: var(--sb-muted) !important;
        margin: 0 0 0.5rem 0;
        line-height: 1.4;
    }

    /* ── Anonymous Reporting Highlight Card (Only Primary Card on Screen) ── */
    .sb-card-highlight {
        background: var(--sb-green-tint) !important;
        border: 1px solid var(--sb-green-border) !important;
        border-radius: 12px !important;
        padding: 1.25rem 1.4rem;
        margin-bottom: 1rem;
        box-shadow: none !important;
        transform: none !important;
    }
    .sb-card-highlight h3 {
        color: var(--sb-green-dark) !important;
        font-size: 1.05rem;
        font-weight: 600;
        margin: 0.5rem 0 0.25rem 0;
    }
    .sb-card-highlight p {
        color: var(--sb-green-text) !important;
        font-size: 0.85rem;
        margin: 0 0 0.5rem 0;
    }

    /* ── Metric Cards: Flat Hairline Border ── */
    [data-testid="stMetric"] {
        background: #FFFFFF !important;
        border: 1px solid var(--sb-border) !important;
        border-radius: 12px !important;
        padding: 0.9rem 1.1rem !important;
        box-shadow: none !important;
    }
    [data-testid="stMetricLabel"] p {
        font-size: 0.82rem !important;
        font-weight: 500 !important;
        color: var(--sb-muted) !important;
        text-transform: capitalize;
    }
    [data-testid="stMetricValue"] div {
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        color: var(--sb-ink) !important;
    }

    /* ── Buttons: Restraint (Primary = Green Accent Fill; Secondary = Neutral Outline) ── */
    /* Primary buttons (e.g. Sign in, Send report) */
    button[kind="primary"], .stButton > button[kind="primary"] {
        background: var(--sb-green) !important;
        color: #FFFFFF !important;
        border: 1px solid var(--sb-green) !important;
        border-radius: 8px !important;
        padding: 0.55rem 1rem !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        box-shadow: none !important;
        transition: background 0.15s ease !important;
    }
    button[kind="primary"]:hover, .stButton > button[kind="primary"]:hover {
        background: var(--sb-green-hover) !important;
        border-color: var(--sb-green-hover) !important;
        color: #FFFFFF !important;
        transform: none !important;
        filter: none !important;
    }

    /* Secondary / Default buttons (All other buttons stay neutral outline) */
    .stButton > button:not([kind="primary"]) {
        background: #FFFFFF !important;
        color: var(--sb-ink) !important;
        border: 1px solid var(--sb-border) !important;
        border-radius: 8px !important;
        padding: 0.55rem 1rem !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        box-shadow: none !important;
        transition: background 0.15s ease, border-color 0.15s ease !important;
        transform: none !important;
    }
    .stButton > button:not([kind="primary"]):hover {
        background: var(--sb-surface) !important;
        border-color: #D1D5DB !important;
        color: var(--sb-ink) !important;
        transform: none !important;
        filter: none !important;
    }

    /* ── Notice / Consent Block: Clear Visual Separation ── */
    .sb-notice-block {
        background: #F9FAFB;
        border: 1px solid var(--sb-border);
        border-radius: 10px;
        padding: 1.1rem 1.3rem;
        margin: 1rem 0 1.25rem 0;
    }
    .sb-notice-title {
        font-size: 0.9rem;
        font-weight: 600;
        color: var(--sb-ink);
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.45rem;
    }
    .sb-notice-body {
        font-size: 0.83rem;
        color: var(--sb-muted);
        line-height: 1.5;
    }

    /* ── Standing Calm AI Disclaimer Note (Not an alarming red box) ── */
    .sb-ai-disclaimer {
        background: #F9FAFB;
        border-left: 3px solid #9CA3AF;
        padding: 0.6rem 0.9rem;
        margin: 0.75rem 0;
        font-size: 0.82rem;
        color: var(--sb-muted);
        border-radius: 0 6px 6px 0;
    }

    /* ── Clean Badges (Text + Shape, No Color Alone) ── */
    .sb-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        font-size: 0.78rem;
        font-weight: 500;
        padding: 0.2rem 0.55rem;
        border-radius: 6px;
        border: 1px solid transparent;
    }
    .sb-badge-neutral {
        background: #F3F4F6;
        color: #374151;
        border-color: #E5E7EB;
    }
    .sb-badge-accent {
        background: var(--sb-green-tint);
        color: var(--sb-green-dark);
        border-color: var(--sb-green-border);
    }
    .sb-badge-warning {
        background: #FEF3C7;
        color: #92400E;
        border-color: #FDE68A;
    }
    .sb-badge-danger {
        background: #FEE2E2;
        color: #991B1B;
        border-color: #FECACA;
    }

    /* ── Distinct Counselor Content Blocks ── */
    .sb-content-original {
        background: #FFFFFF;
        border: 1px solid var(--sb-border);
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.75rem;
    }
    .sb-content-ai {
        background: #F9FAFB;
        border: 1px dashed #CBD5E1;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.75rem;
    }
    .sb-content-notes {
        background: #F8FAFC;
        border-left: 3px solid #64748B;
        padding: 0.85rem 1rem;
        margin-bottom: 0.75rem;
        border-radius: 0 8px 8px 0;
    }

    /* ── Clean Input Elements ── */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        border-radius: 8px !important;
        border-color: var(--sb-border) !important;
        color: var(--sb-ink) !important;
        background: #FFFFFF !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: var(--sb-green) !important;
        box-shadow: 0 0 0 1px var(--sb-green) !important;
    }
    </style>""", unsafe_allow_html=True)
