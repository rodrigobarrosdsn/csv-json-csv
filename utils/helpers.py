import streamlit as st


def setup_page(title: str, icon: str):
    """Configura o layout padrão de cada página."""
    st.set_page_config(
        page_title=f"Dev Utils - {title}",
        page_icon=icon,
        layout="wide",
    )
    st.title(f"{icon} {title}")
    st.divider()
