import streamlit as st
import pandas as pd
import json
import io


st.set_page_config(page_title="Dev Utils - CSV ↔ JSON", page_icon="📋", layout="wide")
st.title("📋 CSV ↔ JSON")
st.divider()

col1, col2 = st.columns(2)

# ── CSV → JSON ──────────────────────────────────────────────
with col1:
    st.subheader("CSV → JSON")

    uploaded_csv = st.file_uploader(
        "Escolha um arquivo CSV", type="csv", key="csv_uploader"
    )

    if uploaded_csv is not None:
        df_csv = pd.read_csv(uploaded_csv)

        st.dataframe(df_csv.head(10), use_container_width=True)
        st.caption(f"{len(df_csv)} linhas × {len(df_csv.columns)} colunas")

        json_data = df_csv.to_json(orient="records", force_ascii=False)
        formatted = json.dumps(json.loads(json_data), indent=4, ensure_ascii=False)

        st.download_button(
            label="⬇️ Baixar arquivo JSON",
            data=formatted,
            file_name="output.json",
            mime="application/json",
        )

# ── JSON → CSV ──────────────────────────────────────────────
with col2:
    st.subheader("JSON → CSV")

    uploaded_json = st.file_uploader(
        "Escolha um arquivo JSON", type="json", key="json_uploader"
    )

    if uploaded_json is not None:
        json_content = json.load(uploaded_json)
        df_json = pd.DataFrame(json_content)

        st.dataframe(df_json.head(10), use_container_width=True)
        st.caption(f"{len(df_json)} linhas × {len(df_json.columns)} colunas")

        csv_buffer = io.StringIO()
        df_json.to_csv(csv_buffer, index=False)

        st.download_button(
            label="⬇️ Baixar arquivo CSV",
            data=csv_buffer.getvalue(),
            file_name="output.csv",
            mime="text/csv",
        )
