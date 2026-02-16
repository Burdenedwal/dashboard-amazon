import streamlit as st
import plotly.graph_objects as go

# Configuração da Página
st.set_page_config(
    page_title="Amazon Profit Master",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização Customizada (CSS)
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    div[data-testid="stSidebarUserContent"] {
        padding-top: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: CONFIGURAÇÕES FIXAS ---
st.sidebar.header("⚙️ Custos Operacionais")
st.sidebar.markdown("Configure as taxas padrão da sua conta.")

taxa_imposto = st.sidebar.slider("Imposto (Simples Nacional %)", 0.0, 20.0, 6.0) / 100
comissao_amazon = st.sidebar.slider("Comissão da Categoria (%)", 0.0, 25.0, 15.0) / 100
taxa_fixa_venda = st.sidebar.number_input("Taxa Fixa por Item (R$)", 0.0, 10.0, 2.00)
frete_fba_fbm = st.sidebar.number_input("Custo de Frete/Coleta (R$)", 0.0, 100.0, 18.00)

st.sidebar.divider()
st.sidebar.info("Dica: Use estes valores como base para todos os cálculos do dashboard.")

# --- TÍTULO ---
st.title("📊 Dashboard de Precificação Amazon")
st.markdown("Ferramenta profissional para análise de margem e ROI.")

# --- ABAS DE FUNCIONALIDADE ---
tab1, tab2 = st.tabs(["🔄 Calculadora Inversa (Preço Alvo)", "🔍 Simulador de Cenários"])

def calcular_metricas(preco_venda, custo_produto):
    v_comissao = preco_venda * comissao_amazon
    v_imposto = preco_venda * taxa_imposto
    custos_totais = custo_produto + v_comissao + v_imposto + taxa_fixa_venda + frete_fba_fbm
    lucro_liquido = preco_venda - custos_totais
    margem = (lucro_liquido / preco_venda) * 100 if preco_venda > 0 else 0
    roi = (lucro_liquido / custo_produto) * 100 if custo_produto > 0 else 0
    
    return {
        "lucro": lucro_liquido,
        "margem": margem,
        "roi": roi,
        "v_comissao": v_comissao,
        "v_imposto": v_imposto,
        "custos_fixos": taxa_fixa_venda + frete_fba_fbm
    }

# --- TAB 1: CALCULADORA INVERSA ---
with tab1:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Inputs")
        custo_bruto = st.number_input("Custo do Produto (NF-e)", min_value=0.01, value=50.0, key="c1")
        margem_alvo = st.number_input("Margem Líquida Desejada (%)", min_value=1.0, value=20.0)
        
        # Cálculo de Markup Reverso: Preço = (Custos Fixos + Custo Produto) / (1 - %Imposto - %Comissão - %MargemAlvo)
        denominador = (1 - taxa_imposto - comissao_amazon - (margem_alvo/100))
        
        if denominador <= 0:
            st.error("A margem desejada é matematicamente impossível com essas taxas.")
            preco_sugerido = 0.0
        else:
            preco_sugerido = (custo_bruto + taxa_fixa_venda + frete_fba_fbm) / denominador

    if preco_sugerido > 0:
        res = calcular_metricas(preco_sugerido, custo_bruto)
        
        with col2:
            st.subheader("Resultado da Estratégia")
            m1, m2, m3 = st.columns(3)
            m1.metric("Preço Sugerido", f"R$ {preco_sugerido:.2f}")
            m2.metric("Lucro Líquido", f"R$ {res['lucro']:.2f}")
            m3.metric("ROI", f"{res['roi']:.1f}%")
            
            # Gráfico de Pizza
            fig = go.Figure(data=[go.Pie(
                labels=['Custo Produto', 'Comissão Amazon', 'Imposto', 'Logística/Taxas', 'Lucro Líquido'],
                values=[custo_bruto, res['v_comissao'], res['v_imposto'], res['custos_fixos'], res['lucro']],
                hole=.4,
                marker_colors=['#E5E5E5', '#FF9900', '#34495E', '#BDC3C7', '#2ECC71']
            )])
            fig.update_layout(title_text="Composição do Preço de Venda")
            st.plotly_chart(fig, use_container_width=True)

# --- TAB 2: SIMULADOR DE CENÁRIOS ---
with tab2:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Simular Venda")
        custo_sim = st.number_input("Custo do Produto (NF-e)", min_value=0.01, value=50.0, key="c2")
        preco_sim = st.number_input("Preço de Venda Pretendido", min_value=0.01, value=120.0)
        
        res_sim = calcular_metricas(preco_sim, custo_sim)

    with col2:
        st.subheader("Análise de Viabilidade")
        s1, s2, s3 = st.columns(3)
        
        cor_lucro = "normal" if res_sim['lucro'] > 0 else "inverse"
        s1.metric("Lucro Líquido", f"R$ {res_sim['lucro']:.2f}", delta=f"{res_sim['margem']:.1f}% Margem")
        s2.metric("ROI", f"{res_sim['roi']:.1f}%")
        s3.metric("Break-even (Custo Total)", f"R$ {(preco_sim - res_sim['lucro']):.2f}")
        
        if res_sim['lucro'] < 0:
            st.error("⚠️ Este cenário resulta em PREJUÍZO.")
        elif res_sim['margem'] < 10:
            st.warning("⚠️ Margem muito baixa para a operação Amazon (risco de variação de frete).")
        else:
            st.success("✅ Cenário lucrativo e saudável.")

        # Detalhamento em Tabela
        st.markdown("---")
        st.write("**Detalhamento de Saídas (R$):**")
        st.json({
            "Preço de Venda": round(preco_sim, 2),
            "(-) Custo de Aquisição": round(custo_sim, 2),
            "(-) Comissão Amazon": round(res_sim['v_comissao'], 2),
            "(-) Imposto": round(res_sim['v_imposto'], 2),
            "(-) Frete/Taxa Fixa": round(res_sim['custos_fixos'], 2),
            "(=) Resultado Final": round(res_sim['lucro'], 2)
        })

# Rodapé
st.divider()
st.caption(f"App desenvolvido para uso exclusivo de Sócios. Versão 1.0 - Amazon Brasil.")
