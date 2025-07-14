import streamlit as st
import os

st.set_page_config(page_title="Dashboard Empresarial", layout="wide")

# -------- CSS: Sidebar moderna, responsiva, sem overlay --------
st.markdown("""
    <style>
        section[data-testid="stSidebar"][aria-expanded="true"] {
            min-width: 230px !important;
            width: 230px !important;
            background: #232a32 !important;
            transition: width 0.15s;
        }
        section[data-testid="stSidebar"][aria-expanded="false"] {
            min-width: 0 !important;
            width: 0 !important;
            background: transparent !important;
            padding: 0 !important;
            overflow-x: hidden;
        }
        section[data-testid="stSidebar"][aria-expanded="false"] ~ div .main .block-container {
            max-width: 100vw !important;
            width: 100vw !important;
            padding-left: 3vw !important;
            padding-right: 3vw !important;
        }
        .main .block-container {
            max-width: 98vw !important;
            padding-left: 2vw !important;
            padding-right: 2vw !important;
        }
        .ag-theme-material {
            width: 98vw !important;
            min-width: 1200px;
        }
        .custom-menu-label {
            font-size: 1.03em;
            margin: 28px 0 18px 15px;
            color: #b9c5d3;
            font-weight: 700;
            letter-spacing: .3px;
        }
        .custom-menu-btn {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 14px 17px 14px 24px;
            font-size: 1.08em;
            color: #f7fafc;
            border-left: 5px solid transparent;
            margin-bottom: 12px;
            background: none;
            cursor: pointer;
            border-radius: 0 12px 12px 0;
            font-weight: 500;
            transition: background .15s, color .12s, border .19s;
            border: none;
            width: 100%;
            text-align: left;
        }
        .custom-menu-btn:hover {
            background: #28303a;
            color: #63e6fc;
        }
        .custom-menu-btn.selected {
            background: #21242b !important;
            color: #60ecff !important;
            border-left: 5px solid #2697f5 !important;
            font-weight: bold !important;
        }
        .custom-menu-ico {
            font-size: 1.25em;
            margin-right: 8px;
        }
    </style>
""", unsafe_allow_html=True)

# -------- Sidebar moderno sem radio duplicado ----------- 
with st.sidebar:
    st.markdown('<div class="custom-menu-label">Menu</div>', unsafe_allow_html=True)
    menu_itens = [
        {"key": "Dashboard", "label": "Dashboard", "ico": "📊"},
        {"key": "Financeiro", "label": "Financeiro", "ico": "💸"},
        {"key": "Contas a Pagar", "label": "Contas a Pagar", "ico": "📤"},
        {"key": "Contas a Receber", "label": "Contas a Receber", "ico": "📥"},
        {"key": "Orçamento", "label": "Orçamento", "ico": "📑"},
        {"key": "Extração de Dados", "label": "Extração de Dados", "ico": "🔍"}, # NOVO BOTÃO
    ]
    if "menu_lateral" not in st.session_state:
        st.session_state.menu_lateral = menu_itens[0]["key"]

    for item in menu_itens:
        is_selected = st.session_state.menu_lateral == item["key"]
        btn = st.button(
            f"{item['ico']} {item['label']}",
            key=f"menu_btn_{item['key']}",
            use_container_width=True
        )
        if btn:
            st.session_state.menu_lateral = item["key"]
        # CSS para destacar o selecionado
        st.markdown(
            f"""
            <style>
            [data-testid="stSidebar"] button#{'menu_btn_' + item['key']} {{
                {"background: #21242b; color: #60ecff; border-left: 5px solid #2697f5; font-weight: bold;" if is_selected else ""}
            }}
            </style>
            """, unsafe_allow_html=True
        )

menu_lateral = st.session_state.menu_lateral

# ----------- CHAMADAS DO MENU -----------

if menu_lateral == "Dashboard":
    from dashboard import show_dashboard
    show_dashboard()

elif menu_lateral == "Financeiro":
    st.title("Financeiro - Análises")
    menu = st.selectbox(
        "Selecione o tipo de análise",
        (
            "Conciliação de extrato bancário",
            "Movimentação de conta corrente",
            "Transferências entre contas correntes"
        )
    )

    # -- Alteração: arquivos agora ficam na pasta "financeiro"
    pasta_fin = os.path.join(os.path.dirname(os.path.abspath(__file__)), "financeiro")
    mapa_arquivo_exato = {
        "Conciliação de extrato bancário": "Conciliaçao de Extrato Bancario.xlsx",
        "Movimentação de conta corrente": "Movimentação de Conta Corrente.xlsx",
        "Transferências entre contas correntes": "Transferencia entre  Contas Correntes.xlsx",
    }

    arquivo_encontrado = os.path.join(pasta_fin, mapa_arquivo_exato[menu])
    if not os.path.exists(arquivo_encontrado):
        st.error(f"Arquivo `{os.path.basename(arquivo_encontrado)}` não encontrado na pasta 'financeiro'.")
        st.stop()

    st.info(f"Arquivo carregado: **{os.path.basename(arquivo_encontrado)}**")

    if menu == "Conciliação de extrato bancário":
        from conc_bancario import show_conc_bancario
        show_conc_bancario(arquivo_encontrado)

    elif menu == "Movimentação de conta corrente":
        from mov_cc import show_mov_cc
        show_mov_cc(arquivo_encontrado)

    elif menu == "Transferências entre contas correntes":
        from transf_cc import show_transf_cc
        show_transf_cc(arquivo_encontrado)

elif menu_lateral == "Contas a Pagar":
    # Os arquivos devem estar dentro de "contas_pagar"
    from contas_pagar import show_contas_pagar
    show_contas_pagar()

elif menu_lateral == "Contas a Receber":
    # Os arquivos devem estar dentro de "contas_receber"
    from contas_receber import show_contas_receber
    show_contas_receber()

elif menu_lateral == "Orçamento":
    # Os arquivos devem estar dentro de "orcamento"
    from orcamento import show_orcamento
    show_orcamento()

elif menu_lateral == "Extração de Dados":
    from extracao_dados import show_extracao_dados
    show_extracao_dados()
