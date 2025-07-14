import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime
from st_aggrid import AgGrid, GridOptionsBuilder
import unicodedata

def normaliza(texto):
    if pd.isna(texto):
        return ""
    return unicodedata.normalize('NFKD', str(texto)).encode('ASCII', 'ignore').decode().lower()

def extrai_empresa(conta):
    conta_norm = normaliza(conta)
    if "pp participacoes" in conta_norm:
        return "PP PARTICIPAÇÕES"
    elif "xbrother" in conta_norm:
        return "XBROTHERS"
    elif "tempreco" in conta_norm:
        return "TEMPREÇO"
    else:
        return "OUTROS"

def show_conc_bancario(arquivo_selecionado):
    try:
        df_raw = pd.read_excel(arquivo_selecionado)
    except Exception as e:
        st.error(f"Erro ao ler '{arquivo_selecionado}': {e}")
        st.stop()

    df = df_raw.copy()

    # --- ADICIONA COLUNA DE EMPRESA ---
    col_conta = None
    for col in df.columns:
        if normaliza(col) == "conta bancaria":
            col_conta = col
            break
    if col_conta is None:
        st.error('Coluna "Conta Bancária" não encontrada.')
        st.stop()

    df["EMPRESA"] = df[col_conta].apply(extrai_empresa)

    # FILTRO DE EMPRESA (selectbox com opção "Todas")
    empresas_unicas = ["Todas", "PP PARTICIPAÇÕES", "XBROTHERS", "TEMPREÇO"]
    empresa_sel = st.selectbox(
        "Filtrar por empresa:",
        empresas_unicas,
        index=0,
        key="empresa_cb"
    )
    if empresa_sel != "Todas":
        df = df[df["EMPRESA"] == empresa_sel]

    # NOVO: CAMPO DE BUSCA GERAL (manual)
    busca_manual = st.text_input("Filtrar por texto (procura em todas as colunas):", "", key="busca_manual_cb")
    if busca_manual:
        df = df[df.apply(lambda row: row.astype(str).str.contains(busca_manual, case=False, na=False), axis=1).any(axis=1)]

    # Datas
    colunas_data = [col for col in df.columns if "data" in normaliza(col)]
    coluna_data = colunas_data[0] if colunas_data else None
    if coluna_data:
        st.markdown("<b>Período de busca</b>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            data_ini = st.date_input("Data Inicial", value=datetime.today().replace(day=1), key="data_ini_cb")
        with col2:
            data_fim = st.date_input("Data Final", value=datetime.today(), key="data_fim_cb")
        data_ini = pd.to_datetime(data_ini)
        data_fim = pd.to_datetime(data_fim)
        df[coluna_data] = pd.to_datetime(df[coluna_data], errors="coerce")
        if data_ini and data_fim:
            mask = (df[coluna_data] >= data_ini) & (df[coluna_data] <= data_fim)
            df = df[mask]
        elif data_fim:
            df = df[df[coluna_data] <= data_fim]

    # FILTRO DE CONCILIADO (mantido)
    col_conciliado = [col for col in df.columns if "conciliado" in normaliza(col)]
    col_conciliado = col_conciliado[0] if col_conciliado else None
    if col_conciliado:
        opcoes = ["Não Especificado", "Sim", "Não"]
        escolha = st.selectbox("Filtrar por Conciliado:", opcoes, key="conciliado_cb")
        if escolha == "Sim":
            df = df[df[col_conciliado].astype(str).str.lower().isin(["sim", "conciliado", "true", "1"])]
        elif escolha == "Não":
            df = df[df[col_conciliado].astype(str).str.lower().isin(["não", "nao", "false", "0", "n"])]

    # CÁLCULO E EXIBIÇÃO DOS SALDOS (POSITIVO E NEGATIVO)
    col_valor = None
    for col in df.columns:
        if "valor" in normaliza(col):
            col_valor = col
            break

    total_receitas = total_despesas = 0
    if col_valor:
        df[col_valor] = pd.to_numeric(df[col_valor], errors='coerce')
        total_receitas = df[df[col_valor] > 0][col_valor].sum()
        total_despesas = df[df[col_valor] < 0][col_valor].sum()

        c1, c2 = st.columns(2)
        with c1:
            st.metric("Total de Receitas", f"R$ {total_receitas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        with c2:
            st.metric("Total de Despesas", f"R$ {total_despesas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    # Exportação
    st.write("## Exportar resultado para Excel")
    output = io.BytesIO()
    nome_arquivo = f"resultado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Resultado')
    st.download_button(
        label=f"Baixar resultado filtrado ({nome_arquivo})",
        data=output.getvalue(),
        file_name=nome_arquivo,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # CONTAGEM DE REGISTROS (ESTILO PRINT)
    st.markdown(
        f"<div style='font-size:14px;margin-bottom:-4px;margin-top:4px;text-align:left;'>"
        f"<b>Exibindo {len(df):,} de {len(df_raw):,} registros</b></div>",
        unsafe_allow_html=True
    )

    # AG-GRID
    if not df.empty:
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_default_column(editable=False, groupable=True, resizable=True)
        gb.configure_side_bar()
        grid_options = gb.build()
        AgGrid(
            df,
            gridOptions=grid_options,
            enable_enterprise_modules=False,
            allow_unsafe_jscode=True,
            theme="material",
            height=680,
            use_container_width=True
        )
    else:
        st.info("Nenhum dado para exibir.")
