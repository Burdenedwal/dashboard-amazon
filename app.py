import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# Configuração de Layout de Alta Performance
st.set_page_config(
    page_title="Amazon FBA | Pro Financial Intelligence",
    page_icon="💰",
    layout="wide"
)

# Design System Avançado (Estética Moderna e Profissional)
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .main-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .metric-label { font-size: 0.9rem; color: #64748b; font-weight: 600; }
    [data-testid="stMetricValue"] { font-size: 2.2rem; color: #0f172a; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: transparent; }
    .stTabs [data-baseweb="tab"] {
        background-color: #e2e8f0;
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
        color: #475569;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #232f3e !important; 
        color: #ffffff !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: MOTOR FINANCEIRO ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg", width=130)
    st.title("🎛️ Configurações Mestre")
    
    with st.expander("📊 Fiscal e Marketplace", expanded=True):
        taxa_imposto = st.number_input("Imposto (Simples Nacional %)", 0.0, 30.0, 6.0, help="Sua alíquota efetiva de imposto sobre a venda bruta.") / 100
        comissao_amazon = st.number_input("Comissão da Amazon (%)", 0.0, 25.0, 15.0, help="Comissão padrão da categoria do produto.") / 100
        taxa_fixa_venda = st.number_input("Taxa Fixa p/ Itens < R$79 (R$)", 0.0, 20.0, 5.0)

    with st.expander("📦 Logística FBA Avançada", expanded=True):
        tarifa_saida = st.number_input("Tarifa de Despacho FBA (R$)", 0.0, 200.0, 14.50, help="Custo de picking e packing da Amazon.")
        custo_inbound = st.number_input("Frete p/ CD Amazon (Unidade R$)", 0.0, 100.0, 1.50)
        armazenagem = st.number_input("Custo de Estocagem (Mês/Un R$)", 0.0, 50.0, 0.45)
        perda_estimada = st.slider("Margem de Perda/Devolução (%)", 0.0, 10.0, 1.5) / 100

    st.divider()
    st.success("Configurações aplicadas com sucesso!")

# --- MOTOR DE CÁLCULO PROFISSIONAL ---
def engine_financeiro(venda, custo_compra):
    # Valores Absolutos
    v_imposto = venda * taxa_imposto
    v_comissao = venda * comissao_amazon
    v_taxa_fixa = taxa_fixa_venda if venda < 79.0 else 0.0
    v_perda = venda * perda_estimada
    
    # Custos de Operação
    custos_logistica = tarifa_saida + custo_inbound + armazenagem + v_taxa_fixa
    custos_variaveis_venda = v_imposto + v_comissao + v_perda
    
    # Margens
    # Margem Bruta = (Venda - Custo Produto) / Venda
    lucro_bruto_valor = venda - custo_compra
    margem_bruta = (lucro_bruto_valor / venda) * 100 if venda > 0 else 0
    
    # Margem Líquida = (Venda - Todos os Custos) / Venda
    total_custos = custo_compra + custos_logistica + custos_variaveis_venda
    lucro_liquido = venda - total_custos
    margem_liquida = (lucro_liquido / venda) * 100 if venda > 0 else 0
    
    # ROI e Markup
    roi = (lucro_liquido / custo_compra) * 100 if custo_compra > 0 else 0
    markup = venda / custo_compra if custo_compra > 0 else 0
    
    return {
        "venda": venda, "custo": custo_compra, "lucro": lucro_liquido,
        "m_bruta": margem_bruta, "m_liquida": margem_liquida, "roi": roi, "markup": markup,
        "imposto_val": v_imposto, "comissao_val": v_comissao, "logistica_val": custos_logistica,
        "perda_val": v_perda, "total_custos": total_custos
    }

# --- UI PRINCIPAL ---
st.title("🚀 Amazon FBA Strategy Suite")

nome_p = st.text_input("📦 Identificação do SKU", placeholder="Digite o nome do produto ou código SKU")
st.markdown(f"### Dashboard de Análise: **{nome_p if nome_p else 'Produto Exemplo'}**")

tab_sim, tab_rev, tab_promo, tab_sens = st.tabs([
    "🔍 Simulador 360°", "🔄 Markup Reverso", "🎁 Mix de Promoção", "📈 Tabela de Elasticidade"
])

# --- TAB 1: SIMULADOR 360 ---
with tab_sim:
    c1, c2 = st.columns([1, 2], gap="large")
    with c1:
        st.subheader("Configuração de Venda")
        custo_prod = st.number_input("Preço de Custo (NF-e)", 0.01, 10000.0, 65.0, key="s_c")
        preco_venda = st.number_input("Preço de Venda (Amazon)", 0.01, 20000.0, 189.90, key="s_v")
        
        dados = engine_financeiro(preco_venda, custo_prod)
        st.divider()
        st.write("**Resumo por Unidade:**")
        st.write(f"Sobra no bolso: **R$ {dados['lucro']:.2f}**")
        st.write(f"Ponto de Equilíbrio: **R$ {dados['total_custos']:.2f}**")

    with c2:
        # Cards de Performance
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("Margem Bruta", f"{dados['m_bruta']:.1f}%", help="Diferença entre custo de compra e venda.")
        col_m2.metric("Margem Líquida", f"{dados['m_liquida']:.1f}%", help="O que sobra após TODAS as taxas e perdas.")
        col_m3.metric("ROI", f"{dados['roi']:.1f}%", help="Retorno sobre o capital investido no estoque.")
        col_m4.metric("Markup", f"{dados['markup']:.2f}x")

        # Gráfico Avançado
        fig = go.Figure()
        # CORREÇÃO AQUI: Removido o argumento 'name' duplicado
        fig.add_trace(go.Bar(
            y=['Financeiro'],
            x=[dados['custo']], 
            orientation='h', 
            name="Custo Produto", 
            marker_color='#cbd5e1'
        ))
        fig.add_trace(go.Bar(
            name='Amazon + Gov',
            y=['Financeiro'],
            x=[dados['imposto_val'] + dados['comissao_val'] + dados['logistica_val']], 
            orientation='h', 
            marker_color='#232f3e'
        ))
        fig.add_trace(go.Bar(
            name='Lucro Real',
            y=['Financeiro'],
            x=[max(0, dados['lucro'])], 
            orientation='h', 
            marker_color='#ff9900'
        ))
        fig.update_layout(barmode='stack', height=250, margin=dict(t=30, b=20), title="Visão de Fluxo por Venda")
        st.plotly_chart(fig, use_container_width=True)

# --- TAB 2: REVERSO ---
with tab_rev:
    st.subheader("🎯 Atingir Meta de Lucratividade")
    c_r1, c_r2 = st.columns(2)
    with c_r1:
        custo_r = st.number_input("Custo de Compra", 0.1, 10000.0, 65.0, key="r_c")
        meta_margem = st.slider("Qual sua meta de Margem Líquida (%)?", 5.0, 60.0, 18.0)
    
    # Cálculo Reverso Real
    # V = (Custo + Logistica) / (1 - %Imp - %Comis - %Perda - %Meta)
    den = (1 - taxa_imposto - comissao_amazon - perda_estimada - (meta_margem/100))
    if den > 0:
        v_sugerida = (custo_r + tarifa_saida + custo_inbound + armazenagem) / den
        with c_r2:
            st.success(f"### Preço de Venda Alvo: R$ {v_sugerida:.2f}")
            st.info(f"Para ter {meta_margem}% de lucro limpo, este deve ser seu preço.")
    else:
        st.error("Meta inalcançável com os custos atuais.")

# --- TAB 3: PROMOÇÕES ---
with tab_promo:
    st.subheader("🎁 Simulador 'Leve 2, Ganhe Desconto'")
    st.markdown("Analise a viabilidade de cupons e descontos progressivos.")
    
    c_p1, c_p2 = st.columns(2)
    with c_p1:
        unidades_promo = st.number_input("Quantidade no Combo", 1, 10, 2)
        desconto_total = st.slider("Desconto Total no Combo (%)", 0, 40, 10) / 100
        
        venda_base = preco_venda * unidades_promo
        venda_com_desconto = venda_base * (1 - desconto_total)
        custo_combo = custo_prod * unidades_promo
        
        # Na Amazon FBA, a taxa de saída pode ser cobrada por unidade ou reduzida em combos
        res_promo = engine_financeiro(venda_com_desconto / unidades_promo, custo_prod)
        lucro_combo = res_promo['lucro'] * unidades_promo
        
    with c_p2:
        st.metric("Lucro Total do Combo", f"R$ {lucro_combo:.2f}")
        st.metric("Margem Líquida do Combo", f"{res_promo['m_liquida']:.1f}%")
        if res_promo['m_liquida'] < 10:
            st.warning("Cuidado! Promoção agressiva demais, margem abaixo de 10%.")

# --- TAB 4: SENSIBILIDADE ---
with tab_sens:
    st.subheader("📊 Stress Test de Preço")
    st.write("Veja o impacto de pequenas mudanças no preço final:")
    
    precos_teste = [preco_venda * (1 + x) for x in [-0.2, -0.1, -0.05, 0, 0.05, 0.1, 0.2]]
    data_sens = []
    for p in precos_teste:
        r = engine_financeiro(p, custo_prod)
        data_sens.append({
            "Preço": f"R$ {p:.2f}",
            "Lucro R$": round(r['lucro'], 2),
            "M. Líquida": f"{r['m_liquida']:.1f}%",
            "ROI": f"{r['roi']:.1f}%",
            "Status": "✅ OK" if r['lucro'] > 0 else "❌ Prejuízo"
        })
    st.table(pd.DataFrame(data_sens))

st.divider()
st.caption(f"Propriedade de {nome_p if nome_p else 'Sua Empresa'}. Dashboard de Auditoria Financeira 2024.")
