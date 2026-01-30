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

# --- 2. DEFINIÇÃO DE CORES POR MUNDO ---
if st.session_state.mundo == "NFe":
    cor_tema = "#FF69B4"  # Rosa Rihanna
    cor_fundo_card = "rgba(255, 105, 180, 0.1)"
    label_mundo = "💎 MODO MATRIZ FISCAL (NF-e)"
    btn_nfe_css = "border: 3px solid #FF69B4 !important; background-color: #FFF0F5 !important; color: #FF69B4 !important;"
    btn_nfse_css = "border: 1px solid #DEE2E6 !important; background-color: #FFFFFF !important; color: #6C757D !important;"
else:
    cor_tema = "#C71585"  # Rosa Choque/Médio
    cor_fundo_card = "rgba(199, 21, 133, 0.1)"
    label_mundo = "📑 MODO AUDITORIA FISCAL (NFS-e)"
    btn_nfse_css = "border: 3px solid #C71585 !important; background-color: #FFF0F5 !important; color: #C71585 !important;"
    btn_nfe_css = "border: 1px solid #DEE2E6 !important; background-color: #FFFFFF !important; color: #6C757D !important;"

# --- 3. CSS UNIFICADO E DINÂMICO ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;800&family=Plus+Jakarta+Sans:wght@400;700&display=swap');
    
    header, [data-testid="stHeader"] {{ display: none !important; }}
    
    .stApp {{ background-color: #F8F9FA !important; }}

    /* Banner de Identificação do Mundo */
    .mundo-banner {{
        background-color: {cor_tema};
        color: white;
        text-align: center;
        padding: 10px;
        font-family: 'Montserrat', sans-serif;
        font-weight: 800;
        font-size: 1.2rem;
        border-radius: 0 0 20px 20px;
        margin-bottom: 30px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }}
    
    /* Botões do Porteiro */
    div[data-testid="column"]:nth-of-type(2) button {{ {btn_nfe_css} }}
    div[data-testid="column"]:nth-of-type(4) button {{ {btn_nfse_css} }}

    .stButton > button {{
        border-radius: 15px !important; 
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 800 !important; 
        height: 55px !important; 
        text-transform: uppercase; 
        width: 100%;
        transition: all 0.2s ease !important;
    }}

    .instrucoes-card {{ 
        background-color: white; 
        border-radius: 15px; 
        padding: 20px; 
        border-left: 8px solid {cor_tema}; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px; 
        min-height: 250px; 
    }}

    h1, h2, h3 {{ font-family: 'Montserrat', sans-serif; font-weight: 800 !important; color: {cor_tema} !important; }}
    
    [data-testid="stFileUploader"] {{ border: 2px dashed {cor_tema} !important; border-radius: 20px !important; background: #FFFFFF !important; }}
    section[data-testid="stFileUploader"] button, div.stDownloadButton > button {{ background-color: {cor_tema} !important; color: white !important; font-weight: 700 !important; border-radius: 15px !important; }}
    [data-testid="stSidebar"] {{ background-color: #FFFFFF !important; border-right: 1px solid #DEE2E6 !important; min-width: 400px !important; }}
    </style>
    
    <div class="mundo-banner">{label_mundo}</div>
""", unsafe_allow_html=True)

# --- 4. SISTEMA DE NAVEGAÇÃO ---
_, col_btn1, espaco, col_btn2, _ = st.columns([2, 1, 0.1, 1, 2])

with col_btn1:
    if st.button("💎 PORTAL TAX NF-e"):
        st.session_state.mundo = "NFe"
        st.rerun()

with col_btn2:
    if st.button("📑 PORTAL TAX NFS-e"):
        st.session_state.mundo = "NFSe"
        st.rerun()

st.markdown("---")

# ==========================================
# MUNDO 1: NF-e (MATRIZ FISCAL)
# ==========================================
if st.session_state.mundo == "NFe":
    st.markdown("<style>[data-testid='stSidebar'] { display: block !important; }</style>", unsafe_allow_html=True)
    st.markdown(f"<h1>💎 MATRIZ FISCAL</h1>", unsafe_allow_html=True)
    
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
        f_nfe = st.file_uploader("Arraste seus arquivos XML ou ZIP aqui", type=["xml", "zip"], accept_multiple_files=True, key="up_nfe")
        if st.button("🚀 PROCESSAR MATRIZ FISCAL"):
            dados_nfe = []
            with st.spinner("Processando Matriz..."):
                for f in f_nfe:
                    if f.name.endswith('.zip'):
                        with zipfile.ZipFile(f) as z:
                            for n in z.namelist():
                                if n.lower().endswith('.xml'): motor_nfe.ler_xml_nfe(z.read(n), dados_nfe, cnpj_l)
                    else: motor_nfe.ler_xml_nfe(f.read(), dados_nfe, cnpj_l)
            if dados_nfe:
                df_nfe = pd.DataFrame(dados_nfe)
                out_nfe = io.BytesIO()
                df_nfe.to_excel(out_nfe, index=False)
                st.success(f"✨ Sucesso! {len(df_nfe)} itens organizados.")
                st.download_button("📥 BAIXAR MATRIZ DIAMANTE", out_nfe.getvalue(), f"matriz_{cnpj_l}.xlsx")
    else: st.warning("👈 Insira o CNPJ na lateral.")

# ==========================================
# MUNDO 2: NFS-e (AUDITORIA FISCAL)
# ==========================================
else:
    st.markdown("<style>[data-testid='stSidebar'], [data-testid='stSidebarCollapsedControl'] { display: none !important; }</style>", unsafe_allow_html=True)
    st.markdown(f"<h1>PORTAL TAX NFS-e - AUDITORIA FISCAL</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="instrucoes-card"><h3>📖 Passo a Passo</h3><ol><li><b>Upload:</b> Arraste arquivos <b>.XML</b> ou <b>.ZIP</b> abaixo.</li><li><b>Ação:</b> Clique em <b>"INICIAR AUDITORIA"</b>.</li><li><b>Conferência:</b> Analise o <b>Diagnóstico</b> de divergências.</li><li><b>Saída:</b> Baixe o Excel final para auditoria.</li></ol></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="instrucoes-card"><h3>📊 O que será obtido?</h3><ul><li><b>Leitura Universal:</b> Dados de centenas de prefeituras consolidados.</li><li><b>Gestão de ISS:</b> Separação entre ISS Próprio e Retido.</li><li><b>Impostos Federais:</b> Captura de PIS, COFINS, CSLL e IRRF.</li><li><b>Diagnóstico:</b> Identificação de notas com retenções pendentes.</li></ul></div>', unsafe_allow_html=True)

    f_nfse = st.file_uploader("Arraste os arquivos XML ou ZIP aqui", type=["xml", "zip"], accept_multiple_files=True, key="up_nfse")
    if f_nfse and st.button("🚀 INICIAR AUDITORIA FISCAL"):
        dados_nfse = []
        with st.spinner("Auditando NFS-e..."):
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
            # Reuso da lógica de processamento numérico
            c_v = ['Vlr_Bruto', 'Vlr_Liquido', 'ISS_Valor', 'Ret_ISS', 'Ret_PIS', 'Ret_COFINS', 'Ret_CSLL', 'Ret_IRRF']
            for c in c_v: df_nfse[c] = pd.to_numeric(df_nfse[c], errors='coerce').fillna(0.0)
            df_nfse['Diagnostico'] = df_nfse.apply(lambda r: "⚠️ Divergência!" if abs(r['Vlr_Bruto'] - r['Vlr_Liquido']) > 0.01 else "✅", axis=1)
            st.success(f"✅ {len(df_nfse)} notas processadas!")
            st.dataframe(df_nfse)
            out_nfse = io.BytesIO()
            df_nfse.to_excel(out_nfse, index=False)
            st.download_button("📥 BAIXAR EXCEL AJUSTADO", out_nfse.getvalue(), "portal_servtax_auditoria.xlsx")
