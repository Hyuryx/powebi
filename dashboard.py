import streamlit as st
import pandas as pd
import os
import plotly.graph_objs as go

def ler_valor_arquivo(nome_arquivo, pasta_dashboard):
    caminho = os.path.join(pasta_dashboard, nome_arquivo + ".xlsx")
    if os.path.exists(caminho):
        try:
            df = pd.read_excel(caminho)
            # Procura a coluna 'valor' (qualquer variação de maiúsculas/minúsculas)
            col_valor = next((col for col in df.columns if col.strip().lower() == 'valor'), None)
            if col_valor and not df.empty:
                return float(df[col_valor].sum())
        except Exception as e:
            st.error(f"Erro ao ler {nome_arquivo}: {e}")
    return 0.0

def show_dashboard():
    st.title("📊 Dashboard Executivo – KPIs Financeiros")

    # 1. Pasta dos arquivos dos KPIs
    pasta_dashboard = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard")
    if not os.path.exists(pasta_dashboard):
        st.warning(f"Pasta 'dashboard' não encontrada em: {pasta_dashboard}")
        st.stop()

    # 2. Ler cada arquivo individualmente
    saldo_pago = ler_valor_arquivo("saldo_pago", pasta_dashboard)
    saldo_pendente = ler_valor_arquivo("saldo_pendente", pasta_dashboard)
    saldo_recebido = ler_valor_arquivo("saldo_recebido", pasta_dashboard)
    saldo_atual = ler_valor_arquivo("saldo_atual", pasta_dashboard)  # se desejar mostrar o arquivo isolado
    saldo_a_pagar = ler_valor_arquivo("saldo_a_pagar", pasta_dashboard)
    saldo_a_receber = ler_valor_arquivo("saldo_a_receber", pasta_dashboard)
    
    # === Calcular o Saldo Previsto: Recebido + Pago - Pendente ===
    saldo_previsto = saldo_recebido + saldo_pago - saldo_pendente

    # Lista dos KPIs para mostrar (saldo_atual pode ser sobrescrito pelo cálculo acima se quiser)
    kpis = [
        {"nome": "💰 Saldo Atual", "valor": saldo_atual, "cor": "#3FB68B"},
        {"nome": "✅ Saldo Pago", "valor": saldo_pago, "cor": "#4A9DFE"},
        {"nome": "💸 Saldo a Pagar", "valor": saldo_a_pagar, "cor": "#FF6F6F"},
        {"nome": "💵 Saldo Recebido", "valor": saldo_recebido, "cor": "#F5A623"},
        {"nome": "📥 Saldo a Receber", "valor": saldo_a_receber, "cor": "#53C7F5"},
        {"nome": "📊 Saldo Previsto", "valor": saldo_previsto, "cor": "#6B47DC"},
    ]

    st.markdown("### KPIs Financeiros")
    kpi_cols = st.columns(3)
    for i, kpi in enumerate(kpis):
        with kpi_cols[i % 3]:
            st.markdown(f"""
                <div style='background:{kpi["cor"]}12;
                            border-radius:12px;
                            padding:24px 14px 8px 18px;
                            margin: 8px 0 12px 0;
                            box-shadow:0 1px 8px #0001;'>
                    <div style='font-size:1.16em;font-weight:bold;letter-spacing:.2px;color:#bbb;'>{kpi["nome"]}</div>
                    <div style='font-size:2.2em;color:{kpi["cor"]};font-weight:700;margin:7px 0 0 0;'>R$ {kpi["valor"]:,.2f}</div>
                </div>
            """, unsafe_allow_html=True)

    # Gráfico comparativo dos KPIs
    fig2 = go.Figure(go.Bar(
        x=[k["nome"] for k in kpis],
        y=[k["valor"] for k in kpis],
        marker=dict(color=[k["cor"] for k in kpis])
    ))
    fig2.update_layout(title="Comparativo dos KPIs Financeiros", xaxis_title="Indicador", yaxis_title="R$")
    st.plotly_chart(fig2, use_container_width=True)

    st.info("Saldo Previsto = Saldo Recebido + Saldo Pago - Saldo Pendente\n"
            "Todos os valores são somas da coluna 'valor' de cada arquivo XLSX na pasta 'dashboard'.")

# Basta rodar show_dashboard() na sua página principal.
