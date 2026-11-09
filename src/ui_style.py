import streamlit as st


def apply_style():
    st.html("""
    <style>
      .stMainBlockContainer { max-width: 52rem; padding-top: 3rem; }
      .policy-identity {
        font-family: system-ui, sans-serif;
        letter-spacing: -.025em;
        font-size: clamp(1.5rem, 4vw, 2rem);
        line-height: 1.15;
        margin: 0;
      }
      .policy-meta {
        overflow-wrap: anywhere;
        font-size: .85rem;
        font-variant-numeric: tabular-nums;
      }
      .policy-meter {
        height: .2rem;
        background: var(--secondary-background-color);
        border-radius: .15rem;
        overflow: hidden;
        margin: .3rem 0 .7rem;
      }
      .policy-meter span {
        height: 100%;
        display: block;
        background: var(--primary-color, #1d5fbf);
      }
      @media (max-width: 600px) {
        .stMainBlockContainer { padding: 2.4rem 1rem 2rem; }
        .stButton button, .stFormSubmitButton button { min-height: 44px; }
      }
    </style>
    """)
