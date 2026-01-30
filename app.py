import streamlit as st
import pandas as pd
import io
import zipfile
# Importando os motores independentes
import motor_nfe
import motor_nfse

# 1. SETUP DE PÁGINA (Deve ser o primeiro comando)
st.set_page_config(page_title="PORTAL TAX CENTER", page_icon="💎", layout="wide")

# 2. ESTILO GLOBAL RIHANNA (BASE)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;800&family=Plus+Jakarta+Sans:wght@400;700&display=swap');
    header, [data-testid="stHeader"] { display: none !important; }
    .stApp { background: radial-gradient(circle at top right, #FFDEEF 0%, #F8F9FA 100%) !important; }
    
    /* Estilo dos Botões do Menu Superior */
    div.stButton > button {
        color: #6C757D !important; background-color: #FFFFFF !important; border: 1px solid #DEE2E6 !important;
        border-radius: 15px !important; font-family: 'Montserrat', sans-serif !important;
        font-weight: 800 !important; height: 50px !important; text-transform: uppercase; width: 100%;
    }
    div.stButton > button:hover { border-color: #FF69B4 !important; color: #FF69B4 !important; transform: translateY(-3px); }
    
    .instrucoes-card { background-color: rgba(255, 255, 255, 0.7); border-radius: 15px; padding: 20px; border-left: 5px solid #FF69B4; margin-bottom: 20px; min-height: 250px; }
    h1, h2, h3 { font-family: 'Montserrat', sans-serif; font-weight: 800 !important; color: #FF69B4 !important; text-align: center; }
    [data-testid="stFileUploader"] { border: 2px dashed #FF69B4 !important; border-radius: 20px !important; background: #FFFFFF !important; padding: 20px !important; }
    section[data-testid="stFileUploader"] button, div.stDownloadButton > button { background-color: #FF69B4 !important; color: white !important; font-weight: 700 !important; }
    </style>
""", unsafe_allow_html=True)

# 3. NAVEGAÇÃO SUPERIOR (INTERRUPTOR DE MUNDOS)
c1, c2, _ = st.columns([1, 1, 2])
if "mundo" not in st.session_state: st.session_state.mundo = "NF-e"

with c1:
    if st.button("💎 PORTAL TAX NF-e"): 
        st.session_state.mundo = "NF-e"
        st.rerun()
with c2:
    if st.button("📑 PORTAL TAX NFS-e"): 
        st.session_state.mundo = "NFS-e"
        st.rerun()

st.markdown("---")

# ==========================================
# LÓGICA DO MUNDO NF-e (COM SIDEBAR)
# ==========================================
if st.session_state.mundo == "NF-e":
    # FORÇA A SIDEBAR A APARECER
    st.markdown("<style>[data-testid='stSidebar'] { display: block !important; }</style>", unsafe_allow_html=True)
    
    st.markdown("<h1>💎 MATRIZ FISCAL NF-e</h1>", unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("### 🔍 Configuração NF-e")
        cnpj = st.text_input("CNPJ DO CLIENTE", key="cnpj_nfe")
        cnpj_l = "".join(filter(str.isdigit, cnpj))
        if len(cnpj_l) == 14:
            if st.button("✅ LIBERAR OPERAÇÃO"): st.session_state.lib_nfe = True
        st.divider()
        if st.button("🗑️ RESETAR"):
            st.session_state.lib_nfe = False
            st.rerun()

    if st.session_state.get('lib_nfe'):
        st.info(f"🏢 Operando CNPJ: {cnpj_l}")
        files = st.file_uploader("Arquivos NF-e", type=["xml", "zip"], accept_multiple_files=True)
        if st.button("🚀 PROCESSAR MATRIZ"):
            res = []
            for f in files:
                if f.name.endswith('.zip'):
                    with zipfile.ZipFile(f) as z:
                        for n in z.namelist():
                            if n.lower().endswith('.xml'): motor_nfe.ler_xml_nfe(z.read(n), res, cnpj_l)
                else: motor_nfe.ler_xml_nfe(f.read(), res, cnpj_l)
            if res:
                df = pd.DataFrame(res)
                out = io.BytesIO()
                df.to_excel(out, index=False)
                st.download_button("📥 BAIXAR MATRIZ", out.getvalue(), f"matriz_{cnpj_l}.xlsx")
    else:
        st.warning("👈 Insira o CNPJ na lateral.")

# ==========================================
# LÓGICA DO MUNDO NFS-e (SEM SIDEBAR)
# ==========================================
else:
    # FORÇA A SIDEBAR A SUMIR COMPLETAMENTE
    st.markdown("<style>[data-testid='stSidebar'], [data-testid='stSidebarCollapsedControl'] { display: none !important; }</style>", unsafe_allow_html=True)
    
    st.markdown("<h1>📑 PORTAL TAX NFS-e</h1>", unsafe_allow_html=True)
    
    files_s = st.file_uploader("Arquivos NFS-e", type=["xml", "zip"], accept_multiple_files=True)
    if files_s and st.button("🚀 INICIAR AUDITORIA"):
        res_s = []
        for f in files_s:
            if f.name.endswith('.zip'):
                with zipfile.ZipFile(f) as z:
                    for n in z.namelist():
                        if n.lower().endswith('.xml'):
                            r = motor_nfse.process_xml_file_nfse(z.read(n), n)
                            if r: res_s.append(r)
            else:
                r = motor_nfse.process_xml_file_nfse(f.read(), f.name)
                if r: res_s.append(r)
        if res_s:
            df_s = pd.DataFrame(res_s)
            st.dataframe(df_s)
            out_s = io.BytesIO()
            df_s.to_excel(out_s, index=False)
            st.download_button("📥 BAIXAR AUDITORIA", out_s.getvalue(), "auditoria.xlsx")
