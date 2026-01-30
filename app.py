import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
import io
import zipfile
import re

# --- CONFIGURAÇÃO GLOBAL ---
st.set_page_config(
    page_title="PORTAL TAX CENTER",
    page_icon="💎",
    layout="wide"
)

# --- CSS PREMIUM UNIFICADO ---
def aplicar_estilo_premium():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;800&family=Plus+Jakarta+Sans:wght@400;700&display=swap');

        header, [data-testid="stHeader"] { display: none !important; }
        
        .stApp { 
            background: radial-gradient(circle at top right, #FFDEEF 0%, #F8F9FA 100%) !important; 
        }

        /* ESTILO DAS TABS */
        .stTabs [data-baseweb="tab-list"] {
            gap: 20px;
            justify-content: center;
        }

        .stTabs [data-baseweb="tab"] {
            height: 60px;
            background-color: #FFFFFF !important;
            border-radius: 15px 15px 0px 0px !important;
            border: 1px solid #DEE2E6 !important;
            font-family: 'Montserrat', sans-serif !important;
            font-weight: 800 !important;
            color: #6C757D !important;
            padding: 10px 30px !important;
        }

        .stTabs [aria-selected="true"] {
            background-color: #FF69B4 !important;
            color: white !important;
            border-color: #FF69B4 !important;
        }

        /* SIDEBAR */
        [data-testid="stSidebar"] {
            background-color: #FFFFFF !important;
            border-right: 1px solid #FFDEEF !important;
            min-width: 380px !important;
        }

        div.stButton > button {
            color: #6C757D !important; 
            background-color: #FFFFFF !important; 
            border: 1px solid #DEE2E6 !important;
            border-radius: 15px !important;
            font-family: 'Montserrat', sans-serif !important;
            font-weight: 800 !important;
            height: 60px !important;
            text-transform: uppercase;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        }

        div.stButton > button:hover {
            transform: translateY(-5px) !important;
            box-shadow: 0 10px 20px rgba(255,105,180,0.2) !important;
            border-color: #FF69B4 !important;
            color: #FF69B4 !important;
        }

        [data-testid="stFileUploader"] { 
            border: 2px dashed #FF69B4 !important; 
            border-radius: 20px !important;
            background: #FFFFFF !important;
            padding: 20px !important;
        }

        section[data-testid="stFileUploader"] button, div.stDownloadButton > button {
            background-color: #FF69B4 !important;
            color: white !important;
            border: 2px solid #FFFFFF !important;
            font-weight: 700 !important;
            border-radius: 15px !important;
            box-shadow: 0 0 15px rgba(255, 105, 180, 0.3) !important;
            text-transform: uppercase;
            width: 100% !important;
        }

        h1, h2, h3 {
            font-family: 'Montserrat', sans-serif;
            font-weight: 800 !important;
            color: #FF69B4 !important;
            text-align: center;
        }

        .instrucoes-card {
            background-color: rgba(255, 255, 255, 0.7);
            border-radius: 15px;
            padding: 20px;
            border-left: 5px solid #FF69B4;
            margin-bottom: 20px;
            min-height: 250px;
        }
        </style>
    """, unsafe_allow_html=True)

aplicar_estilo_premium()

# --- MOTORES DE PROCESSAMENTO (INTEGROS) ---

# --- Módulo NFS-e ---
def get_xml_value_nfse(root, tags):
    for tag in tags:
        element = root.find(f".//{{*}}{tag}")
        if element is None: element = root.find(f".//{tag}")
        if element is not None and element.text: return element.text.strip()
    return "0.00" if any(x in tag.lower() for x in ['vlr', 'valor', 'iss', 'pis', 'cofins', 'ir', 'csll', 'liquido', 'trib']) else ""

def process_xml_file_nfse(content, filename):
    try:
        tree = ET.parse(io.BytesIO(content))
        root = tree.getroot()
        iss_retido_flag = get_xml_value_nfse(root, ['ISSRetido']).lower()
        tp_ret_flag = get_xml_value_nfse(root, ['tpRetISSQN'])
        row = {
            'Arquivo': filename,
            'Nota_Numero': get_xml_value_nfse(root, ['nNFSe', 'NumeroNFe', 'nNF', 'numero', 'Numero']),
            'Data_Emissao': get_xml_value_nfse(root, ['dhProc', 'dhEmi', 'DataEmissaoNFe', 'DataEmissao', 'dtEmi']),
            'Prestador_CNPJ': get_xml_value_nfse(root, ['emit/CNPJ', 'CPFCNPJPrestador/CNPJ', 'CNPJPrestador', 'emit_CNPJ', 'CPFCNPJPrestador/CPF', 'CNPJ']),
            'Prestador_Razao': get_xml_value_nfse(root, ['emit/xNome', 'RazaoSocialPrestador', 'xNomePrestador', 'emit_xNome', 'RazaoSocial', 'xNome']),
            'Tomador_CNPJ': get_xml_value_nfse(root, ['toma/CNPJ', 'CPFCNPJTomador/CNPJ', 'CPFCNPJTomador/CPF', 'dest/CNPJ', 'CNPJTomador', 'toma/CPF', 'tom/CNPJ', 'CNPJ']),
            'Tomador_Razao': get_xml_value_nfse(root, ['toma/xNome', 'RazaoSocialTomador', 'dest/xNome', 'xNomeTomador', 'RazaoSocialTomador', 'tom/xNome', 'xNome']),
            'Vlr_Bruto': get_xml_value_nfse(root, ['vServ', 'ValorServicos', 'vNF', 'vServPrest/vServ', 'ValorTotal']),
            'Vlr_Liquido': get_xml_value_nfse(root, ['vLiq', 'ValorLiquidoNFe', 'vLiqNFSe', 'vLiquido', 'vServPrest/vLiq']),
            'ISS_Valor': get_xml_value_nfse(root, ['vISS', 'ValorISS', 'vISSQN', 'iss/vISS']),
            'Ret_PIS': get_xml_value_nfse(root, ['vPIS', 'ValorPIS', 'vPIS_Ret', 'PISRetido', 'vRetPIS']),
            'Ret_COFINS': get_xml_value_nfse(root, ['vCOFINS', 'ValorCOFINS', 'vCOFINS_Ret', 'COFINSRetido', 'vRetCOFINS']),
            'Ret_CSLL': get_xml_value_nfse(root, ['vCSLL', 'ValorCSLL', 'vCSLL_Ret', 'CSLLRetido', 'vRetCSLL']),
            'Ret_IRRF': get_xml_value_nfse(root, ['vIR', 'ValorIR', 'vIR_Ret', 'IRRetido', 'vRetIR', 'vIRRF']),
            'Descricao': get_xml_value_nfse(root, ['CodigoServico', 'itemServico', 'cServ', 'xDescServ', 'Discriminacao', 'xServ', 'infCpl', 'xProd'])
        }
        if tp_ret_flag == '2' or iss_retido_flag == 'true':
             row['Ret_ISS'] = get_xml_value_nfse(root, ['vTotTribMun', 'vISSRetido', 'ValorISS_Retido', 'vRetISS', 'vISSRet', 'iss/vRet'])
        elif iss_retido_flag == 'false' or tp_ret_flag == '1':
             row['Ret_ISS'] = "0.00"
        else:
             row['Ret_ISS'] = get_xml_value_nfse(root, ['vTotTribMun', 'vISSRetido', 'ValorISS_Retido', 'vRetISS', 'vISSRet', 'iss/vRet'])
        return row
    except: return None

# --- Módulo NF-e ---
def safe_float(v):
    if v is None or pd.isna(v): return 0.0
    txt = str(v).strip().upper()
    if txt in ['NT', '', 'N/A', 'ISENTO', 'NULL', 'ZERO', '-', ' ']: return 0.0
    try:
        txt = txt.replace('R$', '').replace(' ', '').replace('%', '').strip()
        if ',' in txt and '.' in txt: txt = txt.replace('.', '').replace(',', '.')
        elif ',' in txt: txt = txt.replace(',', '.')
        return round(float(txt), 4)
    except: return 0.0

def buscar_tag(tag, no):
    if no is None: return ""
    for el in no.iter():
        if el.tag.split('}')[-1] == tag: return el.text if el.text else ""
    return ""

def ler_xml_nfe(content, dados_lista, cnpj_cliente):
    try:
        xml_str = re.sub(r'\sxmlns(:\w+)?="[^"]+"', '', content.decode('utf-8', errors='replace'))
        root = ET.fromstring(xml_str)
        inf = root.find('.//infNFe')
        if inf is None: return 
        ide, emit, dest = root.find('.//ide'), root.find('.//emit'), root.find('.//dest')
        cnpj_emit = re.sub(r'\D', '', buscar_tag('CNPJ', emit))
        tipo_op = "SAIDA" if (cnpj_emit == re.sub(r'\D', '', str(cnpj_cliente)) and buscar_tag('tpNF', ide) == '1') else "ENTRADA"

        for det in root.findall('.//det'):
            prod, imp = det.find('prod'), det.find('imposto')
            icms, ipi, pis, cof = det.find('.//ICMS'), det.find('.//IPI'), det.find('.//PIS'), det.find('.//COFINS')
            ibs, cbs = det.find('.//IBS'), det.find('.//CBS')
            orig = buscar_tag('orig', icms)
            cst_p = buscar_tag('CST', icms) or buscar_tag('CSOSN', icms)
            
            dados_lista.append({
                "CHAVE_ACESSO": inf.attrib.get('Id', '')[3:],
                "NUM_NF": buscar_tag('nNF', ide),
                "DATA_EMISSAO": buscar_tag('dhEmi', ide) or buscar_tag('dEmi', ide),
                "TIPO_SISTEMA": tipo_op, "CNPJ_EMIT": cnpj_emit, "UF_EMIT": buscar_tag('UF', emit),
                "CNPJ_DEST": re.sub(r'\D', '', buscar_tag('CNPJ', dest)), "UF_DEST": buscar_tag('UF', dest),
                "INDIEDEST": buscar_tag('indIEDest', dest), "CFOP": buscar_tag('CFOP', prod), "NCM": buscar_tag('NCM', prod),
                "VPROD": safe_float(buscar_tag('vProd', prod)), "ORIGEM": orig, "CST-ICMS": orig + cst_p if cst_p else orig,
                "BC-ICMS": safe_float(buscar_tag('vBC', icms)), "ALQ-ICMS": safe_float(buscar_tag('pICMS', icms)), "VLR-ICMS": safe_float(buscar_tag('vICMS', icms)),
                "VAL-ICMS-ST": safe_float(buscar_tag('vICMSST', icms)), "IE_SUBST": buscar_tag('IEST', icms),
                "VAL-DIFAL": safe_float(buscar_tag('vICMSUFDest', imp)) + safe_float(buscar_tag('vFCPUFDest', imp)),
                "CST-IPI": buscar_tag('CST', ipi), "ALQ-IPI": safe_float(buscar_tag('pIPI', ipi)), "VLR-IPI": safe_float(buscar_tag('vIPI', ipi)),
                "CST-PIS": buscar_tag('CST', pis), "VLR-PIS": safe_float(buscar_tag('vPIS', pis)),
                "CST-COFINS": buscar_tag('CST', cof), "VLR-COFINS": safe_float(buscar_tag('vCOFINS', cof)),
                "CLCLASS": buscar_tag('CLClass', prod) or buscar_tag('CLClass', imp),
                "CST-IBS": buscar_tag('CST', ibs), "BC-IBS": safe_float(buscar_tag('vBC', ibs)), "VLR-IBS": safe_float(buscar_tag('vIBS', ibs)),
                "CST-CBS": buscar_tag('CST', cbs), "BC-CBS": safe_float(buscar_tag('vBC', cbs)), "VLR-CBS": safe_float(buscar_tag('vCBS', cbs))
            })
    except: pass

# --- INTERFACE PRINCIPAL ---

tab_nfe, tab_nfse = st.tabs(["💎 PORTAL TAX NF-e", "📑 PORTAL TAX NFS-e"])

# --- ABA 1: NF-e (MATRIZ FISCAL) ---
with tab_nfe:
    st.markdown("<h1>💎 MATRIZ FISCAL NF-e</h1>", unsafe_allow_html=True)
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.markdown('<div class="instrucoes-card"><h3>📖 Manual de Uso</h3><ol><li>Insira o CNPJ na lateral para liberar.</li><li>Arraste arquivos XML ou ZIP.</li><li>Extração completa de 34 colunas.</li></ol></div>', unsafe_allow_html=True)
    with m_col2:
        st.markdown('<div class="instrucoes-card"><h3>🎯 Reforma 2026</h3><ul><li>Tags IBS e CBS processadas.</li><li>Identificação de Entradas/Saídas.</li><li>Mapeamento total de impostos.</li></ul></div>', unsafe_allow_html=True)

    if 'liberado_nfe' not in st.session_state: st.session_state['liberado_nfe'] = False

    with st.sidebar:
        st.markdown("### 🔍 Configuração NF-e")
        cnpj_in = st.text_input("CNPJ DO CLIENTE", key="cnpj_nfe")
        cnpj_l = "".join(filter(str.isdigit, cnpj_in))
        if len(cnpj_l) == 14:
            if st.button("✅ LIBERAR OPERAÇÃO"): st.session_state['liberado_nfe'] = True
        st.divider()
        if st.button("🗑️ RESETAR NF-e"):
            st.session_state['liberado_nfe'] = False
            st.rerun()

    if st.session_state['liberado_nfe']:
        st.info(f"🏢 Operando CNPJ: {cnpj_l}")
        f_nfe = st.file_uploader("Arquivos NF-e (XML/ZIP)", type=["xml", "zip"], accept_multiple_files=True, key="up_nfe")
        if st.button("🚀 PROCESSAR MATRIZ FISCAL"):
            if not f_nfe: st.error("Selecione os arquivos!")
            else:
                l_final = []
                with st.spinner("Extraindo dados..."):
                    for f in f_nfe:
                        if f.name.endswith('.zip'):
                            with zipfile.ZipFile(f) as z:
                                for n in z.namelist():
                                    if n.lower().endswith('.xml'): ler_xml_nfe(z.read(n), l_final, cnpj_l)
                        else: ler_xml_nfe(f.read(), l_final, cnpj_l)
                if l_final:
                    df_nfe = pd.DataFrame(l_final)
                    out_nfe = io.BytesIO()
                    with pd.ExcelWriter(out_nfe, engine='xlsxwriter') as writer:
                        df_nfe.to_excel(writer, index=False)
                    st.success(f"✨ {len(df_nfe)} itens processados!")
                    st.download_button("📥 BAIXAR MATRIZ DIAMANTE", out_nfe.getvalue(), f"matriz_{cnpj_l}.xlsx")
    else:
        st.warning("👈 Insira o CNPJ na barra lateral para começar.")

# --- ABA 2: NFS-e (AUDITORIA FISCAL) ---
with tab_nfse:
    st.markdown("<h1>📑 PORTAL TAX NFS-e</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="instrucoes-card"><h3>📖 Auditoria de Serviços</h3><ol><li>Arraste arquivos XML ou ZIP de prefeituras.</li><li>Clique em Iniciar Auditoria.</li><li>Analise o diagnóstico automático.</li></ol></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="instrucoes-card"><h3>📊 Diagnóstico</h3><ul><li>Separação de ISS Próprio e Retido.</li><li>Identificação de retenções federais.</li><li>Alerta visual de divergências.</li></ul></div>', unsafe_allow_html=True)

    f_nfse = st.file_uploader("Arquivos NFS-e (XML/ZIP)", type=["xml", "zip"], accept_multiple_files=True, key="up_nfse")
    if f_nfse:
        if st.button("🚀 INICIAR AUDITORIA FISCAL"):
            d_rows = []
            with st.spinner("Auditando..."):
                for f in f_nfse:
                    if f.name.endswith('.zip'):
                        with zipfile.ZipFile(f) as z:
                            for x_name in z.namelist():
                                if x_name.endswith('.xml'):
                                    r = process_xml_file_nfse(z.read(x_name), x_name)
                                    if r: d_rows.append(r)
                    else:
                        r = process_xml_file_nfse(f.read(), f.name)
                        if r: d_rows.append(r)
            if d_rows:
                df_nfse = pd.DataFrame(d_rows)
                c_fin = ['Vlr_Bruto', 'Vlr_Liquido', 'ISS_Valor', 'Ret_ISS', 'Ret_PIS', 'Ret_COFINS', 'Ret_CSLL', 'Ret_IRRF']
                for c in c_fin: df_nfse[c] = pd.to_numeric(df_nfse[c], errors='coerce').fillna(0.0)
                df_nfse['Diagnostico'] = df_nfse.apply(lambda r: "⚠️ Divergência!" if abs(r['Vlr_Bruto'] - r['Vlr_Liquido']) > 0.01 else "✅", axis=1)
                
                # Reordenar colunas
                cols = list(df_nfse.columns)
                if 'Ret_ISS' in cols and 'ISS_Valor' in cols:
                    cols.insert(cols.index('ISS_Valor') + 1, cols.pop(cols.index('Ret_ISS')))
                    df_nfse = df_nfse[cols]

                st.success(f"✅ {len(df_nfse)} notas auditadas!")
                st.dataframe(df_nfse)

                out_nfse = io.BytesIO()
                with pd.ExcelWriter(out_nfse, engine='xlsxwriter') as writer:
                    df_nfse.to_excel(writer, index=False, sheet_name='AuditoriaNFS-e')
                    wb = writer.book
                    ws = writer.sheets['AuditoriaNFS-e']
                    h_fmt = wb.add_format({'bold': True, 'bg_color': '#FF69B4', 'font_color': 'white', 'border': 1})
                    n_fmt = wb.add_format({'num_format': '#,##0.00'})
                    for i, col in enumerate(df_nfse.columns):
                        ws.write(0, i, col, h_fmt)
                        if col in c_fin: ws.set_column(i, i, 18, n_fmt)
                        else: ws.set_column(i, i, 22)

                st.download_button("📥 BAIXAR AUDITORIA EXCEL", out_nfse.getvalue(), "auditoria_nfse.xlsx")
