import streamlit as st
import os
import pandas as pd
import numpy as np
import io
from datetime import datetime
from st_aggrid import AgGrid, GridOptionsBuilder

def selecionar_arquivo_excel(titulo="Selecione o arquivo Excel:"):
    pasta = os.path.dirname(os.path.abspath(__file__))
    arquivos_xlsx = [f for f in os.listdir(pasta) if f.lower().endswith(".xlsx")]
    arquivos_xlsx = sorted(arquivos_xlsx)
    arquivo_escolhido = None

    if arquivos_xlsx:
        st.write(f"### {titulo}")
        arquivo_escolhido = st.radio(
            "Clique para escolher o arquivo:",
            arquivos_xlsx,
            key="select_file_radio_transf"
        )
        if arquivo_escolhido:
            st.markdown(
                f"<div style='margin-top:30px; background:#f3f3f3; border-radius:9px; padding:18px; text-align:center; font-size:20px;'>"
                f"<b>Arquivo selecionado:</b> {arquivo_escolhido}"
                f"</div>", unsafe_allow_html=True
            )
    else:
        st.warning("Nenhum arquivo Excel (.xlsx) encontrado na pasta do projeto.")
    return os.path.join(pasta, arquivo_escolhido) if arquivo_escolhido else None

def show_transf_cc(arquivo_selecionado=None):
    if not arquivo_selecionado:
        arquivo_selecionado = selecionar_arquivo_excel("Selecione o arquivo para Transferências entre Contas Correntes:")
    if not arquivo_selecionado:
        st.stop()

    try:
        xls = pd.ExcelFile(arquivo_selecionado)
        sheet_name = xls.sheet_names[0]
        df_raw = pd.read_excel(xls, sheet_name=sheet_name)
    except Exception as e:
        st.error(f"Erro ao ler o Excel: {e}")
        st.stop()

    df_raw.columns = [col.strip() for col in df_raw.columns]
    df = df_raw.copy()

    # Filtro de Status com selectbox (escala única)
    col_status = [col for col in df.columns if "status" in col.lower()]
    col_status = col_status[0] if col_status else None
    status_cores = {
        "Pendente": "#FFF9C4",
        "Efetuado": "#C8E6C9",
        "Cancelado": "#FFCDD2",
        "Estornado": "#BBDEFB"
    }
    status_opcoes = ["Todos", "Nenhum"] + list(status_cores.keys())
    if col_status:
        selected_status = st.selectbox(
            "Status",
            status_opcoes,
            index=0,
            key="status_selectbox_tc"
        )
        # Legenda colorida dos status (destaca o selecionado)
        st.markdown(
            "".join([
                f"<span style='display:inline-block;"
                f"background:{status_cores.get(s, '#fff') if selected_status==s else '#23252b'};"
                f"border-radius:6px;padding:7px 18px 7px 18px;margin:2px 8px 2px 0;"
                f"color:#111;font-weight:bold;font-size:17px;border:2.5px solid #bbb;"
                f"{'box-shadow:0 0 0 2.5px #1976d2;' if selected_status==s else ''};"
                f"transition:all .2s;'>"
                f"{s}</span>"
                for s in status_cores.keys()
            ]),
            unsafe_allow_html=True
        )
        # Filtro de status
        if selected_status == "Nenhum":
            df = df.iloc[0:0]  # Mostra nada
        elif selected_status != "Todos":
            df = df[df[col_status].astype(str).str.capitalize() == selected_status]

    # Campo de busca manual
    busca_manual = st.text_input("Filtrar por texto (procura em todas as colunas):", "", key="busca_manual_tc")
    if busca_manual:
        df = df[df.apply(lambda row: row.astype(str).str.contains(busca_manual, case=False, na=False), axis=1).any(axis=1)]

    # Filtro de data (primeira coluna que contém "data")
    colunas_data = [col for col in df.columns if "data" in col.lower()]
    coluna_data = colunas_data[0] if colunas_data else None
    if coluna_data:
        st.markdown("<b>Período de busca</b>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            data_ini = st.date_input("Data Inicial", value=datetime.today().replace(day=1), key="data_ini_tc")
        with col2:
            data_fim = st.date_input("Data Final", value=datetime.today(), key="data_fim_tc")
        data_ini = pd.to_datetime(data_ini)
        data_fim = pd.to_datetime(data_fim)
        df[coluna_data] = pd.to_datetime(df[coluna_data], errors="coerce")
        if data_ini and data_fim:
            mask = (df[coluna_data] >= data_ini) & (df[coluna_data] <= data_fim)
            df = df[mask]
        elif data_fim:
            df = df[df[coluna_data] <= data_fim]

    # >>>>>>> SOMA DINÂMICA DA COLUNA VALOR <<<<<<<
    col_valor = None
    for col in df.columns:
        if "valor" == col.lower().strip():
            col_valor = col
            break

    if col_valor:
        soma_valor = df[col_valor].replace(",", ".", regex=True)
        soma_valor = pd.to_numeric(soma_valor, errors='coerce').sum()
        st.markdown(
            f"""<div style='font-size:2.2em;font-weight:bold;color:#17c964;margin:20px 0 12px 0;'>
                Total do Valor: R$ {soma_valor:,.2f}
            </div>""", unsafe_allow_html=True
        )

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

    # Contagem de registros
    st.markdown(
        f"<div style='font-size:14px;margin-bottom:-4px;margin-top:4px;text-align:left;'>"
        f"<b>Exibindo {len(df):,} de {len(df_raw):,} registros</b></div>",
        unsafe_allow_html=True
    )

    # AG-GRID para mostrar a tabela filtrada
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
