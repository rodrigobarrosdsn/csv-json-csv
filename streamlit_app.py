import streamlit as st
import pandas as pd
import json

# Título da aplicação
st.title("Conversor CSV <-> JSON")

# Seção para conversão de CSV para JSON
st.header("Converter CSV para JSON")

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
st.header("Converter JSON para CSV")

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
