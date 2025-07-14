import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime
from st_aggrid import AgGrid, GridOptionsBuilder

def valor_final_col(df, col):
    # Pega o último valor não nulo da coluna após o filtro
    serie = df[col].dropna()
    if len(serie) > 0:
        return serie.iloc[-1]
    return 0

def show_mov_cc(arquivo_selecionado):
    try:
        xls = pd.ExcelFile(arquivo_selecionado)
        sheet_name = xls.sheet_names[0]
        df_raw = pd.read_excel(xls, sheet_name=sheet_name)
    except Exception as e:
        st.error(f"Erro ao ler o Excel: {e}")
        st.stop()

    df_raw.columns = [col.strip() for col in df_raw.columns]
    df = df_raw.copy()

    # Filtro "Tipo" com os nomes exatos
    tipos_exatos = [
        "Entrada de Transferência",
        "Estorno de Pagamento de Conta",
        "Estorno Entrada de Transferencia",
        "Lançamento de Entrada",
        "Lançamento de Saída",
        "Pagamento de Conta",
        "Saída de Transferência"
    ]
    col_tipo = None
    for col in df.columns:
        if col.strip().lower() == "tipo":
            col_tipo = col
            break
    if col_tipo is None:
        st.warning('Coluna "Tipo" não encontrada. Selecione manualmente:')
        col_tipo = st.selectbox("Coluna para filtro de tipo:", df.columns)
    tipo_sel = st.selectbox("Tipo", ["Todos"] + tipos_exatos, index=0)
    if tipo_sel != "Todos":
        df = df[df[col_tipo] == tipo_sel]

    # Campo de busca manual
    busca_manual = st.text_input("Filtrar por texto (procura em todas as colunas):", "", key="busca_manual_mc")
    if busca_manual:
        df = df[df.apply(lambda row: row.astype(str).str.contains(busca_manual, case=False, na=False), axis=1).any(axis=1)]

    # Filtro de data (primeira coluna que contém "data")
    colunas_data = [col for col in df.columns if "data" in col.lower()]
    coluna_data = colunas_data[0] if colunas_data else None
    if coluna_data:
        st.markdown("<b>Período de busca</b>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            data_ini = st.date_input("Data Inicial", value=datetime.today().replace(day=1))
        with col2:
            data_fim = st.date_input("Data Final", value=datetime.today())
        data_ini = pd.to_datetime(data_ini)
        data_fim = pd.to_datetime(data_fim)
        df[coluna_data] = pd.to_datetime(df[coluna_data], errors="coerce")
        if data_ini and data_fim:
            mask = (df[coluna_data] >= data_ini) & (df[coluna_data] <= data_fim)
            df = df[mask]
        elif data_fim:
            df = df[df[coluna_data] <= data_fim]

    # Filtro de status (caso exista)
    col_status = [col for col in df.columns if "status" in col.lower()]
    col_status = col_status[0] if col_status else None
    status_opcoes = ["Pendente", "Efetuado", "Cancelado", "Estornado"]
    if col_status:
        selected_status = st.multiselect(
            "Status",
            status_opcoes,
            default=[]
        )
        if selected_status:
            df = df[df[col_status].astype(str).str.capitalize().isin(selected_status)]

    # Cards: Débito, Crédito, Saldo, Saldo Anterior
    col_debito = next((col for col in df.columns if col.lower() in ["débito", "debito"]), None)
    col_credito = next((col for col in df.columns if col.lower() in ["crédito", "credito"]), None)
    col_saldo = next((col for col in df.columns if col.strip().lower() == "saldo"), None)
    col_saldo_anterior = next((col for col in df.columns if col.strip().lower() == "saldo anterior"), None)
    col_valor = next((col for col in df.columns if "valor" in col.lower()), None)

    debito = credito = saldo = saldo_anterior = 0

    if col_debito:
        debito = pd.to_numeric(df[col_debito], errors='coerce').sum()
    elif col_valor:
        debito = pd.to_numeric(df[df[col_valor] > 0][col_valor], errors='coerce').sum()

    if col_credito:
        credito = pd.to_numeric(df[col_credito], errors='coerce').sum()
    elif col_valor:
        credito = pd.to_numeric(df[df[col_valor] < 0][col_valor], errors='coerce').sum()

    if col_saldo:
        saldo = valor_final_col(df, col_saldo)
    if col_saldo_anterior:
        saldo_anterior = valor_final_col(df, col_saldo_anterior)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Débito", f"R$ {debito:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    with c2:
        st.metric("Crédito", f"R$ {credito:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    with c3:
        st.metric("Saldo", f"R$ {saldo:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    with c4:
        st.metric("Saldo Anterior", f"R$ {saldo_anterior:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    # Remove a coluna "Conta Bancária" se existir
    col_conta = next((col for col in df.columns if col.strip().lower() == "conta bancária"), None)
    if col_conta and col_conta in df.columns:
        df = df.drop(columns=[col_conta])

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
