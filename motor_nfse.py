import xml.etree.ElementTree as ET
import io

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
