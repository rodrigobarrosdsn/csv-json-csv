import streamlit as st
import uuid


st.set_page_config(page_title="Dev Utils - GUID/UUID", page_icon="🆔", layout="wide")
st.title("🆔 GUID / UUID Generator")
st.divider()

col_gen, col_info = st.columns([2, 1])

with col_gen:
    st.subheader("Gerador")

    num_guids = st.number_input(
        "Quantos GUIDs deseja gerar? (1-1000)",
        min_value=1,
        max_value=1000,
        value=1,
    )

    guid_version = st.radio(
        "Versão do UUID:",
        options=["UUID4 (Aleatório)", "UUID1 (Baseado em MAC)"],
        horizontal=True,
        key="guid_version",
    )

    use_uppercase = st.checkbox("Maiúsculas", value=False, key="guid_upper")
    use_hyphens = st.checkbox("Com hífens", value=True, key="guid_hyphens")

    if st.button("🔄 Gerar GUIDs", type="primary", key="generate_guids"):
        guids = []
        for _ in range(num_guids):
            g = uuid.uuid4() if "UUID4" in guid_version else uuid.uuid1()
            text = str(g)
            if not use_hyphens:
                text = text.replace("-", "")
            if use_uppercase:
                text = text.upper()
            guids.append(text)

        st.success(f"✓ {num_guids} GUID(s) gerado(s)!")

        guids_text = "\n".join(guids)
        st.code(guids_text, language="text")

        st.download_button(
            label="⬇️ Baixar GUIDs (.txt)",
            data=guids_text,
            file_name="guids.txt",
            mime="text/plain",
        )

with col_info:
    st.subheader("Referência")
    st.info(
        """
        **UUID4 (Aleatório)**
        - Completamente aleatório
        - Mais seguro
        - Melhor para chaves únicas

        **UUID1 (MAC + timestamp)**
        - Inclui endereço MAC e timestamp
        - Mais previsível
        - Bom para tracking sequencial

        **RFC 4122** — padrão universal
        """
    )

    st.divider()

    st.subheader("Validar UUID")
    uuid_to_validate = st.text_input(
        "Cole um UUID para validar",
        placeholder="e2a1c56d-3de0-43e8-bbde-f666172b879f",
    )
    if uuid_to_validate:
        try:
            parsed = uuid.UUID(uuid_to_validate)
            st.success(f"✓ UUID válido (versão {parsed.version})")
            st.json(
                {
                    "hex": parsed.hex,
                    "versão": parsed.version,
                    "variante": str(parsed.variant),
                }
            )
        except ValueError:
            st.error("❌ UUID inválido.")
