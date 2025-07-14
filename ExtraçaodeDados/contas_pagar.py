import streamlit as st
import pandas as pd
import os
from datetime import datetime

def show_contas_pagar():
    st.title("Contas a Pagar - KPIs e Gráficos")

    base_path = os.path.dirname(os.path.abspath(__file__))
    pasta_main = os.path.join(base_path, "contas_pagar")
    path_quebra = os.path.join(pasta_main, "caixa", "quebra de caixa", "quebra-de-caixa.xlsx")
    path_sangria = os.path.join(pasta_main, "caixa", "sangria", "sangria.xlsx")

    # Arquivo principal (demais abas)
    arquivos_xlsx = [f for f in os.listdir(pasta_main) if f.lower().endswith(".xlsx")]
    arquivo_carregado = None
    if arquivos_xlsx:
        arquivos_xlsx.sort(key=lambda f: os.path.getmtime(os.path.join(pasta_main, f)), reverse=True)
        arquivo_carregado = arquivos_xlsx[0]

    opcoes_pagamento = [
        {"key": "caixa", "label": "CAIXA", "icon": "💵"},
        {"key": "debito_credito_pix", "label": "DÉBITO OU CRÉDITO E PIX", "icon": "💳"},
        {"key": "boleto", "label": "BOLETO", "icon": "🧾"},
    ]
    subopcoes = {
        "caixa": ["QUEBRA DE CAIXA", "SANGRIA"],
        "debito_credito_pix": ["DÉBITO", "CRÉDITO", "PIX"],
        "boleto": ["PAGO", "PENDENTE"]
    }

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
            color: #c43a3a !important;
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

    tipo_escolhido = st.session_state.get("tipo_pagamento_pagar", None)
    subopcao_escolhida = st.session_state.get("subopcao_pagar", None)

    # Cards principais
    card_col = st.columns(3)
    for idx, op in enumerate(opcoes_pagamento):
        selected = tipo_escolhido == op['key']
        button_text = f"{op['icon']} {op['label']}"
        btn = card_col[idx].button(
            button_text,
            key=f"card_pagar_{op['key']}",
            use_container_width=True,
            help=op['label'],
        )
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
            st.session_state.tipo_pagamento_pagar = op['key']
            tipo_escolhido = op['key']
            st.session_state.subopcao_pagar = None

    # Sub-botões
    if tipo_escolhido and tipo_escolhido in subopcoes:
        st.write("")
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
                key=f"subopcao_{sub}",
                use_container_width=True
            )
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
                st.session_state.subopcao_pagar = sub
                subopcao_escolhida = sub

        if not subopcao_escolhida:
            st.info("Selecione uma opção para ver os filtros.")
            return

    elif tipo_escolhido is None:
        st.info("Selecione uma opção para exibir os filtros.")
        return

    # ===== ABA QUEBRA DE CAIXA =====
    if tipo_escolhido == "caixa" and subopcao_escolhida == "QUEBRA DE CAIXA":
        if not os.path.exists(path_quebra):
            st.error("Arquivo de Quebra de Caixa não encontrado!")
            return
        df = pd.read_excel(path_quebra)
        df.columns = [c.strip() for c in df.columns]
        colunas_lower = {c.lower(): c for c in df.columns}
        status_col = colunas_lower.get('status', None)
        caixa_col = colunas_lower.get('caixa', None)
        un_col = colunas_lower.get('un. negócio', None)
        data_col = colunas_lower.get('data e hora inicial', None)
        quebra_col = colunas_lower.get('quebra de caixa', None)

        with st.form("filtros_quebra_de_caixa"):
            cols1 = st.columns(3)
            status_opcoes = sorted(df[status_col].dropna().unique()) if status_col else []
            status_selecionado = cols1[0].multiselect("Status", status_opcoes, key="status_qc")
            caixa_opcoes = sorted(df[caixa_col].dropna().unique()) if caixa_col else []
            caixa_selecionado = cols1[1].multiselect("Caixa", caixa_opcoes, key="caixa_qc")
            un_opcoes = sorted(df[un_col].dropna().unique()) if un_col else []
            un_selecionado = cols1[2].multiselect("Un. Negócio", un_opcoes, key="unegocio_qc")
            data_min = pd.to_datetime(df[data_col], errors="coerce").min() if data_col else None
            data_max = pd.to_datetime(df[data_col], errors="coerce").max() if data_col else None
            data_ini, data_fim = st.date_input(
                "Período Data e Hora Inicial",
                value=(data_min, data_max) if data_min and data_max else (None, None),
                key="dt_qc"
            )
            submitted = st.form_submit_button("Buscar")

        df_filt = df.copy()
        if status_col and status_selecionado:
            df_filt = df_filt[df_filt[status_col].isin(status_selecionado)]
        if caixa_col and caixa_selecionado:
            df_filt = df_filt[df_filt[caixa_col].isin(caixa_selecionado)]
        if un_col and un_selecionado:
            df_filt = df_filt[df_filt[un_col].isin(un_selecionado)]
        if data_col and data_ini and data_fim:
            datas = pd.to_datetime(df_filt[data_col], errors="coerce")
            df_filt = df_filt[(datas.dt.date >= data_ini) & (datas.dt.date <= data_fim)]

        st.markdown("## Resultado da Quebra de Caixa")
        if quebra_col:
            total_qc = df_filt[quebra_col].sum()
            sobra = df_filt[df_filt[quebra_col] > 0][quebra_col].sum()
            falta = df_filt[df_filt[quebra_col] < 0][quebra_col].sum()
            st.write(f"**Total Quebra de Caixa (R$):** {total_qc:.2f}")
            st.write(f"**Sobra (R$):** {sobra:.2f}")
            st.write(f"**Falta (R$):** {falta:.2f}")
        st.dataframe(df_filt, use_container_width=True)
        return

    # ===== ABA SANGRIA =====
    if tipo_escolhido == "caixa" and subopcao_escolhida == "SANGRIA":
        if not os.path.exists(path_sangria):
            st.error("Arquivo de Sangria não encontrado!")
            return
        df = pd.read_excel(path_sangria)
        df.columns = [c.strip() for c in df.columns]
        colunas_lower = {c.lower(): c for c in df.columns}
        status_col = colunas_lower.get('status', None)
        caixa_col = colunas_lower.get('caixa', None)
        un_col = colunas_lower.get('un. negócio', None)
        data_col = colunas_lower.get('data e hora inicial', None)
        valor_col = colunas_lower.get('valor', None)

        with st.form("filtros_sangria"):
            cols1 = st.columns(3)
            status_opcoes = sorted(df[status_col].dropna().unique()) if status_col else []
            status_selecionado = cols1[0].multiselect("Status", status_opcoes, key="status_sg")
            caixa_opcoes = sorted(df[caixa_col].dropna().unique()) if caixa_col else []
            caixa_selecionado = cols1[1].multiselect("Caixa", caixa_opcoes, key="caixa_sg")
            un_opcoes = sorted(df[un_col].dropna().unique()) if un_col else []
            un_selecionado = cols1[2].multiselect("Un. Negócio", un_opcoes, key="unegocio_sg")
            data_min = pd.to_datetime(df[data_col], errors="coerce").min() if data_col else None
            data_max = pd.to_datetime(df[data_col], errors="coerce").max() if data_col else None
            data_ini, data_fim = st.date_input(
                "Período Data e Hora Inicial",
                value=(data_min, data_max) if data_min and data_max else (None, None),
                key="dt_sg"
            )
            submitted = st.form_submit_button("Buscar")

        df_filt = df.copy()
        if status_col and status_selecionado:
            df_filt = df_filt[df_filt[status_col].isin(status_selecionado)]
        if caixa_col and caixa_selecionado:
            df_filt = df_filt[df_filt[caixa_col].isin(caixa_selecionado)]
        if un_col and un_selecionado:
            df_filt = df_filt[df_filt[un_col].isin(un_selecionado)]
        if data_col and data_ini and data_fim:
            datas = pd.to_datetime(df_filt[data_col], errors="coerce")
            df_filt = df_filt[(datas.dt.date >= data_ini) & (datas.dt.date <= data_fim)]

        st.markdown("## Resultado da Sangria")
        if valor_col:
            total = df_filt[valor_col].sum()
            st.write(f"**Total Sangria (R$):** {total:.2f}")
        st.dataframe(df_filt, use_container_width=True)
        return

    # ===== ABA PRINCIPAL - demais filtros padrão (Un. Negócio) =====
    if arquivo_carregado:
        df = pd.read_excel(os.path.join(pasta_main, arquivo_carregado))
        df.columns = [c.strip() for c in df.columns]
        colunas_lower = {c.lower(): c for c in df.columns}
        with st.form("filtros_gerais"):
            col1, col2, col3 = st.columns(3)
            status_col = colunas_lower.get('status', None)
            status_opcoes = sorted(df[status_col].dropna().unique()) if status_col else []
            status_selecionado = col1.multiselect("Status", status_opcoes, key="status_geral")
            caixa_col = colunas_lower.get('caixa', None)
            caixa_opcoes = sorted(df[caixa_col].dropna().unique()) if caixa_col else []
            caixa_selecionado = col2.multiselect("Caixa", caixa_opcoes, key="caixa_geral")
            un_col = colunas_lower.get('un. negócio', None)
            un_opcoes = sorted(df[un_col].dropna().unique()) if un_col else []
            un_selecionado = col3.multiselect("Un. Negócio", un_opcoes, key="un_geral")
            data_col = colunas_lower.get('data e hora inicial', None)
            data_min = pd.to_datetime(df[data_col], errors="coerce").min() if data_col else None
            data_max = pd.to_datetime(df[data_col], errors="coerce").max() if data_col else None
            data_ini, data_fim = st.date_input(
                "Período Data e Hora Inicial",
                value=(data_min, data_max) if data_min and data_max else (None, None),
                key="dt_geral"
            )
            submitted = st.form_submit_button("Buscar")

        df_filt = df.copy()
        if status_col and status_selecionado:
            df_filt = df_filt[df_filt[status_col].isin(status_selecionado)]
        if caixa_col and caixa_selecionado:
            df_filt = df_filt[df_filt[caixa_col].isin(caixa_selecionado)]
        if un_col and un_selecionado:
            df_filt = df_filt[df_filt[un_col].isin(un_selecionado)]
        if data_col and data_ini and data_fim:
            datas = pd.to_datetime(df_filt[data_col], errors="coerce")
            df_filt = df_filt[(datas.dt.date >= data_ini) & (datas.dt.date <= data_fim)]

        st.dataframe(df_filt, use_container_width=True)

