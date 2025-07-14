import streamlit as st

def show_financeiro():
    st.header("Financeiro - Análises")

    # Menu de escolha de análise
    menu = st.selectbox(
        "Selecione o tipo de análise",
        (
            "Conciliação de extrato bancário",
            "Movimentação de conta corrente",
            "Transferências entre contas correntes"
        )
    )

    import os
    arquivos_xlsx = [f for f in os.listdir() if f.lower().endswith(".xlsx")]
    if not arquivos_xlsx:
        st.warning("Nenhum arquivo Excel encontrado na pasta do projeto.")
        st.stop()

    mapa_filtro = {
        "Conciliação de extrato bancário": ["concil", "extrato"],
        "Movimentação de conta corrente": ["mov", "corrente"],
        "Transferências entre contas correntes": ["transf", "transfer"]
    }
    padroes = mapa_filtro.get(menu, [])
    arquivo_encontrado = None
    for p in padroes:
        arquivos_filtrados = [f for f in arquivos_xlsx if p in f.lower()]
        if arquivos_filtrados:
            arquivo_encontrado = sorted(
                arquivos_filtrados,
                key=lambda x: os.path.getmtime(x),
                reverse=True
            )[0]
            break

    if not arquivo_encontrado:
        st.error(f"Nenhum arquivo correspondente ao filtro `{menu}` encontrado.")
        st.stop()

    st.info(f"Arquivo carregado: **{arquivo_encontrado}**")

    if menu == "Conciliação de extrato bancário":
        from conc_bancario import show_conc_bancario
        show_conc_bancario(arquivo_encontrado)

    elif menu == "Movimentação de conta corrente":
        from mov_cc import show_mov_cc
        show_mov_cc(arquivo_encontrado)

    elif menu == "Transferências entre contas correntes":
        from transf_cc import show_transf_cc
        show_transf_cc(arquivo_encontrado)
