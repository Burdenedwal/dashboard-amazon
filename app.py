import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA E ESTILO VISUAL (UI/UX)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Amazon FBA Financial Analyst Pro",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Paleta de Cores Amazon Pro
COLOR_DARK_BLUE = "#232f3e"
COLOR_ORANGE = "#ff9900"
COLOR_LIGHT_GREY = "#f0f2f6"
COLOR_SUCCESS = "#2ecc71"
COLOR_DANGER = "#e74c3c"
COLOR_WARNING = "#f1c40f"

# Custom CSS para Estética "Wall Street" / Amazon
st.markdown(f"""
    <style>
    .main {{
        background-color: #ffffff;
    }}
    .stApp header {{
        background-color: {COLOR_DARK_BLUE};
    }}
    h1, h2, h3 {{
        color: {COLOR_DARK_BLUE};
        font-family: 'Helvetica Neue', sans-serif;
    }}
    .metric-card {{
        background-color: {COLOR_LIGHT_GREY};
        border-left: 5px solid {COLOR_ORANGE};
        padding: 15px;
        border-radius: 5px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }}
    .stTabs [data-baseweb="tab-list"] {{
        gap: 2px;
    }}
    .stTabs [data-baseweb="tab"] {{
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {COLOR_DARK_BLUE};
        color: white;
    }}
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. SIDEBAR - INPUTS DE DADOS (DADOS DE ENTRADA)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg", width=150)
    st.markdown("### ⚙️ Parâmetros do Produto")
    
    product_name = st.text_input("Nome do Produto", "Fone Bluetooth Pro X")
    
    st.markdown("---")
    st.markdown("#### 💰 Precificação e Receita")
    price_sale = st.number_input("Preço de Venda (Buybox) R$", min_value=0.0, value=129.90, step=1.0)
    
    st.markdown("#### 📦 Custos do Produto (CMV)")
    cost_product = st.number_input("Custo Unitário (Fornecedor) R$", min_value=0.0, value=35.00, step=0.5)
    cost_inbound = st.number_input("Frete Inbound (Unitário) R$", min_value=0.0, value=1.50, step=0.1, help="Custo para enviar do fornecedor até o CD Amazon")
    cost_prep = st.number_input("Embalagem/Prep (Unitário) R$", min_value=0.0, value=1.00, step=0.1)
    
    st.markdown("#### 🏦 Taxas e Impostos")
    tax_rate = st.slider("Imposto (Simples/Presumido) %", 0.0, 30.0, 6.0, step=0.5) / 100
    commission_rate = st.slider("Comissão Amazon (Referral) %", 0.0, 30.0, 16.0, step=0.5) / 100
    
    st.markdown("#### 🚚 Logística FBA")
    fba_fee = st.number_input("Tarifa de Saída FBA (Peso/Dim) R$", min_value=0.0, value=14.50, step=0.5)
    storage_fee = st.number_input("Armazenagem Mensal Est. R$", min_value=0.0, value=0.50, step=0.1)
    
    st.markdown("#### 📉 Marketing e Riscos")
    tacos_target = st.slider("TACOS Alvo (Ads Total) %", 0.0, 50.0, 10.0, step=1.0, help="Total Advertising Cost of Sales: Gasto total de Ads dividido pela receita total") / 100
    return_rate = st.slider("Taxa de Devolução Estimada %", 0.0, 20.0, 3.0, step=0.5, help="Porcentagem de vendas que retornam e geram perdas") / 100

    # Lógica de Taxa Fixa (Regra < R$79)
    is_low_price = price_sale < 79.00
    fixed_fee_default = 5.00 if is_low_price else 0.00
    
    with st.expander("Configurações Avançadas de Taxas"):
        fixed_fee = st.number_input("Taxa Fixa (Regra < R$79)", value=fixed_fee_default)
        misc_costs = st.number_input("Outros Custos Variáveis R$", value=0.0)

# -----------------------------------------------------------------------------
# 3. NÚCLEO LÓGICO (CALCULATION ENGINE)
# -----------------------------------------------------------------------------

def calculate_financials(p_sale, p_cost, p_inbound, p_prep, p_tax, p_comm, p_fba, p_storage, p_tacos, p_return, p_fixed, p_misc):
    # Receita Bruta
    gross_revenue = p_sale
    
    # Custos Diretos de Venda (Deduções da Receita)
    val_tax = gross_revenue * p_tax
    val_comm = gross_revenue * p_comm
    val_fixed = p_fixed
    val_fba = p_fba
    val_storage = p_storage
    val_ads = gross_revenue * p_tacos
    
    # Custo de Mercadoria Vendida (CMV Total)
    cogs_total = p_cost + p_inbound + p_prep
    
    # Provisionamento de Perdas (Devoluções)
    # Estima-se que na devolução perde-se as taxas de ida e volta e as vezes o produto não volta vendável.
    # Simplificação: % da Venda como perda financeira direta
    val_returns = gross_revenue * p_return
    
    total_costs = val_tax + val_comm + val_fixed + val_fba + val_storage + val_ads + cogs_total + val_returns + p_misc
    
    net_profit = gross_revenue - total_costs
    
    # Métricas
    margin_gross = (gross_revenue - cogs_total) / gross_revenue if gross_revenue > 0 else 0
    margin_net = net_profit / gross_revenue if gross_revenue > 0 else 0
    roi = net_profit / cogs_total if cogs_total > 0 else 0 # ROI sobre investimento no produto
    markup = (p_sale / cogs_total) if cogs_total > 0 else 0
    
    break_even = (cogs_total + val_fixed + val_fba + val_storage + p_misc) / (1 - p_tax - p_comm - p_tacos - p_return)

    return {
        "gross_revenue": gross_revenue,
        "val_tax": val_tax,
        "val_comm": val_comm,
        "val_fixed": val_fixed,
        "val_fba": val_fba,
        "val_storage": val_storage,
        "val_ads": val_ads,
        "cogs_total": cogs_total,
        "val_returns": val_returns,
        "val_misc": p_misc,
        "total_costs": total_costs,
        "net_profit": net_profit,
        "margin_net": margin_net * 100,
        "roi": roi * 100,
        "break_even": break_even
    }

metrics = calculate_financials(
    price_sale, cost_product, cost_inbound, cost_prep, tax_rate, commission_rate, 
    fba_fee, storage_fee, tacos_target, return_rate, fixed_fee, misc_costs
)

# -----------------------------------------------------------------------------
# 4. DASHBOARD & VISUALIZAÇÃO
# -----------------------------------------------------------------------------

st.title(f"📊 FBA Command Center: {product_name}")
st.markdown(f"**Análise Financeira de Precisão** | Status: {'🟢 Lucrativo' if metrics['net_profit'] > 0 else '🔴 Prejuízo'}")

# --- TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["💼 Dashboard Executivo", "📉 Análise de Cascata (P&L)", "🎯 Simulação Reversa", "🤖 Diagnóstico IA"])

# --- TAB 1: DASHBOARD EXECUTIVO ---
with tab1:
    # KPI ROW
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Lucro Líquido Unitário", f"R$ {metrics['net_profit']:.2f}", delta_color="normal")
    with col2:
        st.metric("Margem Líquida Real", f"{metrics['margin_net']:.2f}%", delta=f"{metrics['margin_net'] - 15:.1f}pp vs Meta" if metrics['margin_net'] < 15 else None)
    with col3:
        st.metric("ROI (Retorno s/ Invest.)", f"{metrics['roi']:.2f}%", help="Quanto volta para o bolso para cada R$1 gasto em estoque")
    with col4:
        st.metric("Ponto de Equilíbrio (Break-even)", f"R$ {metrics['break_even']:.2f}", help="Preço mínimo de venda para não perder dinheiro")

    st.markdown("---")
    
    # Charts Row
    c_chart1, c_chart2 = st.columns([2, 1])
    
    with c_chart1:
        st.subheader("Composição de Custos")
        # Donut Chart
        labels = ['CMV (Produto+Frete)', 'Comissão Amazon', 'Logística FBA', 'Impostos', 'Marketing (Ads)', 'Outros (Dev/Arm)']
        values = [
            metrics['cogs_total'], 
            metrics['val_comm'] + metrics['val_fixed'], 
            metrics['val_fba'], 
            metrics['val_tax'], 
            metrics['val_ads'], 
            metrics['val_returns'] + metrics['val_storage'] + metrics['val_misc']
        ]
        
        fig_donut = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.5)])
        fig_donut.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=350)
        fig_donut.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_donut, use_container_width=True)
        
    with c_chart2:
        st.subheader("KPIs Rápidos")
        st.markdown(f"""
        <div class="metric-card">
            <b>Custo Total (Unit):</b><br>
            <span style="font-size: 24px;">R$ {metrics['total_costs']:.2f}</span>
        </div>
        <div style="height: 10px;"></div>
        <div class="metric-card">
            <b>Faturamento (100 unids):</b><br>
            <span style="font-size: 24px;">R$ {metrics['gross_revenue'] * 100:.2f}</span>
        </div>
        <div style="height: 10px;"></div>
        <div class="metric-card">
            <b>Lucro Est. (100 unids):</b><br>
            <span style="font-size: 24px; color: {COLOR_SUCCESS if metrics['net_profit'] > 0 else COLOR_DANGER};">R$ {metrics['net_profit'] * 100:.2f}</span>
        </div>
        """, unsafe_allow_html=True)

# --- TAB 2: WATERFALL (CASCATA) ---
with tab2:
    st.subheader("Fluxo de Erosão do Lucro (Waterfall)")
    st.caption("Entenda exatamente onde cada centavo da venda é consumido.")
    
    fig_waterfall = go.Figure(go.Waterfall(
        name = "20", orientation = "v",
        measure = ["relative", "relative", "relative", "relative", "relative", "relative", "relative", "relative", "total"],
        x = ["Preço Venda", "Impostos", "Comissão Amazon", "Taxa FBA", "CMV (Produto)", "Ads (TACOS)", "Armazenagem", "Devoluções/Perdas", "LUCRO LÍQUIDO"],
        textposition = "outside",
        text = [f"R$ {metrics['gross_revenue']:.2f}", f"-{metrics['val_tax']:.2f}", f"-{metrics['val_comm']+metrics['val_fixed']:.2f}", 
                f"-{metrics['val_fba']:.2f}", f"-{metrics['cogs_total']:.2f}", f"-{metrics['val_ads']:.2f}", 
                f"-{metrics['val_storage']:.2f}", f"-{metrics['val_returns']:.2f}", f"R$ {metrics['net_profit']:.2f}"],
        y = [metrics['gross_revenue'], -metrics['val_tax'], -(metrics['val_comm']+metrics['val_fixed']), 
             -metrics['val_fba'], -metrics['cogs_total'], -metrics['val_ads'], 
             -metrics['val_storage'], -metrics['val_returns'], metrics['net_profit']],
        connector = {"line":{"color":"rgb(63, 63, 63)"}},
        decreasing = {"marker":{"color":COLOR_DANGER}},
        increasing = {"marker":{"color":COLOR_SUCCESS}},
        totals = {"marker":{"color":COLOR_ORANGE}}
    ))
    
    fig_waterfall.update_layout(
        title = "Demonstrativo de Resultado Unitário (DRE)",
        showlegend = False,
        height=500,
        waterfallgap = 0.3
    )
    st.plotly_chart(fig_waterfall, use_container_width=True)

# --- TAB 3: SIMULAÇÃO REVERSA & SENSIBILIDADE ---
with tab3:
    col_rev, col_sens = st.columns([1, 1])
    
    with col_rev:
        st.markdown("### 🎯 Calculadora Reversa")
        st.info("Defina quanto você quer ganhar, e nós diremos o preço de venda.")
        
        target_margin_percent = st.number_input("Margem Líquida Alvo (%)", min_value=1.0, max_value=50.0, value=20.0, step=1.0)
        
        # Reverse Logic formula derived from: NetProfit = Price * (1 - VariableRates) - FixedCosts
        # Variable Rates = Tax + Comm + Ads + Returns
        # Fixed Costs = COGS + FBA + FixedFee + Storage + Misc
        # TargetNet = Price * Target%
        # Price * Target% = Price * (1 - Vars) - Fixed
        # Price * (1 - Vars - Target%) = Fixed
        # Price = Fixed / (1 - Vars - Target%)
        
        var_rates = tax_rate + commission_rate + tacos_target + return_rate
        total_fixed_costs = cost_product + cost_inbound + cost_prep + fba_fee + fixed_fee + storage_fee + misc_costs
        
        denominator = 1 - var_rates - (target_margin_percent/100)
        
        if denominator <= 0:
            st.error("Impossível atingir essa margem com os custos variáveis atuais! A soma das taxas percentuais excede o limite.")
        else:
            suggested_price = total_fixed_costs / denominator
            st.markdown(f"""
            <div style="background-color: #e8f4f8; padding: 20px; border-radius: 10px; text-align: center;">
                <span style="font-size: 16px; color: #555;">Para lucrar {target_margin_percent}% líquido:</span><br>
                <span style="font-size: 36px; font-weight: bold; color: {COLOR_DARK_BLUE};">R$ {suggested_price:.2f}</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Validação rápida
            new_profit = suggested_price * (target_margin_percent/100)
            st.write(f"Isso geraria um lucro unitário de **R$ {new_profit:.2f}**")

    with col_sens:
        st.markdown("### 🔥 Teste de Estresse (Sensibilidade)")
        st.caption("Como o lucro se comporta se o preço ou o custo do fornecedor mudar?")
        
        # Sensitivity Matrix Logic
        prices = np.linspace(price_sale * 0.8, price_sale * 1.2, 5)
        costs = np.linspace(cost_product * 0.8, cost_product * 1.2, 5)
        
        z_data = []
        y_labels = [f"Custo: {c:.2f}" for c in costs]
        x_labels = [f"Preço: {p:.2f}" for p in prices]
        
        for c in costs:
            row = []
            for p in prices:
                # Recalcula simplified
                res = calculate_financials(p, c, cost_inbound, cost_prep, tax_rate, commission_rate, fba_fee, storage_fee, tacos_target, return_rate, fixed_fee, misc_costs)
                row.append(res['net_profit'])
            z_data.append(row)
            
        fig_heat = go.Figure(data=go.Heatmap(
            z=z_data,
            x=x_labels,
            y=y_labels,
            colorscale='RdBu',
            texttemplate="R$ %{z:.2f}",
            zmid=0
        ))
        fig_heat.update_layout(title="Matriz de Lucro Líquido (R$)", height=400)
        st.plotly_chart(fig_heat, use_container_width=True)

# --- TAB 4: DIAGNÓSTICO IA ---
with tab4:
    st.subheader("🤖 FBA Analyst AI - Diagnóstico")
    
    col_kpi, col_advice = st.columns([1, 2])
    
    score = 100
    warnings = []
    successes = []
    
    # Logic Heuristics
    if metrics['margin_net'] < 10:
        score -= 20
        warnings.append(("CRÍTICO", "Margem líquida abaixo de 10%. Risco alto de prejuízo com qualquer variação de Ads ou Devoluções."))
    elif metrics['margin_net'] < 15:
        score -= 10
        warnings.append(("ATENÇÃO", "Margem saudável, mas aperte os cintos. Ideal buscar > 15-20%."))
    else:
        successes.append("Margem Líquida Saudável (>15%).")
        
    if metrics['roi'] < 30:
        score -= 20
        warnings.append(("BAIXO GIRO", "ROI abaixo de 30%. Seu capital está girando lento. Considere renegociar com fornecedor."))
    else:
        successes.append("ROI Excelente (>30%).")
        
    if metrics['val_ads'] > metrics['net_profit']:
        score -= 15
        warnings.append(("ADS EXPENSIVE", "Você está gastando mais em Ads do que lucrando. Cuidado com o TACOS."))

    with col_kpi:
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Saúde do Produto"},
            gauge = {
                'axis': {'range': [0, 100]},
                'bar': {'color': COLOR_ORANGE},
                'steps': [
                    {'range': [0, 50], 'color': "#ffe0e0"},
                    {'range': [50, 80], 'color': "#fff3cd"},
                    {'range': [80, 100], 'color': "#e0f7fa"}]
            }
        ))
        fig_gauge.update_layout(height=300)
        st.plotly_chart(fig_gauge, use_container_width=True)
        
    with col_advice:
        st.markdown("#### Relatório de Consultoria")
        
        for level, msg in warnings:
            if level == "CRÍTICO":
                st.error(f"**{level}:** {msg}")
            else:
                st.warning(f"**{level}:** {msg}")
                
        for msg in successes:
            st.success(f"**SUCESSO:** {msg}")
            
        st.markdown("---")
        st.caption("Recomendação: Utilize a aba 'Simulação Reversa' para ajustar seu preço de venda ideal com base nos alertas acima.")

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #888;'>Amazon FBA Command Center v2.0 | Developed for High Performance Sellers</div>", unsafe_allow_html=True)
