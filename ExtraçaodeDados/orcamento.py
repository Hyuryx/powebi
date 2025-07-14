import streamlit as st
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt

def show_orcamento():
    st.title("Orçamento Analítico")

    # 1. Seleção do arquivo - busca só na pasta 'orcamento'
    pasta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "orcamento")
    if not os.path.exists(pasta):
        st.error(f"Pasta 'orcamento' não encontrada no diretório: {pasta}")
        st.stop()

    arquivos_xlsx = [f for f in os.listdir(pasta) if f.lower().endswith(".xlsx")]
    arq_padrao = None
    for f in arquivos_xlsx:
        if "orc" in f.lower():
            arq_padrao = f
            break

    if not arquivos_xlsx:
        st.warning("Nenhum arquivo XLSX encontrado na pasta 'orcamento'.")
        st.stop()

    arquivo = st.selectbox("Selecione o arquivo XLSX:", arquivos_xlsx, index=arquivos_xlsx.index(arq_padrao) if arq_padrao else 0)
    df = pd.read_excel(os.path.join(pasta, arquivo))
    df.columns = [c.strip() for c in df.columns]

    # Função para encontrar nomes de colunas mesmo com variações
    def encontrar_coluna(candidatos):
        for nome in df.columns:
            for cand in candidatos:
                if cand in nome.lower():
                    return nome
        return None

    col_conta = encontrar_coluna(['conta'])
    col_orcado = encontrar_coluna(['orçado', 'orcado'])
    col_previsto = encontrar_coluna(['previsto'])
    col_realizado = encontrar_coluna(['realizado'])
    col_tipo = encontrar_coluna(['tipo', 'grupo', 'classe'])  # se existir

    if not (col_conta and col_orcado and col_previsto and col_realizado):
        st.error("Sua planilha precisa ter colunas de Conta, Orçado, Previsto e Realizado (pode ter nomes ou acentos diferentes).")
        st.stop()

    # Filtros Extras
    st.subheader("Filtros")
    col1, col2 = st.columns(2)
    with col1:
        contas = sorted(df[col_conta].dropna().unique())
        sel_contas = st.multiselect("Conta(s)", contas, default=contas)
        df = df[df[col_conta].isin(sel_contas)]
    with col2:
        if col_tipo:
            tipos = sorted(df[col_tipo].dropna().unique())
            sel_tipos = st.multiselect("Tipo", tipos, default=tipos)
            df = df[df[col_tipo].isin(sel_tipos)]

    # Cálculo AH (Realizado/Orçado) e AV (Despesa/Faturamento)
    df_num = df.copy()
    for col in [col_orcado, col_previsto, col_realizado]:
        df_num[col] = pd.to_numeric(df_num[col], errors='coerce')

    # AH: Realizado / Orçado (em %)
    df['AH'] = np.where(df_num[col_orcado] != 0, df_num[col_realizado] / df_num[col_orcado], np.nan)
    # AV: Despesa (linha) / Faturamento
    if any(str(c).strip().lower() == 'faturamento' for c in df[col_conta]):
        try:
            fat_val = float(df_num[df[col_conta].str.lower() == 'faturamento'][col_orcado].values[0])
        except Exception:
            fat_val = None
        df['AV'] = np.where(
            df[col_conta].str.lower() != 'faturamento',
            np.where(fat_val and fat_val != 0, df_num[col_orcado] / fat_val, np.nan),
            np.nan
        )
    else:
        df['AV'] = np.nan

    # Formatação para visualização
    def format_moeda(val):
        try:
            return f"R$ {float(val):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except Exception:
            return val

    for col in [col_orcado, col_previsto, col_realizado]:
        df[col] = df[col].apply(format_moeda)
    df['AH'] = df['AH'].apply(lambda x: f"{x:.0%}" if pd.notnull(x) else "-")
    df['AV'] = df['AV'].apply(lambda x: f"{x:.0%}" if pd.notnull(x) else "-")

    # Mostra a tabela
    st.markdown("""
    <style>
    .orc-table td, .orc-table th {padding: 7px 12px; font-size: 1.09em;}
    .orc-table th {background: #f8fbfd;}
    .orc-table {background: #fff; border-radius: 8px;}
    </style>
    """, unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Gráfico de barras: Orçado, Previsto, Realizado (apenas contas filtradas)
    st.markdown("### Análise Visual por Conta")
    contas_plot = df[col_conta]
    orcado_plot = pd.to_numeric(df[col_orcado].str.replace('R\$','').str.replace('.','').str.replace(',','.').str.strip(), errors='coerce')
    previsto_plot = pd.to_numeric(df[col_previsto].str.replace('R\$','').str.replace('.','').str.replace(',','.').str.strip(), errors='coerce')
    realizado_plot = pd.to_numeric(df[col_realizado].str.replace('R\$','').str.replace('.','').str.replace(',','.').str.strip(), errors='coerce')

    fig, ax = plt.subplots(figsize=(9, 5))
    bar_width = 0.2
    index = np.arange(len(contas_plot))
    ax.bar(index, orcado_plot, bar_width, label='Orçado', color='#82d3f7')
    ax.bar(index + bar_width, previsto_plot, bar_width, label='Previsto', color='#a1e49d')
    ax.bar(index + 2 * bar_width, realizado_plot, bar_width, label='Realizado', color='#f7bc77')
    ax.set_xticks(index + bar_width)
    ax.set_xticklabels(contas_plot, rotation=18, ha='right', fontsize=11)
    ax.legend()
    ax.set_ylabel("Valores (R$)")
    ax.set_title("Comparativo Orçado x Previsto x Realizado")
    st.pyplot(fig)
