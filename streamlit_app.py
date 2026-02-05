import streamlit as st
import pandas as pd
import json
import base64
import binascii

# Título da aplicação
st.title("Dev Backend Utilities")

# Seção para conversão de CSV para JSON
st.header("📋 CSV para JSON")

# Upload do arquivo CSV
uploaded_csv = st.file_uploader("Escolha um arquivo CSV", type="csv")

if uploaded_csv is not None:
    # Ler o arquivo CSV
    df_csv = pd.read_csv(uploaded_csv)

    # Converter para JSON
    json_data = df_csv.to_json(orient='records')

    # Salvar o JSON em um arquivo
    json_filename = 'output.json'
    with open(json_filename, 'w') as json_file:
        json.dump(json.loads(json_data), json_file, indent=4)

    # Oferecer o download do arquivo JSON
    with open(json_filename, 'rb') as json_file:
        st.download_button(
            label="Baixar arquivo JSON",
            data=json_file,
            file_name=json_filename,
            mime='application/json'
        )

# Seção para conversão de JSON para CSV
st.header("📄 JSON para CSV")

# Upload do arquivo JSON
uploaded_json = st.file_uploader("Escolha um arquivo JSON", type="json")

if uploaded_json is not None:
    # Ler o arquivo JSON
    json_data = json.load(uploaded_json)

    # Converter para DataFrame
    df_json = pd.DataFrame(json_data)

    # Salvar o CSV em um arquivo
    csv_filename = 'output.csv'
    df_json.to_csv(csv_filename, index=False)

    # Oferecer o download do arquivo CSV
    with open(csv_filename, 'rb') as csv_file:
        st.download_button(
            label="Baixar arquivo CSV",
            data=csv_file,
            file_name=csv_filename,
            mime='text/csv'
        )

# Seção para converter Secret (HEX) para MFA (Base32)
st.header("🔐 Secret para MFA")

hex_secret = st.text_input("Cole o Secret em HEX", placeholder="ex: f47e25ddef361713f7a1d21d8e2e6aea25b80e68")

if hex_secret:
    try:
        # HEX -> bytes
        raw = binascii.unhexlify(hex_secret)
        
        # bytes -> Base32
        base32_secret = base64.b32encode(raw).decode("utf-8").replace("=", "")
        
        st.success("✓ Conversão realizada com sucesso!")
        st.code(base32_secret, language="text")
        
        # Botão para copiar
        st.write("Base32 Secret (pronto para usar no MFA):")
        st.text_input("Copie o valor abaixo:", value=base32_secret, disabled=True)
    except binascii.Error:
        st.error("❌ Erro: Secret inválido. Certifique-se de que é um HEX válido.")

# Seção para formatar JSON
st.header("🎯 Formatar JSON")

json_input = st.text_area("Cole o JSON em uma linha", placeholder='{"campo": "valor"}', height=150)

if json_input:
    try:
        # Parse the JSON string
        data = json.loads(json_input)
        
        # Format the JSON
        formatted_json = json.dumps(data, indent=4, ensure_ascii=False)
        
        st.success("✓ JSON formatado com sucesso!")
        st.code(formatted_json, language="json")
        
        # Botão para copiar
        st.text_area("Copie o JSON formatado abaixo:", value=formatted_json, disabled=True, height=200)
    except json.JSONDecodeError:
        st.error("❌ Erro: JSON inválido. Verifique o formato.")
