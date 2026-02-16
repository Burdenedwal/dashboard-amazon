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
COLOR_TEXT = "#111111"

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
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }}
    .metric-card:hover {{
        transform: translateY(-2px);
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
    
    /* Tooltip Customization via info icons */
    .stTooltipIcon {{
        color: {COLOR_ORANGE};
    }}
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. SIDEBAR - INPUTS DE DADOS (DADOS DE ENTRADA)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg", width=150)
    st.markdown("### ⚙️ Parâmetros do Produto")
    
    product_name = st.text_input("Nome do Produto", "Fone Bluetooth Pro X", help="Nome interno para identificação no relatório.")
    
    st.markdown("---")
    st.markdown("#### 💰 Precificação e Receita")
    price_sale = st.number_input(
        "Preço de Venda (Buybox) R$", 
        min_value=0.0, value=129.90, step=1.0, format="%.2f",
        help="O preço final que o cliente paga na Amazon. É a base para cálculo de todas as taxas percentuais."
    )
    
    st.markdown("#### 📦 Custos do Produto (CMV)")
    cost_product = st.number_input(
        "Custo Unitário (Fornecedor) R$", 
        min_value=0.0, value=35.00, step=0.5, format="%.2f",
        help="Quanto você paga por unidade para o fabricante/fornecedor."
    )
    cost_inbound = st.number_input(
        "Frete Inbound (Unitário) R$", 
        min_value=0.0, value=1.50, step=0.1, format="%.2f",
        help="Custo rateado para enviar o produto do fornecedor (ou sua casa) até o Centro de Distribuição (CD) da Amazon."
    )
    cost_prep = st.number_input(
        "Embalagem/Prep (Unitário) R$", 
        min_value=0.0, value=1.00, step=0.1, format="%.2f",
        help="Custo de etiquetas, polybags, caixas de envio ou serviço de preparação terceirizado."
    )
    
    st.markdown("#### 🏦 Taxas e Impostos")
    tax_rate_input = st.slider(
        "Imposto (Simples/Presumido) %", 
        0.0, 30.0, 6.0, step=0.5,
        help="Alíquota efetiva de imposto sobre a nota fiscal de venda (DAS). Consulte seu contador."
    )
    tax_rate = tax_rate_input / 100
    
    commission_rate_input = st.slider(
        "Comissão Amazon (Referral) %", 
        0.0, 30.0, 16.0, step=0.5,
        help="Taxa de referência da categoria (geralmente entre 12% e 16% + impostos sobre comissão se aplicável)."
    )
    commission_rate = commission_rate_input / 100
    
    st.markdown("#### 🚚 Logística FBA")
    fba_fee = st.number_input(
        "Tarifa de Saída FBA (Peso/Dim) R$", 
        min_value=0.0, value=14.50, step=0.5, format="%.2f",
        help="Taxa fixa cobrada pela Amazon para pegar (pick), embalar (pack) e enviar (ship) o produto ao cliente. Baseado no peso e dimensões."
    )
    storage_fee = st.number_input(
        "Armazenagem Mensal Est. R$", 
        min_value=0.0, value=0.50, step=0.1, format="%.2f",
        help="Custo estimado de ocupação de espaço no CD. Aumenta no Q4 (out/nov/dez)."
    )
    
    st.markdown("#### 📉 Marketing e Riscos")
    tacos_target_input = st.slider(
        "TACOS Alvo (Ads Total) %", 
        0.0, 50.0, 10.0, step=1.0,
        help="Total Advertising Cost of Sales. É o quanto do faturamento total você aceita gastar em anúncios (PPC) para manter as vendas girando."
    )
    tacos_target = tacos_target_input / 100
    
    return_rate_input = st.slider(
        "Taxa de Devolução Estimada %", 
        0.0, 20.0, 3.0, step=0.5,
        help="Porcentagem de vendas que retornam. O custo é calculado estimando a perda das taxas de envio e danos ao produto."
    )
    return_rate = return_rate_input / 100

    # Lógica de Taxa Fixa (Regra < R$79)
    is_low_price = price_sale < 79.00
    fixed_fee_default = 5.00 if is_low_price else 0.00
    
    with st.expander("🛠️ Configurações Avançadas de Taxas"):
        st.caption("Ajuste fino para custos ocultos.")
        fixed_fee = st.number_input(
            "Taxa Fixa (Regra < R$79)", 
            value=fixed_fee_default,
            help="Taxa administrativa extra que a Amazon cobra para itens abaixo de R$79,00."
        )
        misc_costs = st.number_input(
            "Outros Custos Variáveis R$", 
            value=0.0,
            help="Custos extras como adesivagem extra ou brindes inclusos."
        )

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
    
    # Break-even Point calculation
    # Fixed costs here refer to per-unit fixed values (FBA, Product Cost, Fixed Fee, Misc)
    # Variable costs here refer to percentages (Tax, Comm, Tacos, Return)
    # Price * (1 - Variable%) = FixedPerUnit
    denominator = (1 - p_tax - p_comm - p_tacos - p_return)
    break_even = (cogs_total + val_fixed + val_fba + val_storage + p_misc) / denominator if denominator > 0 else 999999

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
        "break_even": break_even,
        "markup": markup
    }

metrics = calculate_financials(
    price_sale, cost_product, cost_inbound, cost_prep, tax_rate, commission_rate, 
    fba_fee, storage_fee, tacos_target, return_rate, fixed_fee, misc_costs
)

# -----------------------------------------------------------------------------
# 4. DASHBOARD & VISUALIZAÇÃO
# -----------------------------------------------------------------------------

st.title(f"📊 FBA Command Center: {product_name}")
st.markdown(f"**Análise Financeira de Precisão** | Status: {'🟢 **LUCRATIVO**' if metrics['net_profit'] > 0 else '🔴 **PREJUÍZO**'}")

# --- TABS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💼 Dashboard Executivo", 
    "📉 Análise de Cascata (P&L)", 
    "🎯 Simulador & Psicologia de Preços", 
    "🔮 Cenários Futuros (Corrigido)",
    "❓ Glossário & Ajuda"
])

# --- TAB 1: DASHBOARD EXECUTIVO ---
with tab1:
    # KPI ROW
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Lucro Líquido Unitário", 
            f"R$ {metrics['net_profit']:.2f}", 
            delta_color="normal",
            help="O que sobra limpo no seu bolso após pagar TUDO (Produto, Amazon, Imposto, Ads)."
        )
    with col2:
        st.metric(
            "Margem Líquida Real", 
            f"{metrics['margin_net']:.2f}%", 
            delta=f"{metrics['margin_net'] - 15:.1f}pp vs Meta (15%)" if metrics['margin_net'] < 15 else None,
            help="A porcentagem do preço de venda que vira lucro. Abaixo de 15% é considerado arriscado para Private Label."
        )
    with col3:
        st.metric(
            "ROI (Retorno s/ Invest.)", 
            f"{metrics['roi']:.2f}%", 
            help="Para cada R$1,00 que você gasta comprando estoque, quanto volta de lucro? Ideal > 30%."
        )
    with col4:
        st.metric(
            "Break-even (Ponto de Equilíbrio)", 
            f"R$ {metrics['break_even']:.2f}", 
            help="O preço MÍNIMO que você pode vender para ficar no zero a zero (nem lucro, nem prejuízo)."
        )

    st.markdown("---")
    
    # Charts Row
    c_chart1, c_chart2 = st.columns([2, 1])
    
    with c_chart1:
        st.subheader("Para onde vai o dinheiro?")
        # Donut Chart with better colors
        labels = ['CMV (Produto+Frete)', 'Comissão Amazon', 'Logística FBA', 'Impostos', 'Marketing (Ads)', 'Outros (Dev/Arm)']
        values = [
            metrics['cogs_total'], 
            metrics['val_comm'] + metrics['val_fixed'], 
            metrics['val_fba'], 
            metrics['val_tax'], 
            metrics['val_ads'], 
            metrics['val_returns'] + metrics['val_storage'] + metrics['val_misc']
        ]
        colors = ['#2c3e50', '#f39c12', '#e67e22', '#e74c3c', '#3498db', '#95a5a6']
        
        fig_donut = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.6, marker=dict(colors=colors))])
        fig_donut.update_layout(
            margin=dict(t=20, b=20, l=20, r=20), 
            height=350,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
        )
        fig_donut.update_traces(textposition='outside', textinfo='percent+label')
        st.plotly_chart(fig_donut, use_container_width=True)
        
    with c_chart2:
        st.subheader("Projeção de Lote")
        
        lote_qty = st.number_input("Tamanho do Lote (unidades)", value=100, step=50)
        
        total_inv = metrics['cogs_total'] * lote_qty
        total_profit = metrics['net_profit'] * lote_qty
        total_rev = metrics['gross_revenue'] * lote_qty
        
        st.markdown(f"""
        <div class="metric-card">
            <small>Investimento em Estoque</small><br>
            <span style="font-size: 20px; font-weight: bold;">R$ {total_inv:,.2f}</span>
        </div>
        <div style="height: 10px;"></div>
        <div class="metric-card">
            <small>Faturamento Estimado</small><br>
            <span style="font-size: 20px; font-weight: bold;">R$ {total_rev:,.2f}</span>
        </div>
        <div style="height: 10px;"></div>
        <div class="metric-card" style="border-left: 5px solid {COLOR_SUCCESS if total_profit > 0 else COLOR_DANGER};">
            <small>Lucro Líquido do Lote</small><br>
            <span style="font-size: 24px; font-weight: bold; color: {COLOR_SUCCESS if total_profit > 0 else COLOR_DANGER};">
                R$ {total_profit:,.2f}
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        # Add Export Button
        csv_data = pd.DataFrame([metrics]).to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar Relatório CSV",
            data=csv_data,
            file_name=f'fba_analise_{product_name.replace(" ","_")}.csv',
            mime='text/csv',
        )

# --- TAB 2: WATERFALL (CASCATA) ---
with tab2:
    st.subheader("Fluxo de Erosão do Lucro (Waterfall)")
    st.markdown("Este gráfico mostra **exatamente** em qual etapa você está perdendo margem. Ideal para identificar gargalos.")
    
    fig_waterfall = go.Figure(go.Waterfall(
        name = "20", orientation = "v",
        measure = ["relative", "relative", "relative", "relative", "relative", "relative", "relative", "relative", "total"],
        x = ["Preço Venda", "Impostos", "Comissão Amazon", "Taxa FBA", "CMV (Produto)", "Ads (TACOS)", "Armazenagem", "Perdas/Dev", "LUCRO LÍQUIDO"],
        textposition = "outside",
        text = [f"R${metrics['gross_revenue']:.2f}", f"-{metrics['val_tax']:.2f}", f"-{metrics['val_comm']+metrics['val_fixed']:.2f}", 
                f"-{metrics['val_fba']:.2f}", f"-{metrics['cogs_total']:.2f}", f"-{metrics['val_ads']:.2f}", 
                f"-{metrics['val_storage']:.2f}", f"-{metrics['val_returns']:.2f}", f"R${metrics['net_profit']:.2f}"],
        y = [metrics['gross_revenue'], -metrics['val_tax'], -(metrics['val_comm']+metrics['val_fixed']), 
             -metrics['val_fba'], -metrics['cogs_total'], -metrics['val_ads'], 
             -metrics['val_storage'], -metrics['val_returns'], metrics['net_profit']],
        connector = {"line":{"color":"rgb(63, 63, 63)"}},
        decreasing = {"marker":{"color":COLOR_DANGER}},
        increasing = {"marker":{"color":COLOR_SUCCESS}},
        totals = {"marker":{"color":COLOR_ORANGE}}
    ))
    
    fig_waterfall.update_layout(
        title = "DRE Visual (Cascata)",
        showlegend = False,
        height=550,
        waterfallgap = 0.3
    )
    st.plotly_chart(fig_waterfall, use_container_width=True)

# --- TAB 3: SIMULAÇÃO REVERSA & PSICOLOGIA ---
with tab3:
    col_rev, col_psy = st.columns([1, 1])
    
    with col_rev:
        st.markdown("### 🎯 Calculadora Reversa")
        st.info("Digite quanto você quer de margem, e o sistema calcula o preço de venda necessário.")
        
        target_margin_percent = st.number_input("Margem Líquida Alvo (%)", min_value=1.0, max_value=60.0, value=20.0, step=1.0)
        
        var_rates = tax_rate + commission_rate + tacos_target + return_rate
        total_fixed_costs = cost_product + cost_inbound + cost_prep + fba_fee + fixed_fee + storage_fee + misc_costs
        
        denominator = 1 - var_rates - (target_margin_percent/100)
        
        if denominator <= 0:
            st.error("⚠️ Impossível! Seus custos variáveis (Imposto + Amazon + Ads) já são maiores que o que sobra para a margem.")
        else:
            suggested_price = total_fixed_costs / denominator
            st.markdown(f"""
            <div style="background-color: #e8f4f8; padding: 20px; border-radius: 10px; text-align: center; border: 1px solid #b3d7e8;">
                <span style="font-size: 14px; color: #555; text-transform: uppercase; letter-spacing: 1px;">Preço Matemático</span><br>
                <span style="font-size: 32px; font-weight: bold; color: {COLOR_DARK_BLUE};">R$ {suggested_price:.2f}</span>
            </div>
            """, unsafe_allow_html=True)
            
            new_profit_check = suggested_price * (target_margin_percent/100)
            st.caption(f"Lucro projetado nesse preço: R$ {new_profit_check:.2f}")

    with col_psy:
        st.markdown("### 🧠 Psicologia de Preços (Novo)")
        st.markdown("Preços matemáticos vendem menos. Use preços psicológicos para aumentar a conversão.")
        
        if denominator > 0:
            base_price = int(suggested_price)
            
            # Opções Psicológicas
            opt_90 = float(base_price) + 0.90
            if opt_90 < suggested_price: opt_90 += 1.0 # Ensure we don't drop too much
            
            opt_99 = float(base_price) + 0.99
            if opt_99 < suggested_price: opt_99 += 1.0
            
            opt_97 = float(base_price) + 0.97
            
            # Recalcular lucro para essas opções
            def quick_calc_profit(p):
                res = calculate_financials(p, cost_product, cost_inbound, cost_prep, tax_rate, commission_rate, fba_fee, storage_fee, tacos_target, return_rate, fixed_fee, misc_costs)
                return res['net_profit'], res['margin_net']

            p90, m90 = quick_calc_profit(opt_90)
            p99, m99 = quick_calc_profit(opt_99)
            
            st.markdown("**Sugestões Inteligentes:**")
            
            # Card 1
            st.markdown(f"""
            <div class="metric-card" style="margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="font-size: 22px; font-weight: bold;">R$ {opt_90:.2f}</span> <span style="color: #666; font-size: 12px;">(Padrão Brasileiro)</span>
                </div>
                <div style="text-align: right;">
                    <span style="font-size: 14px; color: {COLOR_SUCCESS if m90 >= target_margin_percent else COLOR_DANGER}">Margem: {m90:.1f}%</span><br>
                    <small>Lucro: R$ {p90:.2f}</small>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Card 2
            st.markdown(f"""
            <div class="metric-card" style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="font-size: 22px; font-weight: bold;">R$ {opt_99:.2f}</span> <span style="color: #666; font-size: 12px;">(Agressivo)</span>
                </div>
                <div style="text-align: right;">
                    <span style="font-size: 14px; color: {COLOR_SUCCESS if m99 >= target_margin_percent else COLOR_DANGER}">Margem: {m99:.1f}%</span><br>
                    <small>Lucro: R$ {p99:.2f}</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.caption("Nota: Preços terminados em .90 tendem a performar melhor no e-commerce brasileiro do que números quebrados como R$ 134,52.")

# --- TAB 4: CENÁRIOS FUTUROS (CORRIGIDO) ---
with tab4:
    st.subheader("🔮 Matriz de Cenários Automática")
    st.markdown("Não confie apenas no plano A. Veja o que acontece nos cenários Otimista e Pessimista.")
    
    # Definição dos Cenários
    scenarios = {
        "Pessimista 🌧️": {
            "price": price_sale * 0.90, # Vender 10% mais barato
            "cost": cost_product * 1.10, # Custo sobe 10%
            "ads": tacos_target * 1.20 # Ads sobem 20%
        },
        "Realista (Atual) ☁️": {
            "price": price_sale,
            "cost": cost_product,
            "ads": tacos_target
        },
        "Otimista ☀️": {
            "price": price_sale * 1.10, # Vender 10% mais caro
            "cost": cost_product * 0.95, # Negociou 5% desconto
            "ads": tacos_target * 0.80 # Otimizou ads
        }
    }
    
    scenario_display_data = []
    
    for name, params in scenarios.items():
        res = calculate_financials(
            params['price'], params['cost'], cost_inbound, cost_prep, 
            tax_rate, commission_rate, fba_fee, storage_fee, 
            params['ads'], return_rate, fixed_fee, misc_costs
        )
        # Formatando valores como strings para exibição segura e bonita
        scenario_display_data.append({
            "Cenário": name,
            "Preço Venda": f"R$ {params['price']:.2f}",
            "Lucro Líquido": f"R$ {res['net_profit']:.2f}",
            "Margem %": f"{res['margin_net']:.1f}%",
            "ROI %": f"{res['roi']:.1f}%"
        })
    
    # Convertendo para DataFrame apenas para estrutura, mas usando Plotly Table para renderizar
    df_display = pd.DataFrame(scenario_display_data)

    # Tabela Profissional usando Plotly (Substitui o st.dataframe com style que estava quebrando)
    fig_table = go.Figure(data=[go.Table(
        header=dict(values=list(df_display.columns),
                    fill_color=COLOR_DARK_BLUE,
                    font=dict(color='white', size=14),
                    align='left',
                    height=40),
        cells=dict(values=[df_display[k].tolist() for k in df_display.columns],
                   fill_color=[[COLOR_LIGHT_GREY if i % 2 == 0 else 'white' for i in range(len(df_display))]],
                   align='left',
                   font=dict(color=[COLOR_TEXT], size=13),
                   height=30)
    )])
    
    fig_table.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=200
    )
    
    st.plotly_chart(fig_table, use_container_width=True)
    
    st.info("💡 **Dica:** A tabela acima agora usa renderização gráfica para garantir 100% de estabilidade e visual profissional.")

# --- TAB 5: GLOSSÁRIO (NOVO) ---
with tab5:
    st.markdown("### 📚 Dicionário do Amazon Seller")
    st.markdown("Termos essenciais para entender a saúde do seu negócio.")
    
    with st.expander("O que é TACOS?"):
        st.write("""
        **Total Advertising Cost of Sales.** Diferente do ACOS (que olha só para a venda vinda do anúncio), 
        o TACOS mede o impacto dos anúncios no faturamento TOTAL (Orgânico + Pago).
        *Fórmula:* (Gasto Total Ads / Receita Total) * 100.
        *Meta:* Ideal manter abaixo de 10-15% para produtos maduros.
        """)
        
    with st.expander("O que é ROI vs. Margem?"):
        st.write("""
        **Margem:** Quanto sobra do preço de venda. (Ex: Vendi por 100, sobrou 20. Margem 20%).
        **ROI:** Quanto seu dinheiro rendeu. (Ex: Gastei 50 para comprar e vender o item. Lucrei 20. ROI = 20/50 = 40%).
        *Dica:* Pague as contas com Margem, mas enriqueça com ROI (Giro de estoque).
        """)
        
    with st.expander("Custos Ocultos (Storage e Devoluções)"):
        st.write("""
        Muitos vendedores esquecem de calcular:
        1. **Armazenagem:** Se o produto fica parado, você paga aluguel por cm³.
        2. **Devoluções:** O cliente devolve, a Amazon cobra taxa de envio e as vezes o produto volta "invendável". Sempre reserve 2-5% do faturamento para cobrir isso.
        """)

# --- AI DIAGNOSIS ---
st.markdown("---")
st.subheader("🤖 Diagnóstico Inteligente")

score = 100
warnings = []
successes = []

# Logic Heuristics
if metrics['margin_net'] < 10:
    score -= 25
    warnings.append(("CRÍTICO", "Margem líquida perigosamente baixa (<10%). Qualquer aumento no custo de ads vai gerar prejuízo."))
elif metrics['margin_net'] < 15:
    score -= 10
    warnings.append(("ATENÇÃO", "Margem abaixo de 15%. Volume de vendas precisa ser muito alto para compensar."))
else:
    successes.append("Margem Líquida saudável (>15%).")
    
if metrics['roi'] < 30:
    score -= 25
    warnings.append(("BAIXO GIRO", "ROI < 30%. O risco de capital empatado é alto. Tente negociar custo ou aumentar preço."))
else:
    successes.append("ROI excelente para Private Label (>30%).")
    
if metrics['break_even'] > (price_sale * 0.85):
    score -= 15
    warnings.append(("FRAGILIDADE", "Seu Break-even está muito próximo do preço atual. Você tem pouca margem para fazer promoções."))

col_score, col_text = st.columns([1, 3])

with col_score:
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': COLOR_ORANGE},
            'steps': [
                {'range': [0, 60], 'color': "#ffe0e0"},
                {'range': [60, 85], 'color': "#fff3cd"},
                {'range': [85, 100], 'color': "#e0f7fa"}]
        }
    ))
    fig_gauge.update_layout(height=180, margin=dict(t=30, b=30, l=30, r=30))
    st.plotly_chart(fig_gauge, use_container_width=True)

with col_text:
    for level, msg in warnings:
        if level == "CRÍTICO":
            st.error(f"**{level}:** {msg}")
        else:
            st.warning(f"**{level}:** {msg}")
            
    if not warnings:
        st.success("🎉 Produto com saúde financeira excelente! Sinal verde para investir.")
    
    st.caption("Nota baseada em benchmarks de Top Sellers da Amazon Brasil.")

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #888; font-size: 12px;'>Amazon FBA Command Center v3.1 | Ultimate Edition</div>", unsafe_allow_html=True)
