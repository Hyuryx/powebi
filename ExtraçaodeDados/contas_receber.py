import streamlit as st
import pandas as pd
import os
from datetime import datetime

def show_contas_receber():
    st.title("Contas a Receber - KPIs e Gráficos")

    # Busca arquivo .xlsx mais recente na pasta contas_receber
    pasta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "contas_receber")
    arquivos_xlsx = [f for f in os.listdir(pasta) if f.lower().endswith(".xlsx")]
    arquivo_carregado = None
    if arquivos_xlsx:
        arquivos_xlsx.sort(key=lambda f: os.path.getmtime(os.path.join(pasta, f)), reverse=True)
        arquivo_carregado = arquivos_xlsx[0]

    # Opções principais e subopções
    opcoes_recebimento = [
        {"key": "caixa", "label": "CAIXA", "icon": "💵"},
        {"key": "debito_credito_pix", "label": "DÉBITO OU CRÉDITO E PIX", "icon": "💳"},
        {"key": "boleto", "label": "BOLETO", "icon": "🧾"},
    ]
    subopcoes = {
        "caixa": ["QUEBRA DE CAIXA", "SANGRIA"],
        "debito_credito_pix": ["DÉBITO", "CRÉDITO", "PIX"],
        "boleto": ["PAGO", "PENDENTE"]
    }
    # --- CSS dos cards e subcards ---
    st.markdown("""
        <style>
        div[data-testid="column"] > div > button.kpi-card {
            display: flex !important;
            align-items: center;
            justify-content: center;
            height: 70px;
            border: 2.5px solid #e6e6e6;
            border-radius: 18px;
            font-size: 1.3em;
            font-weight: 600;
            margin: 4px 0 10px 0;
            background: #fff;
            box-shadow: 0 2px 8px #00000010;
            transition: 0.17s;
            cursor: pointer;
        }
        div[data-testid="column"] > div > button.kpi-card.selected {
            border-width: 2.7px !important;
            box-shadow: 0 3px 18px #00000020;
            border-color: #1C62B6;
        }
        div[data-testid="column"] > div > button.kpi-card:hover {
            border-color: #1C62B6;
        }
        .sub-btn {
            display: inline-block;
            font-size: 1.13em;
            min-width: 180px;
            padding: 26px 32px;
            margin: 15px 40px 22px 0;
            border-radius: 28px;
            border: 2.5px solid #bbeede;
            background: #d4f8e8;
            color: #127055;
            font-weight: bold;
            letter-spacing: .5px;
            transition: background 0.14s, color 0.14s, border 0.13s, box-shadow 0.15s;
            box-shadow: 0 1px 12px #bbeede50;
            cursor: pointer;
            text-align: center;
        }
        .sub-btn.selected {
            background: #60ecbb;
            color: #034c34;
            border-color: #4ad39c;
        }
        .sub-btn.blue {background:#e2f2ff; color:#1666d6; border-color:#72bbff;}
        .sub-btn.blue.selected {background:#8fd0ff; color:#1666d6; border-color:#3976be;}
        .sub-btn.red {background:#fde8e8; color:#b22f2f; border-color:#ffabab;}
        .sub-btn.red.selected {background:#ffb9b9; color:#9c1313; border-color:#ff5757;}
        </style>
    """, unsafe_allow_html=True)

    tipo_escolhido = st.session_state.get("tipo_recebimento_receber", None)
    subopcao_escolhida = st.session_state.get("subopcao_receber", None)

    card_col = st.columns(3)
    for idx, op in enumerate(opcoes_recebimento):
        selected = tipo_escolhido == op['key']
        button_text = f"{op['icon']} {op['label']}"
        btn = card_col[idx].button(
            button_text,
            key=f"card_receber_{op['key']}",
            use_container_width=True,
            help=op['label'],
        )
        # Visually style button
        card_col[idx].markdown(
            f"""<script>
            var btns = window.parent.document.querySelectorAll('button[kind="secondary"]');
            if(btns.length>={idx+1}){{
                btns[{idx}].classList.add('kpi-card');
                {"btns["+str(idx)+"].classList.add('selected');" if selected else "btns["+str(idx)+"].classList.remove('selected');"}
            }}
            </script>""",
            unsafe_allow_html=True
        )
        if btn:
            st.session_state.tipo_recebimento_receber = op['key']
            tipo_escolhido = op['key']
            st.session_state.subopcao_receber = None

    # Sub-botões, só se tipo foi escolhido
    if tipo_escolhido and tipo_escolhido in subopcoes:
        st.write("")  # Espaço visual
        subs = subopcoes[tipo_escolhido]
        n_cols = len(subs)
        cols = st.columns(n_cols)
        for i, sub in enumerate(subs):
            sub_selected = subopcao_escolhida == sub
            cor_sub = ""
            if tipo_escolhido == "caixa":
                cor_sub = ""
            elif tipo_escolhido == "debito_credito_pix":
                cor_sub = "blue"
            elif tipo_escolhido == "boleto":
                cor_sub = "red"
            btn = cols[i].button(
                sub,
                key=f"subopcao_receber_{sub}",
                use_container_width=True
            )
            # JS visual
            cols[i].markdown(
                f"""<script>
                var subbtn = window.parent.document.querySelectorAll('button[kind="secondary"]')[{3+i}];
                if(subbtn){{
                    subbtn.classList.add('sub-btn');
                    {'subbtn.classList.add("selected");' if sub_selected else 'subbtn.classList.remove("selected");'}
                    {'subbtn.classList.add("'+cor_sub+'");' if cor_sub else ''}
                }}
                </script>""",
                unsafe_allow_html=True
            )
            if btn:
                st.session_state.subopcao_receber = sub
                subopcao_escolhida = sub

        if not subopcao_escolhida:
            st.info("Selecione uma opção para ver os filtros.")
            return

    elif tipo_escolhido is None:
        st.info("Selecione uma opção para exibir os filtros.")
        return

    # Filtros Correspondentes
    st.markdown("---")
    st.subheader("Filtros Correspondentes:")
    with st.form("busca_contas_receber"):
        col1, col2, col3 = st.columns(3)
        with col1:
            data_pagamento = st.date_input("Data Pagamento", value=None, key="receber_dt_pgto")
        with col2:
            data_vencimento = st.date_input("Data Vencimento", value=None, key="receber_dt_venc")
        with col3:
            data_emissao = st.date_input("Data Emissão", value=None, key="receber_dt_emi")
        bancos_caixas = st.text_input("Bancos e Caixas", key="receber_banco")
        lojas = st.text_input("Lojas", key="receber_loja")
        categoria_fin = st.text_input("Categoria Financeira", key="receber_cat")
        submitted = st.form_submit_button("Buscar")

    if arquivo_carregado:
        df = pd.read_excel(os.path.join(pasta, arquivo_carregado))
        df.columns = [c.strip() for c in df.columns]
        # Filtra pelo tipo de recebimento + subopção
        col_tipo_pag = next((c for c in df.columns if "pagamento" in c.lower() or "forma" in c.lower()), None)
        if col_tipo_pag:
            if tipo_escolhido == "caixa":
                if subopcao_escolhida == "QUEBRA DE CAIXA":
                    if any("quebra" in c.lower() for c in df.columns):
                        col_quebra = next((c for c in df.columns if "quebra" in c.lower()), None)
                        df = df[df[col_quebra].notnull()]
                elif subopcao_escolhida == "SANGRIA":
                    if any("sangria" in c.lower() for c in df.columns):
                        col_sangria = next((c for c in df.columns if "sangria" in c.lower()), None)
                        df = df[df[col_sangria].notnull()]
                else:
                    df = df[df[col_tipo_pag].astype(str).str.lower().str.contains("caixa|dinheiro")]
            elif tipo_escolhido == "debito_credito_pix":
                if subopcao_escolhida:
                    df = df[df[col_tipo_pag].astype(str).str.lower().str.contains(subopcao_escolhida.lower())]
            elif tipo_escolhido == "boleto":
                if subopcao_escolhida:
                    df = df[df[col_tipo_pag].astype(str).str.lower().str.contains(subopcao_escolhida.lower())]

        # Filtros adicionais
        if data_pagamento:
            col_data_pgto = next((c for c in df.columns if "pagamento" in c.lower()), None)
            if col_data_pgto:
                df = df[pd.to_datetime(df[col_data_pgto], errors="coerce").dt.date == data_pagamento]
        if data_vencimento:
            col_data_venc = next((c for c in df.columns if "venc" in c.lower()), None)
            if col_data_venc:
                df = df[pd.to_datetime(df[col_data_venc], errors="coerce").dt.date == data_vencimento]
        if data_emissao:
            col_data_emis = next((c for c in df.columns if "emi" in c.lower()), None)
            if col_data_emis:
                df = df[pd.to_datetime(df[col_data_emis], errors="coerce").dt.date == data_emissao]
        if bancos_caixas:
            col_banco = next((c for c in df.columns if "banco" in c.lower() or "caixa" in c.lower()), None)
            if col_banco:
                df = df[df[col_banco].astype(str).str.contains(bancos_caixas, case=False, na=False)]
        if lojas:
            col_loja = next((c for c in df.columns if "loja" in c.lower()), None)
            if col_loja:
                df = df[df[col_loja].astype(str).str.contains(lojas, case=False, na=False)]
        if categoria_fin:
            col_cat = next((c for c in df.columns if "categ" in c.lower()), None)
            if col_cat:
                df = df[df[col_cat].astype(str).str.contains(categoria_fin, case=False, na=False)]
        st.markdown("---")
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Nenhum registro encontrado para os filtros selecionados.")
    else:
        st.info("Nenhum dado para exibir ainda. Coloque um arquivo na pasta 'contas_receber'.")
