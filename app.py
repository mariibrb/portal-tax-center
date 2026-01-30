import streamlit as st
import pandas as pd
import io
import zipfile
from motor_nfe import ler_xml_nfe
from motor_nfse import process_xml_file_nfse

# --- CONFIGURAÇÃO GLOBAL ---
st.set_page_config(page_title="PORTAL TAX CENTER", page_icon="💎", layout="wide")

# --- CSS BASE (UI UNIFICADA) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;800&family=Plus+Jakarta+Sans:wght@400;700&display=swap');
    
    /* Remove o cabeçalho padrão do Streamlit */
    header, [data-testid="stHeader"] { display: none !important; }
    
    .stApp { background: radial-gradient(circle at top right, #FFDEEF 0%, #F8F9FA 100%) !important; }
    
    /* ESTILO DAS TABS */
    .stTabs [data-baseweb="tab"] {
        height: 60px; background-color: #FFFFFF !important; border-radius: 15px 15px 0px 0px !important;
        border: 1px solid #DEE2E6 !important; font-family: 'Montserrat', sans-serif !important;
        font-weight: 800 !important; color: #6C757D !important; padding: 10px 30px !important;
    }
    .stTabs [aria-selected="true"] { background-color: #FF69B4 !important; color: white !important; border-color: #FF69B4 !important; }
    
    /* SIDEBAR PADRÃO */
    [data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #FFDEEF !important; min-width: 350px !important; }
    
    /* BOTÕES */
    div.stButton > button {
        color: #6C757D !important; background-color: #FFFFFF !important; border: 1px solid #DEE2E6 !important;
        border-radius: 15px !important; font-family: 'Montserrat', sans-serif !important;
        font-weight: 800 !important; height: 60px !important; text-transform: uppercase;
        width: 100%; transition: all 0.4s ease !important;
    }
    div.stButton > button:hover { transform: translateY(-5px) !important; border-color: #FF69B4 !important; color: #FF69B4 !important; }
    
    /* UPLOADER E DOWNLOADER */
    [data-testid="stFileUploader"] { border: 2px dashed #FF69B4 !important; border-radius: 20px !important; background: #FFFFFF !important; padding: 20px !important; }
    section[data-testid="stFileUploader"] button, div.stDownloadButton > button {
        background-color: #FF69B4 !important; color: white !important; font-weight: 700 !important; border-radius: 15px !important; text-transform: uppercase; width: 100% !important;
    }
    
    h1, h2, h3 { font-family: 'Montserrat', sans-serif; font-weight: 800 !important; color: #FF69B4 !important; text-align: center; }
    .instrucoes-card { background-color: rgba(255, 255, 255, 0.7); border-radius: 15px; padding: 20px; border-left: 5px solid #FF69B4; margin-bottom: 20px; min-height: 250px; }
    </style>
""", unsafe_allow_html=True)

# --- NAVEGAÇÃO POR ABAS ---
tab_nfe, tab_nfse = st.tabs(["💎 PORTAL TAX NF-e", "📑 PORTAL TAX NFS-e"])

# ==========================================
# ABA NF-e (A SIDEBAR DEVE APARECER AQUI)
# ==========================================
with tab_nfe:
    # FORÇA A EXIBIÇÃO DA SIDEBAR
    st.markdown("""
        <style>
            [data-testid="stSidebar"] { display: block !important; }
            [data-testid="stSidebarCollapsedControl"] { display: block !important; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1>💎 MATRIZ FISCAL NF-e</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: st.markdown('<div class="instrucoes-card"><h3>📖 Manual NF-e</h3><ol><li>Insira o CNPJ na lateral.</li><li>Arraste os arquivos.</li><li>Obtenha as 34 colunas.</li></ol></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="instrucoes-card"><h3>🎯 Reforma 2026</h3><ul><li>Tags IBS/CBS.</li><li>Entradas e Saídas.</li><li>Mapeamento Total.</li></ul></div>', unsafe_allow_html=True)
    
    if 'lib_nfe' not in st.session_state: st.session_state['lib_nfe'] = False
    
    with st.sidebar:
        st.markdown("### 🔍 Configuração NF-e")
        cnpj_in = st.text_input("CNPJ DO CLIENTE", key="in_nfe")
        cnpj_l = "".join(filter(str.isdigit, cnpj_in))
        if len(cnpj_l) == 14:
            if st.button("✅ LIBERAR OPERAÇÃO"): st.session_state['lib_nfe'] = True
        st.divider()
        if st.button("🗑️ RESETAR NF-e"):
            st.session_state['lib_nfe'] = False
            st.rerun()

    if st.session_state['lib_nfe']:
        st.info(f"🏢 Operando CNPJ: {cnpj_l}")
        files = st.file_uploader("Arquivos NF-e (XML ou ZIP)", type=["xml", "zip"], accept_multiple_files=True, key="u_nfe")
        if st.button("🚀 PROCESSAR MATRIZ NF-e"):
            res_nfe = []
            with st.spinner("Brilhando nos dados..."):
                for f in files:
                    if f.name.endswith('.zip'):
                        with zipfile.ZipFile(f) as z:
                            for n in z.namelist():
                                if n.lower().endswith('.xml'): ler_xml_nfe(z.read(n), res_nfe, cnpj_l)
                    else: ler_xml_nfe(f.read(), res_nfe, cnpj_l)
            if res_nfe:
                df = pd.DataFrame(res_nfe)
                out = io.BytesIO()
                df.to_excel(out, index=False, engine='xlsxwriter')
                st.success(f"✨ {len(df)} itens processados!")
                st.download_button("📥 BAIXAR MATRIZ DIAMANTE", out.getvalue(), f"matriz_{cnpj_l}.xlsx")
    else: st.warning("👈 Insira o CNPJ na lateral para começar.")

# ==========================================
# ABA NFS-e (A SIDEBAR DEVE SUMIR AQUI)
# ==========================================
with tab_nfse:
    # FORÇA O OCULTAMENTO DA SIDEBAR
    st.markdown("""
        <style>
            [data-testid="stSidebar"] { display: none !important; }
            [data-testid="stSidebarCollapsedControl"] { display: none !important; }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<h1>📑 PORTAL TAX NFS-e</h1>", unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3: st.markdown('<div class="instrucoes-card"><h3>📖 Manual NFS-e</h3><ol><li>Arraste os arquivos XML/ZIP.</li><li>Clique em Auditoria.</li><li>Analise o Diagnóstico.</li></ol></div>', unsafe_allow_html=True)
    with c4: st.markdown('<div class="instrucoes-card"><h3>📊 Diagnóstico</h3><ul><li>ISS Próprio vs Retido.</li><li>Retenções Federais.</li><li>Universalidade Prefeituras.</li></ul></div>', unsafe_allow_html=True)
    
    files_s = st.file_uploader("Arquivos NFS-e (XML ou ZIP)", type=["xml", "zip"], accept_multiple_files=True, key="u_nfse")
    if files_s and st.button("🚀 INICIAR AUDITORIA NFS-e"):
        res_nfse = []
        with st.spinner("Auditando..."):
            for f in files_s:
                if f.name.endswith('.zip'):
                    with zipfile.ZipFile(f) as z:
                        for n in z.namelist():
                            if n.lower().endswith('.xml'):
                                r = process_xml_file_nfse(z.read(n), n)
                                if r: res_nfse.append(r)
                else:
                    r = process_xml_file_nfse(f.read(), f.name)
                    if r: res_nfse.append(r)
        if res_nfse:
            df_s = pd.DataFrame(res_nfse)
            cols_v = ['Vlr_Bruto', 'Vlr_Liquido', 'ISS_Valor', 'Ret_ISS', 'Ret_PIS', 'Ret_COFINS', 'Ret_CSLL', 'Ret_IRRF']
            for c in cols_v: df_s[c] = pd.to_numeric(df_s[c], errors='coerce').fillna(0.0)
            df_s['Diagnostico'] = df_s.apply(lambda r: "⚠️ Divergência!" if abs(r['Vlr_Bruto'] - r['Vlr_Liquido']) > 0.01 else "✅", axis=1)
            
            st.success(f"✅ {len(df_s)} notas auditadas!")
            st.dataframe(df_s)
            
            out_s = io.BytesIO()
            df_s.to_excel(out_s, index=False)
            st.download_button("📥 BAIXAR AUDITORIA EXCEL", out_s.getvalue(), "auditoria_nfse.xlsx")
