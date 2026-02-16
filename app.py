import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# --- CONFIGURAÇÃO DE ALTA PERFORMANCE ---
st.set_page_config(
    page_title="Amazon FBA | Command Center",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- DESIGN SYSTEM "WALL STREET" ---
st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
    .main-header {
        font-family: 'Helvetica Neue', sans-serif;
        color: #232f3e;
        font-weight: 700;
        margin-bottom: 0px;
    }
    .metric-container {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #ff9900;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        color: #856404;
        padding: 15px;
        border-radius: 5px;
        font-size: 0.9rem;
    }
    div[data-testid="stMetricValue"] { font-size: 24px; color: #111; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: PARÂMETROS ESTRATÉGICOS ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg", width=140)
    st.markdown("### ⚙️ Engine Financeiro")
    
    with st.expander("📊 Fiscal & Marketplace", expanded=True):
        taxa_imposto = st.number_input("Imposto Simples/Presumido (%)", 0.0, 35.0, 6.0, step=0.5) / 100
        comissao_amazon = st.number_input("Comissão Amazon (%)", 0.0, 30.0, 15.0, step=0.5) / 100
        taxa_fixa = st.number_input("Taxa Fixa (<R$79)", 0.0, 10.0, 5.0)

    with st.expander("📦 Logística & Estoque", expanded=True):
        fba_fee = st.number_input("Tarifa FBA (Peso/Dimensão)", 0.0, 500.0, 14.50, help="Consulte a tabela da Amazon baseada no peso cubado.")
        frete_inbound = st.number_input("Frete Fornecedor->Amazon (Unit)", 0.0, 100.0, 1.20)
        custo_estoque_mes = st.number_input("Custo Mensal Armazenagem (Unit)", 0.0, 50.0, 0.45)
        meses_estoque = st.slider("Giro de Estoque (Meses)", 1, 12, 1, help="Quanto tempo o produto fica parado pagando aluguel?")
        perda_estoque = st.slider("Provisionamento de Perda/Quebra (%)", 0.0, 10.0, 1.5) / 100

    with st.expander("📢 Marketing (PPC)", expanded=True):
        tacos_target = st.slider("Target TACOS (%)", 0.0, 40.0, 10.0, help="Total Advertising Cost of Sales: Quanto da receita total você gasta em anúncios.") / 100

    st.divider()
    st.caption("v2.0 Pro - Desenvolvido para Alta Performance")

# --- CORE CALCULATION ENGINE ---
def calcular_cenario(preco, custo_prod):
    # Receita Líquida de Vendas
    imposto_val = preco * taxa_imposto
    
    # Custos Variáveis de Venda
    comissao_val = preco * comissao_amazon
    taxa_fixa_val = taxa_fixa if preco < 79.0 else 0.0
    ads_val = preco * tacos_target
    perda_val = preco * perda_estoque
    
    # Custos Logísticos Totais
    armazenagem_total = custo_estoque_mes * meses_estoque
    logistica_total = fba_fee + frete_inbound + armazenagem_total + taxa_fixa_val
    
    # Custo Total e Lucros
    custos_totais = custo_prod + logistica_total + comissao_val + imposto_val + ads_val + perda_val
    lucro_liquido = preco - custos_totais
    
    # Métricas
    margem_bruta = ((preco - custo_prod) / preco) * 100 if preco > 0 else 0
    margem_liquida = (lucro_liquido / preco) * 100 if preco > 0 else 0
    roi = (lucro_liquido / custo_prod) * 100 if custo_prod > 0 else 0
    markup = preco / custo_prod if custo_prod > 0 else 0
    
    return {
        "Preço": preco,
        "Custo Produto": custo_prod,
        "Imposto": imposto_val,
        "Comissão Amazon": comissao_val,
        "Logística FBA": logistica_total,
        "Marketing (Ads)": ads_val,
        "Perdas/Outros": perda_val,
        "Lucro Líquido": lucro_liquido,
        "Margem Líquida": margem_liquida,
        "ROI": roi,
        "Markup": markup,
        "Break_Even": custos_totais - imposto_val - comissao_val - ads_val # Aproximado
    }

# --- MAIN UI ---
st.title("🦅 Amazon FBA Command Center")
nome_sku = st.text_input("Identificação do Produto (SKU/ASIN)", placeholder="Ex: Fone Bluetooth Pro X...")

# Abas de Navegação
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 P&L e Waterfall", 
    "🎯 Simulador Reverso", 
    "📈 Análise de Sensibilidade",
    "🤖 Diagnóstico IA"
])

# --- TAB 1: WATERFALL & P&L ---
with tab1:
    col_input, col_kpi = st.columns([1, 3], gap="large")
    
    with col_input:
        st.subheader("Inputs do Produto")
        c_prod = st.number_input("Custo de Aquisição (CMV)", 0.0, 10000.0, 45.00)
        p_venda = st.number_input("Preço de Venda (Buybox)", 0.0, 10000.0, 129.90)
        
        data = calcular_cenario(p_venda, c_prod)
        
        st.markdown("---")
        st.markdown("**Resumo Rápido:**")
        if data['Lucro Líquido'] > 0:
            st.success(f"Lucro: R$ {data['Lucro Líquido']:.2f}/un")
        else:
            st.error(f"Prejuízo: R$ {data['Lucro Líquido']:.2f}/un")

    with col_kpi:
        # KPI ROW
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Margem Líquida", f"{data['Margem Líquida']:.1f}%", delta_color="normal" if data['Margem Líquida'] > 15 else "inverse")
        k2.metric("ROI (Retorno)", f"{data['ROI']:.1f}%")
        k3.metric("Markup", f"{data['Markup']:.2f}x")
        k4.metric("Custo Mkt (Ads)", f"R$ {data['Marketing (Ads)']:.2f}")
        
        # CHART ROW: WATERFALL (O Pulo do Gato Financeiro)
        fig = go.Figure(go.Waterfall(
            name = "Fluxo de Caixa", orientation = "v",
            measure = ["relative", "relative", "relative", "relative", "relative", "relative", "relative", "total"],
            x = ["Venda Bruta", "Imposto", "Comissão", "FBA & Logística", "Custo Produto", "Ads (PPC)", "Perdas", "LUCRO LÍQUIDO"],
            textposition = "outside",
            text = [f"R${x:.2f}" for x in [data['Preço'], -data['Imposto'], -data['Comissão Amazon'], -data['Logística FBA'], -data['Custo Produto'], -data['Marketing (Ads)'], -data['Perdas/Outros'], data['Lucro Líquido']]],
            y = [data['Preço'], -data['Imposto'], -data['Comissão Amazon'], -data['Logística FBA'], -data['Custo Produto'], -data['Marketing (Ads)'], -data['Perdas/Outros'], data['Lucro Líquido']],
            connector = {"line":{"color":"rgb(63, 63, 63)"}},
            decreasing = {"marker":{"color":"#FF5252"}}, # Vermelho para custos
            increasing = {"marker":{"color":"#2ECC71"}}, # Verde para Venda
            totals = {"marker":{"color":"#232F3E"}}      # Azul Amazon para Lucro
        ))
        fig.update_layout(title="Demonstrativo de Resultado (Unitário)", showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)

# --- TAB 2: REVERSO ---
with tab2:
    st.subheader("🎯 Definindo Preço pela Meta")
    cr1, cr2 = st.columns(2)
    with cr1:
        custo_rev = st.number_input("Custo do Produto", 0.0, 5000.0, 45.0, key="rev_c")
        target_margin = st.slider("Meta de Margem Líquida (%)", 0, 50, 20)
    
    # Cálculo Reverso Complexo com Ads e Logística
    # Preço = (CustosFixos) / (1 - %Varaveis)
    # Variáveis: Imposto, Comissão, Ads, Perda, MargemMeta
    denominator = 1 - (taxa_imposto + comissao_amazon + tacos_target + perda_estoque + (target_margin/100))
    custos_fixos_abs = custo_rev + fba_fee + frete_inbound + (custo_estoque_mes * meses_estoque)
    
    with cr2:
        if denominator > 0:
            price_target = custos_fixos_abs / denominator
            if price_target < 79: price_target += taxa_fixa # Ajuste simples
            
            st.metric("Preço Sugerido de Venda", f"R$ {price_target:.2f}")
            st.info(f"Para sobrar **{target_margin}%** limpo no bolso, considerando que você vai gastar **{tacos_target*100}%** em anúncios.")
        else:
            st.error("Matematicamente impossível atingir essa margem com os custos atuais.")

# --- TAB 3: SENSIBILIDADE ---
with tab3:
    st.subheader("🧪 Matriz de Decisão")
    st.write("Simulação de Variação de Preço e Impacto no Lucro Anual (Est. 1000 un/mês)")
    
    base_price = p_venda
    range_prices = [base_price * (1 + x/100) for x in range(-15, 16, 5)]
    
    results = []
    for p in range_prices:
        d = calcular_cenario(p, c_prod)
        results.append({
            "Variação": f"{((p/base_price)-1)*100:+.0f}%",
            "Preço Venda": round(p, 2),
            "Lucro Unit": round(d['Lucro Líquido'], 2),
            "Margem %": round(d['Margem Líquida'], 1),
            "Lucro Mensal (1k un)": round(d['Lucro Líquido'] * 1000, 2)
        })
    
    df_sens = pd.DataFrame(results)
    st.dataframe(df_sens.style.background_gradient(subset=['Lucro Unit'], cmap='RdYlGn'), use_container_width=True)
    
    # Export Button
    csv = df_sens.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Baixar Relatório em CSV", data=csv, file_name="analise_precificacao.csv", mime="text/csv")

# --- TAB 4: DIAGNÓSTICO IA (Rule Based) ---
with tab4:
    st.subheader("🤖 Diagnóstico do Analista Virtual")
    
    m_liq = data['Margem Líquida']
    roi = data['ROI']
    ads = data['Marketing (Ads)']
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Análise de Viabilidade:**")
        if m_liq < 10:
            st.error("🔴 **ALTO RISCO:** Sua margem líquida está abaixo de 10%. Qualquer variação no PPC ou devolução pode gerar prejuízo real.")
        elif m_liq < 18:
            st.warning("🟡 **ATENÇÃO:** Margem saudável, mas apertada. Monitore o ACOS diariamente.")
        else:
            st.success("🟢 **EXCELENTE:** Margem acima de 18%. Produto com gordura para escalar agressivamente no Ads.")
            
    with c2:
        st.markdown("**Recomendação Estratégica:**")
        if roi < 30:
            st.write("📉 **ROI Baixo:** Seu capital volta muito devagar. Tente negociar preço com fornecedor ou aumentar o giro.")
        else:
            st.write("🚀 **ROI Alto:** Ótimo uso de capital. Reinvista o lucro para evitar ruptura de estoque.")
            
        if tacos_target > 0.15 and m_liq < 15:
            st.write("⚠️ **Alerta de Marketing:** Você está gastando muito em Ads para a margem que tem. Otimize suas campanhas.")

st.divider()
st.caption("Amazon FBA Intelligence Suite © 2024 - Modo Profissional Ativado")
