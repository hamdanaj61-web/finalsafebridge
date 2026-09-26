"""Vibrant, modern, and appealing design system for SafeBridge AI.
Features modern Google Fonts (Plus Jakarta Sans & Outfit), radiant gradients,
elevated cards with smooth micro-interactions, and vibrant color accents.
"""

def apply_styles():
    import streamlit as st
    st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Outfit:wght@500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

    /* ── Core Modern Canvas & Design Tokens ── */
    :root {
        --sb-bg: #F8FAFC;
        --sb-surface: #FFFFFF;
        --sb-surface-hover: #F1F5F9;
        --sb-border: #E2E8F0;
        --sb-border-subtle: #F1F5F9;
        --sb-ink: #0F172A;
        --sb-muted: #64748B;
        --sb-faint: #94A3B8;
        
        /* Vibrant Brand Tokens */
        --sb-primary: #4F46E5;
        --sb-primary-hover: #4338CA;
        --sb-primary-light: #EEF2FF;
        --sb-primary-border: #C7D2FE;
        --sb-primary-gradient: linear-gradient(135deg, #4F46E5 0%, #6366F1 50%, #7C3AED 100%);
        --sb-primary-gradient-subtle: linear-gradient(135deg, rgba(79, 70, 229, 0.07) 0%, rgba(124, 58, 237, 0.05) 100%);
        
        /* Emerald & Success Tokens */
        --sb-emerald: #10B981;
        --sb-emerald-dark: #065F46;
        --sb-emerald-light: #ECFDF5;
        --sb-emerald-border: #A7F3D0;
        --sb-emerald-gradient: linear-gradient(135deg, #10B981 0%, #059669 100%);
        
        /* Amber & Warning Tokens */
        --sb-amber: #F59E0B;
        --sb-amber-dark: #92400E;
        --sb-amber-light: #FEF3C7;
        --sb-amber-border: #FDE68A;
        
        /* Coral / Rose Urgency Tokens */
        --sb-rose: #F43F5E;
        --sb-rose-dark: #9F1239;
        --sb-rose-light: #FFE4E6;
        --sb-rose-border: #FECDD3;

        /* Radius & Shadow */
        --sb-radius-sm: 8px;
        --sb-radius-md: 12px;
        --sb-radius-lg: 16px;
        --sb-radius-xl: 20px;
        --sb-shadow-sm: 0 2px 4px rgba(15, 23, 42, 0.04);
        --sb-shadow-md: 0 4px 16px -2px rgba(15, 23, 42, 0.06), 0 2px 6px -1px rgba(15, 23, 42, 0.03);
        --sb-shadow-lg: 0 12px 28px -4px rgba(15, 23, 42, 0.08), 0 4px 12px -2px rgba(15, 23, 42, 0.04);
        --sb-shadow-glow: 0 8px 24px -2px rgba(79, 70, 229, 0.25);
    }

    /* ── Ambient Background & Clean Typography ── */
    .stApp {
        background-color: var(--sb-bg) !important;
        background-image: 
            radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.06) 0px, transparent 45%),
            radial-gradient(at 100% 0%, rgba(16, 185, 129, 0.05) 0px, transparent 40%),
            radial-gradient(at 100% 100%, rgba(124, 58, 237, 0.05) 0px, transparent 40%) !important;
        color: var(--sb-ink) !important;
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        -webkit-font-smoothing: antialiased;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 1.8rem;
        padding-bottom: 3.5rem;
    }

    /* Headings font */
    h1, h2, h3, h4, h5, h6, .sb-title {
        font-family: 'Outfit', 'Plus Jakarta Sans', sans-serif !important;
        color: var(--sb-ink) !important;
        letter-spacing: -0.015em;
    }

    .stApp p, .stApp label, .stApp li {
        color: var(--sb-ink);
    }

    /* ── Streamlit Built-in Icons & Material Symbols Protection ── */
    .material-symbols-rounded,
    .material-symbols-outlined,
    .material-icons,
    [data-testid*="stIcon"],
    [data-testid*="stIconMaterial"],
    [data-testid*="stExpandSidebarButton"] *,
    [data-testid*="stSidebarCollapseButton"] *,
    [data-testid="baseButton-headerNoPadding"] *,
    [data-testid="stTextInputRootElement"] button *,
    button[aria-label*="password" i] *,
    button[aria-label*="sidebar" i] *,
    span[class*="e1vmumty"] {
        font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
        font-weight: normal !important;
        font-style: normal !important;
        line-height: 1 !important;
        letter-spacing: normal !important;
        text-transform: none !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        white-space: nowrap !important;
        word-wrap: normal !important;
        direction: ltr !important;
        font-feature-settings: 'liga' 1 !important;
        -webkit-font-feature-settings: 'liga' 1 !important;
        -webkit-font-smoothing: antialiased !important;
    }

    /* ── Modern Sidebar ── */
    [data-testid="stSidebar"] {
        background: #FFFFFF !important;
        border-right: 1px solid var(--sb-border) !important;
        box-shadow: 2px 0 12px rgba(15, 23, 42, 0.02) !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: var(--sb-border) !important;
        margin: 1.25rem 0 !important;
    }
    [data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label {
        padding: 0.6rem 0.9rem !important;
        border-radius: var(--sb-radius-md) !important;
        transition: all 0.2s ease !important;
        margin-bottom: 0.25rem !important;
    }
    [data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label:hover {
        background: var(--sb-surface-hover) !important;
    }
    [data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label[data-checked="true"],
    [data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label:has(input:checked) {
        background: var(--sb-primary-light) !important;
        color: var(--sb-primary) !important;
        font-weight: 600 !important;
        border-left: 3px solid var(--sb-primary) !important;
    }

    /* ── Vibrant Page Header Banner ── */
    .sb-page-header {
        background: #FFFFFF;
        border: 1px solid var(--sb-border);
        border-radius: var(--sb-radius-lg);
        padding: 1.6rem 1.8rem;
        margin-bottom: 1.8rem;
        box-shadow: var(--sb-shadow-sm);
        position: relative;
        overflow: hidden;
    }
    .sb-page-header::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: var(--sb-primary-gradient);
    }
    .sb-page-header h1 {
        font-size: 1.85rem;
        font-weight: 800;
        margin: 0 0 0.35rem 0;
        color: var(--sb-ink) !important;
        letter-spacing: -0.025em;
    }
    .sb-page-header p {
        font-size: 0.98rem;
        color: var(--sb-muted) !important;
        margin: 0;
        line-height: 1.5;
    }
    .sb-pill-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.76rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        background: var(--sb-primary-light);
        color: var(--sb-primary);
        border: 1px solid var(--sb-primary-border);
        margin-bottom: 0.6rem;
    }

    /* ── Elevated Modern Cards ── */
    .card, .sb-card {
        background: #FFFFFF !important;
        border-radius: var(--sb-radius-lg) !important;
        border: 1px solid var(--sb-border) !important;
        box-shadow: var(--sb-shadow-md) !important;
        padding: 1.4rem 1.5rem !important;
        margin-bottom: 1.25rem !important;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
        position: relative;
        overflow: hidden;
    }
    .card:hover, .sb-card:hover {
        transform: translateY(-4px) !important;
        box-shadow: var(--sb-shadow-lg), 0 0 0 1px #818CF8 !important;
        border-color: #818CF8 !important;
    }
    .card h2, .card h3, .sb-card h3 {
        font-size: 1.15rem;
        font-weight: 700;
        margin: 0.6rem 0 0.35rem 0;
        color: var(--sb-ink) !important;
        letter-spacing: -0.01em;
    }
    .card p.muted, .sb-card p.muted {
        font-size: 0.88rem;
        color: var(--sb-muted) !important;
        margin: 0 0 0.6rem 0;
        line-height: 1.45;
    }
    .sb-icon-box {
        width: 44px;
        height: 44px;
        border-radius: var(--sb-radius-md);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: var(--sb-primary-light);
        color: var(--sb-primary);
        margin-bottom: 0.4rem;
        transition: all 0.2s ease;
    }
    .card:hover .sb-icon-box {
        background: var(--sb-primary);
        color: #FFFFFF;
        transform: scale(1.05);
    }

    /* ── Anonymous Highlight Card (Lush Emerald Glow) ── */
    .sb-card-highlight {
        background: linear-gradient(135deg, #ECFDF5 0%, #F0FDF4 100%) !important;
        border: 1.5px solid var(--sb-emerald-border) !important;
        border-radius: var(--sb-radius-lg) !important;
        padding: 1.4rem 1.5rem !important;
        margin-bottom: 1.25rem !important;
        box-shadow: 0 8px 24px -2px rgba(16, 185, 129, 0.15) !important;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
        position: relative;
    }
    .sb-card-highlight:hover {
        transform: translateY(-4px) !important;
        box-shadow: 0 16px 32px -4px rgba(16, 185, 129, 0.22) !important;
        border-color: #34D399 !important;
    }
    .sb-card-highlight h3 {
        color: var(--sb-emerald-dark) !important;
        font-size: 1.15rem;
        font-weight: 700;
        margin: 0.6rem 0 0.35rem 0;
    }
    .sb-card-highlight p {
        color: #047857 !important;
        font-size: 0.88rem;
        margin: 0 0 0.6rem 0;
        line-height: 1.45;
    }
    .sb-card-highlight .sb-icon-box {
        background: #D1FAE5;
        color: var(--sb-emerald);
    }
    .sb-card-highlight:hover .sb-icon-box {
        background: var(--sb-emerald);
        color: #FFFFFF;
    }

    /* ── Metric Cards: Vibrant Top Line & Elevated Look ── */
    [data-testid="stMetric"] {
        background: #FFFFFF !important;
        border: 1px solid var(--sb-border) !important;
        border-radius: var(--sb-radius-lg) !important;
        padding: 1.2rem 1.3rem !important;
        box-shadow: var(--sb-shadow-sm) !important;
        position: relative;
        overflow: hidden;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: var(--sb-shadow-md) !important;
    }
    [data-testid="stMetric"]::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--sb-primary-gradient);
    }
    [data-testid="stMetricLabel"] p {
        font-size: 0.84rem !important;
        font-weight: 600 !important;
        color: var(--sb-muted) !important;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    [data-testid="stMetricValue"] div {
        font-family: 'Outfit', sans-serif !important;
        font-size: 2rem !important;
        font-weight: 800 !important;
        color: var(--sb-ink) !important;
        letter-spacing: -0.02em;
    }

    /* ── Radiant Buttons ── */
    /* Primary buttons */
    button[kind="primary"], .stButton > button[kind="primary"] {
        background: var(--sb-primary-gradient) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: var(--sb-radius-md) !important;
        padding: 0.65rem 1.3rem !important;
        font-weight: 700 !important;
        font-size: 0.94rem !important;
        box-shadow: var(--sb-shadow-glow) !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
        letter-spacing: 0.01em;
    }
    button[kind="primary"]:hover, .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 28px -2px rgba(79, 70, 229, 0.45) !important;
        color: #FFFFFF !important;
    }
    button[kind="primary"]:active, .stButton > button[kind="primary"]:active {
        transform: translateY(0px) !important;
    }

    /* Secondary buttons */
    .stButton > button:not([kind="primary"]) {
        background: #FFFFFF !important;
        color: var(--sb-ink) !important;
        border: 1.5px solid var(--sb-border) !important;
        border-radius: var(--sb-radius-md) !important;
        padding: 0.65rem 1.2rem !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        box-shadow: var(--sb-shadow-sm) !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:not([kind="primary"]):hover {
        background: #F8FAFC !important;
        border-color: var(--sb-primary-border) !important;
        color: var(--sb-primary) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px -2px rgba(79, 70, 229, 0.12) !important;
    }

    /* ── Notice / Consent Block ── */
    .sb-notice-block {
        background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
        border: 1px solid var(--sb-border);
        border-left: 4px solid var(--sb-primary);
        border-radius: var(--sb-radius-md);
        padding: 1.2rem 1.4rem;
        margin: 1.25rem 0 1.5rem 0;
        box-shadow: var(--sb-shadow-sm);
    }
    .sb-notice-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: var(--sb-ink);
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .sb-notice-body {
        font-size: 0.88rem;
        color: var(--sb-muted);
        line-height: 1.6;
    }

    /* ── Standing Calm AI Disclaimer Note ── */
    .sb-ai-disclaimer {
        background: #F8FAFC;
        border-left: 3px solid #6366F1;
        padding: 0.75rem 1.1rem;
        margin: 1rem 0;
        font-size: 0.85rem;
        color: var(--sb-muted);
        border-radius: 0 var(--sb-radius-md) var(--sb-radius-md) 0;
        box-shadow: var(--sb-shadow-sm);
    }

    /* ── Vibrant Badges ── */
    .sb-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.8rem;
        font-weight: 700;
        padding: 0.3rem 0.7rem;
        border-radius: 9999px;
        border: 1px solid transparent;
        letter-spacing: 0.02em;
    }
    .sb-badge-neutral {
        background: #F1F5F9;
        color: #334155;
        border-color: #CBD5E1;
    }
    .sb-badge-accent {
        background: var(--sb-primary-light);
        color: var(--sb-primary);
        border-color: var(--sb-primary-border);
    }
    .sb-badge-success {
        background: var(--sb-emerald-light);
        color: var(--sb-emerald-dark);
        border-color: var(--sb-emerald-border);
    }
    .sb-badge-warning {
        background: var(--sb-amber-light);
        color: var(--sb-amber-dark);
        border-color: var(--sb-amber-border);
    }
    .sb-badge-danger {
        background: var(--sb-rose-light);
        color: var(--sb-rose-dark);
        border-color: var(--sb-rose-border);
    }

    /* ── Clean & Polished Inputs ── */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        border-radius: var(--sb-radius-md) !important;
        border: 1.5px solid var(--sb-border) !important;
        color: var(--sb-ink) !important;
        background: #FFFFFF !important;
        padding: 0.65rem 0.85rem !important;
        font-size: 0.94rem !important;
        transition: all 0.2s ease !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: var(--sb-primary) !important;
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15) !important;
    }

    /* ── Streamlit Tabs Styling ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: #FFFFFF;
        padding: 0.4rem 0.5rem;
        border-radius: var(--sb-radius-lg);
        border: 1px solid var(--sb-border);
        box-shadow: var(--sb-shadow-sm);
        margin-bottom: 1.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: auto;
        padding: 0.6rem 1.25rem;
        border-radius: var(--sb-radius-md);
        font-weight: 600;
        font-size: 0.95rem;
        color: var(--sb-muted);
        border: none !important;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background: var(--sb-primary-gradient) !important;
        color: #FFFFFF !important;
        box-shadow: var(--sb-shadow-glow) !important;
    }

    /* ── Step-by-Step Guided Reporting Styling ── */
    .sb-stepper-wrap {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: #FFFFFF;
        padding: 1rem 1.4rem;
        border-radius: var(--sb-radius-lg);
        border: 1px solid var(--sb-border);
        margin-bottom: 1.5rem;
        box-shadow: var(--sb-shadow-sm);
    }
    .sb-step-item {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        font-size: 0.86rem;
        font-weight: 600;
        color: var(--sb-muted);
    }
    .sb-step-item.active {
        color: var(--sb-primary);
        font-weight: 700;
    }
    .sb-step-item.completed {
        color: var(--sb-emerald);
    }
    .sb-step-circle {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #F1F5F9;
        color: var(--sb-muted);
        font-size: 0.82rem;
        font-weight: 700;
        transition: all 0.2s ease;
    }
    .sb-step-item.active .sb-step-circle {
        background: var(--sb-primary-gradient);
        color: #FFFFFF;
        box-shadow: 0 4px 10px rgba(79, 70, 229, 0.35);
    }
    .sb-step-item.completed .sb-step-circle {
        background: var(--sb-emerald);
        color: #FFFFFF;
    }

    /* Guided Choice Card / Button Container */
    .sb-choice-box {
        background: #FFFFFF;
        border: 2px solid var(--sb-border);
        border-radius: var(--sb-radius-lg);
        padding: 1.1rem 1.25rem;
        margin-bottom: 0.75rem;
        cursor: pointer;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
        display: flex;
        align-items: flex-start;
        gap: 0.9rem;
    }
    .sb-choice-box:hover {
        border-color: #818CF8;
        background: #F8FAFC;
        transform: translateY(-2px);
        box-shadow: 0 8px 20px -2px rgba(79, 70, 229, 0.12);
    }
    .sb-choice-box.selected {
        border-color: var(--sb-primary);
        background: var(--sb-primary-light);
        box-shadow: 0 0 0 1px var(--sb-primary), 0 8px 20px -2px rgba(79, 70, 229, 0.18);
    }

    /* Guided Review Card */
    .sb-review-card {
        background: #FFFFFF;
        border: 1px solid var(--sb-border);
        border-radius: var(--sb-radius-lg);
        padding: 1.5rem 1.6rem;
        margin-bottom: 1.5rem;
        box-shadow: var(--sb-shadow-md);
        position: relative;
        overflow: hidden;
    }
    .sb-review-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 5px;
        bottom: 0;
        background: var(--sb-primary-gradient);
    }
    .sb-review-item {
        display: flex;
        align-items: flex-start;
        gap: 0.8rem;
        padding: 0.65rem 0;
        border-bottom: 1px dashed var(--sb-border);
    }
    .sb-review-item:last-child {
        border-bottom: none;
    }
    .sb-review-label {
        width: 140px;
        font-size: 0.84rem;
        font-weight: 700;
        color: var(--sb-muted);
        text-transform: uppercase;
        letter-spacing: 0.04em;
        flex-shrink: 0;
    }
    .sb-review-val {
        font-size: 0.95rem;
        font-weight: 600;
        color: var(--sb-ink);
        flex-grow: 1;
    }
    </style>""", unsafe_allow_html=True)
