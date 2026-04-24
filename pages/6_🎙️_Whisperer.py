import streamlit as st
import os
import subprocess
import tempfile

st.set_page_config(page_title="Dev Utils - Whisperer", page_icon="🎙️", layout="wide")
st.title("🎙️ Whisperer — Transcrição de Áudios")
st.divider()

# Verificar se whisper está instalado
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

if not WHISPER_AVAILABLE:
    st.error(
        "**Whisper não está instalado.** Execute o comando abaixo no terminal e reinicie o app:\n\n"
        "```bash\npip install openai-whisper ffmpeg-python\n```"
    )
    st.stop()

# Sidebar: configurações
with st.sidebar:
    st.subheader("⚙️ Configurações")
    model_size = st.selectbox(
        "Modelo Whisper",
        options=["tiny", "base", "small", "medium", "large"],
        index=0,
        help="Modelos maiores são mais precisos, mas mais lentos.",
    )
    st.caption(
        "**tiny** — mais rápido, menos preciso\n\n"
        "**base** — equilíbrio ideal\n\n"
        "**small/medium/large** — mais preciso, mais lento"
    )

# Upload de arquivos
uploaded_files = st.file_uploader(
    "Faça upload dos arquivos de áudio",
    type=["wav", "mp3", "ogg", "m4a", "flac", "webm"],
    accept_multiple_files=True,
)

if not uploaded_files:
    st.info("Faça upload de um ou mais arquivos de áudio para começar.")
    st.stop()

# Botão para iniciar transcrição
if st.button("🎙️ Transcrever", type="primary", use_container_width=True):
    with st.spinner(f"Carregando modelo Whisper **{model_size}**..."):
        model = whisper.load_model(model_size)

    transcriptions = {}

    for uploaded_file in uploaded_files:
        file_name = uploaded_file.name
        base_name, ext = os.path.splitext(file_name)

        # Salvar o arquivo em disco temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_in:
            tmp_in.write(uploaded_file.read())
            tmp_in_path = tmp_in.name

        audio_path = tmp_in_path

        # Converter OGG/WebM para WAV via ffmpeg se necessário
        if ext.lower() in (".ogg", ".webm"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_wav:
                tmp_wav_path = tmp_wav.name
            command = ["ffmpeg", "-i", tmp_in_path, tmp_wav_path, "-y"]
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode != 0:
                st.warning(f"⚠️ Falha ao converter **{file_name}** para WAV. Tentando transcrever diretamente.")
            else:
                audio_path = tmp_wav_path

        # Transcrever
        with st.spinner(f"Transcrevendo **{file_name}**..."):
            try:
                result = model.transcribe(audio_path)
                transcriptions[file_name] = result["text"]
            except Exception as e:
                transcriptions[file_name] = f"[Erro na transcrição: {e}]"

        # Limpar arquivos temporários
        try:
            os.remove(tmp_in_path)
            if audio_path != tmp_in_path:
                os.remove(audio_path)
        except OSError:
            pass

    # Exibir resultados
    st.success(f"✅ {len(transcriptions)} arquivo(s) transcritos!")
    st.divider()

    all_text = ""
    for file_name, text in transcriptions.items():
        st.subheader(f"📄 {file_name}")
        st.text_area(
            label="Transcrição",
            value=text,
            height=150,
            key=f"transcription_{file_name}",
        )
        all_text += f"Transcrição de {file_name}:\n{text}\n\n"

    # Download das transcrições
    st.divider()
    st.download_button(
        label="⬇️ Baixar todas as transcrições (.txt)",
        data=all_text.encode("utf-8"),
        file_name="transcricoes.txt",
        mime="text/plain",
        use_container_width=True,
    )
