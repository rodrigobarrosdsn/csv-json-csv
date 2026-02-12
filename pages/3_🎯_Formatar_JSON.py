import streamlit as st
import json
import re
import sys
from collections import OrderedDict


st.set_page_config(
    page_title="Dev Utils - JSON Formatter & Validator",
    page_icon="🎯",
    layout="wide",
)
st.title("🎯 JSON Formatter & Validator")
st.caption("Inspirado no jsonformatter.curiousconcept.com")
st.divider()


# ── Funções auxiliares ──────────────────────────────────────
def get_json_stats(data, raw_text: str) -> dict:
    """Coleta estatísticas do JSON."""

    def count_nodes(obj):
        if isinstance(obj, dict):
            return 1 + sum(count_nodes(v) for v in obj.values())
        elif isinstance(obj, list):
            return 1 + sum(count_nodes(v) for v in obj)
        return 1

    def max_depth(obj, level=0):
        if isinstance(obj, dict):
            if not obj:
                return level
            return max(max_depth(v, level + 1) for v in obj.values())
        elif isinstance(obj, list):
            if not obj:
                return level
            return max(max_depth(v, level + 1) for v in obj)
        return level

    def count_keys(obj):
        keys = set()
        if isinstance(obj, dict):
            keys.update(obj.keys())
            for v in obj.values():
                keys.update(count_keys(v))
        elif isinstance(obj, list):
            for v in obj:
                keys.update(count_keys(v))
        return keys

    def count_arrays(obj):
        c = 0
        if isinstance(obj, list):
            c = 1
            for v in obj:
                c += count_arrays(v)
        elif isinstance(obj, dict):
            for v in obj.values():
                c += count_arrays(v)
        return c

    def count_objects(obj):
        c = 0
        if isinstance(obj, dict):
            c = 1
            for v in obj.values():
                c += count_objects(v)
        elif isinstance(obj, list):
            for v in obj:
                c += count_objects(v)
        return c

    all_keys = count_keys(data)
    return {
        "Tamanho original": f"{len(raw_text.encode('utf-8')):,} bytes",
        "Total de nós": count_nodes(data),
        "Profundidade máxima": max_depth(data),
        "Chaves únicas": len(all_keys),
        "Total de objetos": count_objects(data),
        "Total de arrays": count_arrays(data),
        "Tipo raiz": type(data).__name__,
    }


def try_fix_json(text: str) -> str:
    """Tenta corrigir JSONs com erros comuns."""
    fixed = text.strip()

    # Trailing commas: ,} ou ,]
    fixed = re.sub(r",\s*([}\]])", r"\1", fixed)

    # Single quotes → double quotes (cuidado com apóstrofos dentro de strings)
    # Simples: troca aspas simples que delimitam chaves/valores
    if "'" in fixed and '"' not in fixed:
        fixed = fixed.replace("'", '"')

    # Chaves sem aspas: { key: "value" } → { "key": "value" }
    fixed = re.sub(
        r'(?<=[{,])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:',
        r' "\1":',
        fixed,
    )

    # Comentários de linha
    fixed = re.sub(r"//.*$", "", fixed, flags=re.MULTILINE)

    # Comentários de bloco
    fixed = re.sub(r"/\*.*?\*/", "", fixed, flags=re.DOTALL)

    return fixed


def render_tree(data, prefix="", is_last=True, is_root=True) -> str:
    """Gera representação em árvore do JSON."""
    lines = []
    connector = "" if is_root else ("└── " if is_last else "├── ")
    child_prefix = "" if is_root else (prefix + ("    " if is_last else "│   "))

    if isinstance(data, dict):
        if not is_root:
            lines.append(f"{prefix}{connector}{{object}}")
        items = list(data.items())
        for i, (key, value) in enumerate(items):
            last = i == len(items) - 1
            if isinstance(value, (dict, list)):
                lines.append(f"{child_prefix}{'└── ' if last else '├── '}\"{key}\":")
                sub_prefix = child_prefix + ("    " if last else "│   ")
                lines.append(render_tree(value, sub_prefix, True, False))
            else:
                display = json.dumps(value, ensure_ascii=False)
                lines.append(
                    f"{child_prefix}{'└── ' if last else '├── '}\"{key}\": {display}"
                )
    elif isinstance(data, list):
        if not is_root:
            lines.append(f"{prefix}{connector}[array ({len(data)} items)]")
        for i, item in enumerate(data):
            last = i == len(data) - 1
            if isinstance(item, (dict, list)):
                lines.append(f"{child_prefix}{'└── ' if last else '├── '}[{i}]:")
                sub_prefix = child_prefix + ("    " if last else "│   ")
                lines.append(render_tree(item, sub_prefix, True, False))
            else:
                display = json.dumps(item, ensure_ascii=False)
                lines.append(
                    f"{child_prefix}{'└── ' if last else '├── '}[{i}]: {display}"
                )
    else:
        display = json.dumps(data, ensure_ascii=False)
        lines.append(f"{prefix}{connector}{display}")

    return "\n".join(lines)


def validate_json_strict(text: str) -> list[str]:
    """Valida JSON e retorna lista de warnings."""
    warnings = []

    # Verifica trailing commas
    if re.search(r",\s*[}\]]", text):
        warnings.append("⚠️ Trailing comma detectada (não permitida no JSON padrão)")

    # Verifica comentários
    if re.search(r"//|/\*", text):
        warnings.append("⚠️ Comentários detectados (não permitidos no JSON padrão)")

    # Verifica single quotes
    if re.search(r"(?<![\\])'", text) and '"' not in text:
        warnings.append("⚠️ Aspas simples detectadas (JSON requer aspas duplas)")

    # Verifica chaves sem aspas
    if re.search(r"(?<=[{,])\s*[a-zA-Z_]\w*\s*:", text):
        warnings.append("⚠️ Chaves sem aspas detectadas")

    # Verifica duplicatas
    try:
        decoder = json.JSONDecoder(object_pairs_hook=lambda pairs: pairs)
        pairs = decoder.decode(text)

        def check_dupes(pairs_list, path=""):
            issues = []
            if isinstance(pairs_list, list) and all(
                isinstance(p, tuple) and len(p) == 2 for p in pairs_list
            ):
                keys = [p[0] for p in pairs_list]
                seen = set()
                for k in keys:
                    if k in seen:
                        issues.append(
                            f"⚠️ Chave duplicada: \"{k}\" em {path or 'raiz'}"
                        )
                    seen.add(k)
                for k, v in pairs_list:
                    issues.extend(check_dupes(v, f"{path}.{k}"))
            return issues

        warnings.extend(check_dupes(pairs))
    except Exception:
        pass

    return warnings


# ── Sidebar de opções ───────────────────────────────────────
with st.sidebar:
    st.subheader("⚙️ Opções")

    indent_option = st.selectbox(
        "Indentação:",
        options=["Tab", "1 espaço", "2 espaços", "3 espaços", "4 espaços", "Compacto"],
        index=4,
        key="json_indent",
    )

    indent_map = {
        "Tab": "\t",
        "1 espaço": 1,
        "2 espaços": 2,
        "3 espaços": 3,
        "4 espaços": 4,
        "Compacto": None,
    }
    indent_value = indent_map[indent_option]

    sort_keys = st.checkbox("Ordenar chaves", value=False, key="json_sort")
    ensure_ascii = st.checkbox("Escapar caracteres não-ASCII", value=False, key="json_ascii")
    auto_fix = st.checkbox("🔧 Tentar corrigir JSON inválido", value=False, key="json_fix")

    st.divider()
    st.caption("Padrão: RFC 8259")


# ── Área principal ──────────────────────────────────────────
col_input, col_output = st.columns([1, 1], gap="large")

with col_input:
    st.subheader("📝 JSON Data")

    # Tabs para input: colar, upload ou URL
    input_tab1, input_tab2 = st.tabs(["Colar", "Upload"])

    with input_tab1:
        json_input = st.text_area(
            "Cole seu JSON aqui",
            placeholder='{\n  "name": "John",\n  "age": 30,\n  "active": true\n}',
            height=400,
            key="json_input_paste",
            label_visibility="collapsed",
        )

    with input_tab2:
        uploaded_file = st.file_uploader(
            "Envie um arquivo JSON",
            type=["json", "txt"],
            key="json_file_upload",
        )
        if uploaded_file:
            json_input = uploaded_file.read().decode("utf-8")
            st.text_area(
                "Conteúdo do arquivo:",
                value=json_input,
                height=350,
                disabled=True,
                key="json_file_preview",
            )

    col_process, col_clear = st.columns(2)
    with col_process:
        process_btn = st.button(
            "▶️ Processar JSON", type="primary", use_container_width=True
        )
    with col_clear:
        if st.button("🗑️ Limpar", use_container_width=True, key="json_clear"):
            st.rerun()

with col_output:
    st.subheader("📤 Resultado")

    if process_btn and json_input:
        raw_text = json_input.strip()
        original_text = raw_text

        # Validação (warnings)
        warnings = validate_json_strict(raw_text)

        # Tentar fix se habilitado
        if auto_fix:
            raw_text = try_fix_json(raw_text)
            if raw_text != original_text:
                warnings.insert(0, "🔧 JSON foi corrigido automaticamente")

        try:
            data = json.loads(raw_text)

            # Status
            if warnings:
                for w in warnings:
                    st.warning(w)
            st.success("✅ JSON válido!")

            # Tabs de saída
            out_tab1, out_tab2, out_tab3 = st.tabs(
                ["Formatado", "🌳 Tree View", "📊 Estatísticas"]
            )

            with out_tab1:
                separators = (",", ":") if indent_value is None else (",", ": ")
                formatted = json.dumps(
                    data,
                    indent=indent_value,
                    sort_keys=sort_keys,
                    ensure_ascii=ensure_ascii,
                    separators=separators,
                )
                st.code(formatted, language="json", line_numbers=True)

                size_original = len(original_text.encode("utf-8"))
                size_formatted = len(formatted.encode("utf-8"))
                diff = size_formatted - size_original
                sign = "+" if diff > 0 else ""

                st.caption(
                    f"Original: {size_original:,}B → Formatado: {size_formatted:,}B ({sign}{diff:,}B)"
                )

                col_dl1, col_dl2 = st.columns(2)
                with col_dl1:
                    st.download_button(
                        "⬇️ Baixar formatado",
                        data=formatted,
                        file_name="formatted.json",
                        mime="application/json",
                        use_container_width=True,
                    )
                with col_dl2:
                    minified = json.dumps(
                        data,
                        separators=(",", ":"),
                        ensure_ascii=ensure_ascii,
                    )
                    st.download_button(
                        "⬇️ Baixar minificado",
                        data=minified,
                        file_name="minified.json",
                        mime="application/json",
                        use_container_width=True,
                    )

            with out_tab2:
                tree = render_tree(data)
                st.code(tree, language="text", line_numbers=False)

            with out_tab3:
                stats = get_json_stats(data, raw_text)
                for label, value in stats.items():
                    st.metric(label=label, value=value)

        except json.JSONDecodeError as e:
            st.error(f"❌ JSON inválido!")

            # Informações detalhadas do erro
            st.markdown(f"""
            **Erro:** {e.msg}

            **Linha:** {e.lineno} | **Coluna:** {e.colno} | **Posição:** {e.pos}
            """)

            # Mostrar a linha com erro
            lines = raw_text.split("\n")
            if e.lineno and e.lineno <= len(lines):
                error_line = lines[e.lineno - 1]
                st.code(error_line, language="text")
                pointer = " " * max(0, e.colno - 1) + "^"
                st.code(pointer, language="text")

            if not auto_fix:
                st.info("💡 Dica: habilite **Tentar corrigir JSON inválido** nas opções da sidebar.")

    elif process_btn:
        st.warning("Cole ou envie um JSON para processar.")
    else:
        st.info("Cole seu JSON e clique em **Processar JSON** para começar.")
