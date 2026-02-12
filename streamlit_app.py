import streamlit as st

st.set_page_config(
    page_title="Dev Backend Utilities",
    page_icon="🛠️",
    layout="wide",
)

st.title("🛠️ Dev Backend Utilities")
st.divider()

st.markdown(
    """
    Bem-vindo ao **Dev Backend Utilities** — um conjunto de ferramentas
    para facilitar o dia a dia do desenvolvedor backend.

    Selecione uma ferramenta no menu lateral para começar.
    """
)

# Cards com as ferramentas disponíveis
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        ### 📋 CSV ↔ JSON
        Converta arquivos **CSV para JSON** e vice-versa de forma rápida,
        com preview dos dados e download direto.
        """
    )
    st.page_link("pages/1_📋_CSV_JSON.py", label="Abrir CSV ↔ JSON", icon="📋")

    st.markdown("---")

    st.markdown(
        """
        ### 🎯 JSON Formatter & Validator
        Formata, valida e visualiza JSON com **tree view**, estatísticas,
        auto-fix e configurações de indentação. Inspirado no curiousconcept.
        """
    )
    st.page_link("pages/3_🎯_Formatar_JSON.py", label="Abrir JSON Formatter", icon="🎯")

with col2:
    st.markdown(
        """
        ### 🔐 Secret para MFA
        Converta secrets em **HEX, Base64 ou texto** para Base32.
        Suporte a múltiplos formatos, detalhes do secret e preview TOTP.
        """
    )
    st.page_link("pages/2_🔐_Secret_MFA.py", label="Abrir Secret MFA", icon="🔐")

    st.markdown("---")

    st.markdown(
        """
        ### 🆔 GUID / UUID Generator
        Gere **UUIDs v1 ou v4** em lote (até 1000), com opções de
        formato. Inclui validador de UUID.
        """
    )
    st.page_link("pages/4_🆔_GUID_UUID.py", label="Abrir GUID/UUID", icon="🆔")

st.divider()
st.caption("Dev Backend Utilities • Feito com Streamlit")

