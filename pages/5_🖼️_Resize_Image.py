import streamlit as st
from PIL import Image
import io


st.set_page_config(page_title="Dev Utils - Resize Image", page_icon="🖼️", layout="wide")
st.title("🖼️ Resize Image PNG")
st.divider()

uploaded_file = st.file_uploader(
    "Faça upload da imagem",
    type=["png", "jpg", "jpeg", "webp"],
    key="resize_uploader",
)

if uploaded_file is not None:
    img = Image.open(uploaded_file)

    col_config, col_preview = st.columns([1, 2], gap="large")

    with col_config:
        st.subheader("Configurações")

        st.markdown(f"**Original:** {img.width} × {img.height} px")
        st.markdown(f"**Formato:** {img.format or uploaded_file.type}")
        st.markdown(f"**Tamanho:** {uploaded_file.size / 1024:.1f} KB")

        st.divider()

        mode = st.radio(
            "Modo de redimensionamento:",
            ["Porcentagem", "Dimensões em pixels"],
            horizontal=True,
            key="resize_mode",
        )

        if mode == "Porcentagem":
            scale = st.slider(
                "Reduzir para (%):",
                min_value=1,
                max_value=200,
                value=40,
                step=1,
                key="resize_scale",
            )
            new_w = max(1, int(img.width * scale / 100))
            new_h = max(1, int(img.height * scale / 100))
        else:
            new_w = st.number_input(
                "Largura (px):", min_value=1, max_value=10000, value=img.width, key="resize_w"
            )
            new_h = st.number_input(
                "Altura (px):", min_value=1, max_value=10000, value=img.height, key="resize_h"
            )

        keep_aspect = st.checkbox("Manter proporção", value=True, key="resize_aspect")

        if keep_aspect and mode == "Dimensões em pixels":
            ratio = img.width / img.height
            new_h = max(1, int(new_w / ratio))
            st.caption(f"Altura ajustada: {new_h} px")

        st.markdown(f"**Nova dimensão:** {new_w} × {new_h} px")

        output_format = st.selectbox(
            "Formato de saída:",
            ["PNG", "JPEG", "WEBP"],
            key="resize_format",
        )

        if output_format == "JPEG":
            quality = st.slider("Qualidade JPEG:", 10, 100, 85, key="resize_quality")

        resize_btn = st.button("🔄 Redimensionar", type="primary", use_container_width=True)

    with col_preview:
        tab_orig, tab_result = st.tabs(["📷 Original", "✅ Resultado"])

        with tab_orig:
            st.image(img, caption=f"Original — {img.width}×{img.height}", use_container_width=True)

        with tab_result:
            if resize_btn:
                resized = img.resize((new_w, new_h), Image.LANCZOS)

                buf = io.BytesIO()
                save_kwargs = {}
                fmt = output_format.upper()
                ext = output_format.lower()

                if fmt == "JPEG":
                    if resized.mode == "RGBA":
                        resized = resized.convert("RGB")
                    save_kwargs["quality"] = quality
                    ext = "jpg"

                resized.save(buf, format=fmt, **save_kwargs)
                buf.seek(0)
                result_size = buf.getbuffer().nbytes

                st.image(resized, caption=f"Redimensionada — {new_w}×{new_h}", use_container_width=True)

                col_m1, col_m2, col_m3 = st.columns(3)
                col_m1.metric("Dimensão", f"{new_w}×{new_h}")
                col_m2.metric("Tamanho", f"{result_size / 1024:.1f} KB")
                reduction = (1 - result_size / uploaded_file.size) * 100
                col_m3.metric("Redução", f"{reduction:.1f}%")

                original_name = uploaded_file.name.rsplit(".", 1)[0]
                st.download_button(
                    label=f"⬇️ Baixar imagem .{ext}",
                    data=buf.getvalue(),
                    file_name=f"{original_name}_resized.{ext}",
                    mime=f"image/{ext}",
                    use_container_width=True,
                )
            else:
                st.info("Ajuste as configurações e clique em **Redimensionar**.")
else:
    st.info("Faça upload de uma imagem para começar.")
