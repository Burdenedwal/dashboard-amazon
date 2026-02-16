import streamlit as st
import plotly.graph_objects as go

# Configuração de Layout Premium
st.set_page_config(
    page_title="Amazon FBA Pro | Intelligence Dashboard",
    page_icon="📈",
    layout="wide"
)

# Design System (CSS customizado)
st.markdown("""
    <style>
    .main { background-color: #f4f7f9; }
    [data-testid="stMetricValue"] { font-size: 1.8rem; font-weight: 700; color: #232f3e; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #ffffff;
        border-radius: 8px 8px 0px 0px;
        gap: 1px;
        padding-top: 10px;
    }
    .stTabs [aria-selected="true"] { background-color: #ff9900 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: PARÂMETROS GLOBAIS ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg", width=120)
    st.title("Configurações de Conta")
    
    with st.expander("📌 Impostos e Taxas", expanded=True):
        taxa_imposto = st.number_input("Imposto Simples Nacional (%)", 0.0, 25.0, 6.0, help="Alíquota do seu Simples Nacional baseada no seu faturamento anual.") / 100
        comissao_amazon = st.number_input("Comissão da Categoria (%)", 0.0, 25.0, 15.0, help="Porcentagem que a Amazon cobra sobre o valor total da venda.") / 100
        taxa_fixa_venda = st.number_input("Taxa Fixa p/ Venda < R$79 (R$)", 0.0, 10.0, 5.0, help="A Amazon cobra uma taxa fixa de R$ 5,00 para itens vendidos abaixo de R$ 79,00.")

    with st.expander("🚚 Logística FBA", expanded=True):
        tarifa_processamento_fba = st.number_input("Tarifa de Saída FBA (R$)", 0.0, 150.0, 14.50, help="Custo fixo que a Amazon cobra para separar, embalar e enviar seu produto.")
        custo_frete_inbound = st.number_input("Custo de Envio p/ Centro (R$)", 0.0, 50.0, 1.20, help="Quanto você gasta de frete para mandar uma unidade do seu fornecedor até o galpão da Amazon.")
        armazenagem_estimada = st.number_input("Armazenagem Mensal (R$)", 0.0, 10.0, 0.50, help="Estimativa de custo de ocupação de espaço no galpão da Amazon por unidade/mês.")

    st.divider()
    st.info("💡 Estas taxas são aplicadas em todos os cálculos automáticos.")

# --- LÓGICA CORE DE FINANÇAS ---
def calcular_financeiro(venda, custo_compra):
    v_imposto = venda * taxa_imposto
    v_comissao = venda * comissao_amazon
    v_taxa_fixa = taxa_fixa_venda if venda < 79.0 else 0.0
    
    custo_total_logistica = tarifa_processamento_fba + custo_frete_inbound + armazenagem_estimada + v_taxa_fixa
    desembolso_total = custo_compra + v_imposto + v_comissao + custo_total_logistica
    
    lucro = venda - desembolso_total
    margem = (lucro / venda) * 100 if venda > 0 else 0
    roi = (lucro / custo_compra) * 100 if custo_compra > 0 else 0
    markup = venda / custo_compra if custo_compra > 0 else 0
    
    return {
        "lucro": lucro, "margem": margem, "roi": roi, "markup": markup,
        "v_imposto": v_imposto, "v_comissao": v_comissao, "v_logistica": custo_total_logistica,
        "custo_produto": custo_compra, "venda": venda
    }

# --- INTERFACE PRINCIPAL ---
st.title("🏦 Dashboard de Inteligência de Preço - Amazon FBA")

# Campo para Nome do Produto
nome_produto = st.text_input("📦 Nome do Produto para Simulação", placeholder="Ex: Kit de Ferramentas Profissional")

st.markdown(f"### Analisando: {nome_produto if nome_produto else 'Novo Produto'}")

tab1, tab2, tab3 = st.tabs(["🔍 Simulador de Cenário", "🔄 Calculadora Reversa", "📊 Tabela de Sensibilidade"])

# TAB 1: SIMULADOR DE CENÁRIO
with tab1:
    c1, c2 = st.columns([1, 2])
    with c1:
        st.subheader("Entradas")
        custo_in = st.number_input("Custo de Compra (NF-e)", 0.01, 5000.0, 50.0, key="t1_c", help="O valor unitário que você paga ao fornecedor com impostos de entrada.")
        venda_in = st.number_input("Preço de Venda Pretendido", 0.01, 10000.0, 149.90, key="t1_v", help="O preço que será exibido no anúncio da Amazon.")
        
        dados = calcular_financeiro(venda_in, custo_in)
        
    with c2:
        m1, m2, m3 = st.columns(3)
        m1.metric("Lucro Líquido", f"R$ {dados['lucro']:.2f}", help="Dinheiro que sobra limpo no seu bolso após pagar tudo.")
        m2.metric("Margem Líquida", f"{dados['margem']:.1f}%", help="Porcentagem de lucro em relação ao preço de venda.")
        m3.metric("ROI", f"{dados['roi']:.1f}%", help="Retorno sobre o Investimento: quanto você ganha para cada real investido no produto.")
        
        # Gráfico de composição
        fig = go.Figure(data=[go.Pie(
            labels=['Produto', 'Impostos', 'Comissão', 'Logística FBA', 'Lucro'],
            values=[dados['custo_produto'], dados['v_imposto'], dados['v_comissao'], dados['v_logistica'], max(0, dados['lucro'])],
            hole=.4,
            marker_colors=['#BDC3C7', '#34495E', '#FF9900', '#2C3E50', '#27AE60']
        )])
        fig.update_layout(title="Distribuição do Real (Onde vai seu dinheiro?)")
        st.plotly_chart(fig, use_container_width=True)

# TAB 2: CALCULADORA REVERSA
with tab2:
    c1, c2 = st.columns([1, 2])
    with c1:
        st.subheader("Qual sua meta?")
        custo_rev = st.number_input("Custo de Compra (NF-e)", 0.01, 5000.0, 50.0, key="t2_c")
        margem_desejada = st.slider("Margem Líquida Alvo (%)", 5, 50, 20, help="Escolha a porcentagem de lucro que você deseja ter sobre a venda.")
        
        # Cálculo Simplificado para Reversa (assumindo venda > 79)
        denominador = (1 - taxa_imposto - comissao_amazon - (margem_desejada/100))
        if denominador > 0:
            preco_alvo = (custo_rev + tarifa_processamento_fba + custo_frete_inbound + armazenagem_estimada) / denominador
        else:
            preco_alvo = 0
            
    with c2:
        if preco_alvo > 0:
            st.success(f"### Preço Sugerido: R$ {preco_alvo:.2f}")
            res_rev = calcular_financeiro(preco_alvo, custo_rev)
            
            k1, k2, k3 = st.columns(3)
            k1.info(f"Markup: {res_rev['markup']:.2f}x")
            k2.info(f"Imposto: R$ {res_rev['v_imposto']:.2f}")
            k3.info(f"Comissão: R$ {res_rev['v_comissao']:.2f}")
            
            st.warning(f"Se você vender a **R$ {preco_alvo:.2f}**, sobrará **R$ {res_rev['lucro']:.2f}** por unidade após todas as taxas.")
        else:
            st.error("A meta de margem é impossível com as taxas atuais.")

# TAB 3: TABELA DE SENSIBILIDADE
with tab3:
    st.subheader("Análise de Elasticidade")
    st.markdown("Veja o que acontece com seu lucro se você der descontos ou subir o preço.")
    
    custo_sens = st.number_input("Custo do Produto", 0.01, 5000.0, 50.0, key="t3_c")
    venda_ref = st.number_input("Preço de Referência", 0.01, 10000.0, 150.0, key="t3_v")
    
    variacoes = [-0.15, -0.10, -0.05, 0, 0.05, 0.10, 0.15]
    
    st.markdown("---")
    cols_sens = st.columns(len(variacoes))
    
    for i, var in enumerate(variacoes):
        p_var = venda_ref * (1 + var)
        d_var = calcular_financeiro(p_var, custo_sens)
        with cols_sens[i]:
            cor = "normal" if var == 0 else "inverse" if var < 0 else "normal"
            st.metric(f"{var*100:+.0f}%", f"R$ {p_var:.0f}", delta=f"L: R${d_var['lucro']:.1f}", delta_color=cor)
            st.caption(f"Margem: {d_var['margem']:.1f}%")

st.divider()
st.caption("🔒 Amazon FBA Intelligence - Desenvolvido para decisão estratégica entre sócios.")
