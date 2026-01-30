import streamlit as st
import pandas as pd
import io
import zipfile
import motor_nfe
import motor_nfse

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="PORTAL TAX CENTER", page_icon="💎", layout="wide")

if "mundo" not in st.session_state: 
    st.session_state.mundo = "NFe"

# --- 2. CSS ESTILO DIVISOR DE CADERNO ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;800&family=Plus+Jakarta+Sans:wght@400;700&display=swap');
    
    header, [data-testid="stHeader"] {{ display: none !important; }}
    
    /* Fundo original preservado */
    .stApp {{ background: radial-gradient(circle at top right, #FFDEEF 0%, #F8F9FA 100%) !important; }}

    /* Estilo dos Botões como Abas de Caderno */
    .stButton > button {{
        border-radius: 15px 15px 0 0 !important; /* Arredondado só em cima */
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 800 !important; 
        height: 50px !important; 
        text-transform: uppercase; 
        width: 100%;
        margin-bottom: -2px !important; /* Encosta na linha */
        transition: all 0.3s ease !important;
        border: 1px solid #DEE2E6 !important;
        background-color: rgba(255, 255, 255, 0.5) !important;
        color: #6C757D !important;
    }}

    /* Aba Ativa (Mundo Selecionado) */
    .aba-ativa > div > button {{
        background-color: #FFFFFF !important;
        color: #FF69B4 !important;
        border: 1px solid #FF69B4 !important;
        border-bottom: 2px solid #FFFFFF !important; /* Apaga a linha embaixo */
        box-shadow: 0 -4px 10px rgba(255, 105, 180, 0.1) !important;
        z-index: 10;
    }}
    
    .stButton > button:hover {{ 
        color: #FF69B4 !important; 
    }}

    /* Linha Divisora (Folha de Caderno) */
    .linha-caderno {{
        border-bottom: 2px solid #FF69B4;
        margin-top: -2px;
        margin-bottom: 30px;
        width: 100%;
    }}

    .instrucoes-card {{ background-color: rgba(255, 255, 255, 0.7); border-radius: 15px; padding: 20px; border-left: 5px solid #FF69B4; margin-bottom: 20px; min-height: 250px; }}
    h1, h2, h3 {{ font-family: 'Montserrat', sans-serif; font-weight: 800 !important; color: #FF69B4 !important; text-align: center; }}
    
    [data-testid="stFileUploader"] {{ border: 2px dashed #FF69B4 !important; border-radius: 20px !important; background: #FFFFFF !important; padding: 20px !important; }}
    section[data-testid="stFileUploader"] button, div.stDownloadButton > button {{ background-color: #FF69B4 !important; color: white !important; font-weight: 700 !important; border-radius: 15px !important; }}
    [data-testid="stSidebar"] {{ background-color: #FFFFFF !important; border-right: 1px solid #FFDEEF !important; min-width: 400px !important; }}
    </style>
""", unsafe_allow_html=True)

# --- 3. SISTEMA DE NAVEGAÇÃO (ABAS DE CADERNO) ---
_, col_btn1, col_btn2, _ = st.columns([1.5, 1, 1, 1.5])

with col_btn1:
    if st.session_state.mundo == "NFe":
        st.markdown('<div class="aba-ativa">', unsafe_allow_html=True)
    if st.button("💎 PORTAL TAX NF-e"):
        st.session_state.mundo = "NFe"
        st.rerun()
    if st.session_state.mundo == "NFe":
        st.markdown('</div>', unsafe_allow_html=True)

with col_btn2:
    if st.session_state.mundo == "NFSe":
        st.markdown('<div class="aba-ativa">', unsafe_allow_html=True)
    if st.button("📑 PORTAL TAX NFS-e"):
        st.session_state.mundo = "NFSe"
        st.rerun()
    if st.session_state.mundo == "NFSe":
        st.markdown('</div>', unsafe_allow_html=True)

# Linha que conecta as abas
st.markdown('<div class="linha-caderno"></div>', unsafe_allow_html=True)

# ==========================================
# MUNDO 1: NF-e (MATRIZ FISCAL)
# ==========================================
if st.session_state.mundo == "NFe":
    st.markdown("<style>[data-testid='stSidebar'] { display: block !important; }</style>", unsafe_allow_html=True)
    st.markdown("<h1>💎 MATRIZ FISCAL</h1>", unsafe_allow_html=True)
    
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.markdown('<div class="instrucoes-card"><h3>📖 Manual de Uso</h3><ol><li><b>Configuração:</b> Informe o CNPJ na lateral para liberar o painel.</li><li><b>Upload:</b> Arraste arquivos XML ou ZIP para o campo rosa.</li><li><b>Processamento:</b> Extração automática das 34 colunas.</li></ol></div>', unsafe_allow_html=True)
    with m_col2:
        st.markdown('<div class="instrucoes-card"><h3>🎯 Dados Obtidos</h3><ul><li><b>Mapeamento Total:</b> 34 colunas fiscais extraídas.</li><li><b>Reforma 2026:</b> Tags de IBS, CBS e CLClass incluídas.</li><li><b>Inteligência:</b> Separação automática entre Entradas e Saídas.</li></ul></div>', unsafe_allow_html=True)

    if 'lib_nfe' not in st.session_state: st.session_state.lib_nfe = False
    
    with st.sidebar:
        st.markdown("### 🔍 Configuração")
        cnpj = st.text_input("CNPJ DO CLIENTE", placeholder="00.000.000/0001-00")
        cnpj_l = "".join(filter(str.isdigit, cnpj))
        if len(cnpj_l) == 14:
            if st.button("✅ LIBERAR OPERAÇÃO"): st.session_state.lib_nfe = True
        st.divider()
        if st.button("🗑️ RESETAR SISTEMA"):
            st.session_state.lib_nfe = False
            st.rerun()

    if st.session_state.lib_nfe:
        st.info(f"🏢 Empresa Liberada: {cnpj_l}")
        f_nfe = st.file_uploader("Arraste seus arquivos XML ou ZIP aqui", type=["xml", "zip"], accept_multiple_files=True, key="up_nfe")
        if st.button("🚀 PROCESSAR MATRIZ FISCAL"):
            dados_nfe = []
            with st.spinner("💎 Rihanna Style: Brilhando nos dados..."):
                for f in f_nfe:
                    if f.name.endswith('.zip'):
                        with zipfile.ZipFile(f) as z:
                            for n in z.namelist():
                                if n.lower().endswith('.xml'): motor_nfe.ler_xml_nfe(z.read(n), dados_nfe, cnpj_l)
                    else: motor_nfe.ler_xml_nfe(f.read(), dados_nfe, cnpj_l)
            if dados_nfe:
                df_nfe = pd.DataFrame(dados_nfe)
                out_nfe = io.BytesIO()
                with pd.ExcelWriter(out_nfe, engine='xlsxwriter') as writer:
                    df_nfe.to_excel(writer, index=False)
                st.success(f"✨ Sucesso! {len(df_nfe)} itens organizados.")
                st.download_button("📥 BAIXAR MATRIZ DIAMANTE", out_nfe.getvalue(), f"matriz_{cnpj_l}.xlsx")
    else: st.warning("👈 Insira o CNPJ na barra lateral e clique em 'Liberar Operação' para começar.")

# ==========================================
# MUNDO 2: NFS-e (AUDITORIA FISCAL)
# ==========================================
else:
    st.markdown("<style>[data-testid='stSidebar'], [data-testid='stSidebarCollapsedControl'] { display: none !important; }</style>", unsafe_allow_html=True)
    st.markdown("<h1>PORTAL TAX NFS-e - AUDITORIA FISCAL</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="instrucoes-card"><h3>📖 Passo a Passo</h3><ol><li><b>Upload:</b> Arraste arquivos <b>.XML</b> ou <b>.ZIP</b> abaixo.</li><li><b>Ação:</b> Clique em <b>"INICIAR AUDITORIA"</b>.</li><li><b>Conferência:</b> Analise o <b>Diagnóstico</b> de divergências.</li><li><b>Saída:</b> Baixe o Excel final para auditoria.</li></ol></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="instrucoes-card"><h3>📊 O que será obtido?</h3><ul><li><b>Leitura Universal:</b> Dados de centenas de prefeituras consolidados.</li><li><b>Gestão de ISS:</b> Separação entre ISS Próprio e Retido.</li><li><b>Impostos Federais:</b> Captura de PIS, COFINS, CSLL e IRRF.</li><li><b>Diagnóstico:</b> Identificação de notas com retenções pendentes.</li></ul></div>', unsafe_allow_html=True)

    f_nfse = st.file_uploader("Arraste os arquivos XML ou ZIP aqui", type=["xml", "zip"], accept_multiple_files=True, key="up_nfse")
    
    if f_nfse and st.button("🚀 INICIAR AUDITORIA FISCAL"):
        dados_nfse = []
        with st.spinner("Processando..."):
            for f in f_nfse:
                if f.name.endswith('.zip'):
                    with zipfile.ZipFile(f) as z:
                        for n in z.namelist():
                            if n.lower().endswith('.xml'):
                                r = motor_nfse.process_xml_file_nfse(z.read(n), n)
                                if r: dados_nfse.append(r)
                else:
                    r = motor_nfse.process_xml_file_nfse(f.read(), f.name)
                    if r: dados_nfse.append(r)
        
        if dados_nfse:
            df_nfse = pd.DataFrame(dados_nfse)
            cols_fin = ['Vlr_Bruto', 'Vlr_Liquido', 'ISS_Valor', 'Ret_ISS', 'Ret_PIS', 'Ret_COFINS', 'Ret_CSLL', 'Ret_IRRF']
            for c in cols_fin: df_nfse[c] = pd.to_numeric(df_nfse[c], errors='coerce').fillna(0.0)
            df_nfse['Diagnostico'] = df_nfse.apply(lambda r: "⚠️ Divergência!" if abs(r['Vlr_Bruto'] - r['Vlr_Liquido']) > 0.01 else "✅", axis=1)
            
            st.success(f"✅ {len(df_nfse)} notas processadas!")
            st.dataframe(df_nfse)
            
            out_nfse = io.BytesIO()
            with pd.ExcelWriter(out_nfse, engine='xlsxwriter') as writer:
                df_nfse.to_excel(writer, index=False, sheet_name='PortalServTax')
            st.download_button("📥 BAIXAR EXCEL AJUSTADO", out_nfse.getvalue(), "portal_servtax_auditoria.xlsx")
