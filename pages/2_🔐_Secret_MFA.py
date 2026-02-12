import streamlit as st
import base64
import binascii
import hashlib
import hmac
import struct
import time


st.set_page_config(page_title="Dev Utils - Secret MFA", page_icon="🔐", layout="wide")
st.title("🔐 Secret para MFA")
st.divider()

# ── Layout principal ────────────────────────────────────────
col_input, col_output = st.columns([1, 1], gap="large")

with col_input:
    st.subheader("Entrada")

    input_format = st.radio(
        "Formato do Secret:",
        options=["HEX", "Base64", "Texto plano (UTF-8)"],
        horizontal=True,
        key="mfa_input_format",
    )

    secret_input = st.text_area(
        "Cole o Secret aqui",
        placeholder={
            "HEX": "f47e25ddef361713f7a1d21d8e2e6aea25b80e68",
            "Base64": "9H4l3e82FxP3odIdji5q6iW4Dmg=",
            "Texto plano (UTF-8)": "minha-chave-secreta",
        }[input_format],
        height=120,
        key="mfa_secret_input",
    )

    st.caption("Espaços, hífens e quebras de linha são removidos automaticamente.")

    col_btn, col_clear = st.columns([1, 1])
    with col_btn:
        convert_btn = st.button("🔄 Converter", type="primary", use_container_width=True)
    with col_clear:
        if st.button("🗑️ Limpar", use_container_width=True):
            st.rerun()

with col_output:
    st.subheader("Resultado")

    if convert_btn and secret_input:
        cleaned = secret_input.strip().replace(" ", "").replace("-", "").replace("\n", "")

        try:
            # Converter para bytes conforme formato selecionado
            if input_format == "HEX":
                raw = binascii.unhexlify(cleaned)
            elif input_format == "Base64":
                raw = base64.b64decode(cleaned)
            else:
                raw = cleaned.encode("utf-8")

            # Gerar todos os formatos de saída
            base32_secret = base64.b32encode(raw).decode("utf-8")
            base32_no_pad = base32_secret.replace("=", "")
            hex_output = binascii.hexlify(raw).decode("utf-8")
            b64_output = base64.b64encode(raw).decode("utf-8")

            st.success("✓ Conversão realizada com sucesso!")

            # Base32 — o principal
            st.markdown("**Base32** (para apps MFA)")
            st.code(base32_no_pad, language="text")

            # Outros formatos em expander
            with st.expander("📋 Todos os formatos", expanded=True):
                formats = {
                    "Base32 (com padding)": base32_secret,
                    "Base32 (sem padding)": base32_no_pad,
                    "HEX": hex_output,
                    "Base64": b64_output,
                }
                for label, value in formats.items():
                    st.text_input(label, value=value, disabled=True, key=f"fmt_{label}")

            # Info do secret
            with st.expander("📊 Detalhes do Secret"):
                st.json({
                    "tamanho_bytes": len(raw),
                    "tamanho_bits": len(raw) * 8,
                    "sha1_hash": hashlib.sha1(raw).hexdigest(),
                    "algoritmo_recomendado": "TOTP (RFC 6238)",
                    "segurança": "✓ Forte (≥ 160 bits)" if len(raw) >= 20 else "⚠️ Fraco (< 160 bits)",
                })

            # Gerar código TOTP atual
            with st.expander("⏱️ Código TOTP atual (preview)"):
                try:
                    # TOTP simplificado (RFC 6238)
                    time_step = 30
                    t = int(time.time()) // time_step
                    t_bytes = struct.pack(">Q", t)
                    h = hmac.new(raw, t_bytes, hashlib.sha1).digest()
                    offset = h[-1] & 0x0F
                    code = struct.unpack(">I", h[offset:offset + 4])[0]
                    code = (code & 0x7FFFFFFF) % 1000000

                    remaining = time_step - (int(time.time()) % time_step)

                    st.metric(
                        label="Código TOTP",
                        value=f"{code:06d}",
                        delta=f"expira em {remaining}s",
                    )
                    st.caption("⚠️ Este é um preview. Use seu app MFA para códigos reais.")
                except Exception:
                    st.warning("Não foi possível gerar o TOTP para este secret.")

        except (binascii.Error, ValueError) as e:
            st.error(f"❌ Secret inválido para o formato {input_format}.")
            st.caption(f"Detalhe: {e}")

    elif convert_btn and not secret_input:
        st.warning("Cole um secret no campo de entrada.")
    else:
        st.info("Cole seu secret e clique em **Converter** para ver o resultado.")

st.divider()

# ── Guia de uso ─────────────────────────────────────────────
with st.expander("📖 Como usar", expanded=False):
    st.markdown(
        """
        ### Passo a passo

        1. **Selecione o formato** do secret que você possui (HEX, Base64 ou texto)
        2. **Cole o secret** no campo de entrada
        3. Clique em **Converter**
        4. Copie o valor **Base32** gerado
        5. No seu app de MFA (Google Authenticator, Authy, Microsoft Authenticator):
           - Escolha **Inserir chave manualmente**
           - Cole o valor Base32
           - Pronto! O código TOTP será gerado automaticamente

        ### Formatos comuns

        | Formato | Exemplo | Onde encontrar |
        |---------|---------|---------------|
        | HEX | `f47e25ddef36...` | Banco de dados, APIs |
        | Base64 | `9H4l3e82Fx...` | Configurações, tokens |
        | Base32 | `6R7CL...` | Apps de MFA |
        | Texto | `minha-chave` | Configurações simples |
        """
    )
