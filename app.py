# -*- coding: utf-8 -*-
import os
import zipfile
import io
from flask import Flask, jsonify
import logging
from ftplib import FTP

# Configura o logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
# --- LINHA FINAL PARA CORRIGIR OS ACENTOS ---
app.config['JSON_AS_ASCII'] = False
# ---------------------------------------------

# Detalhes do servidor FTP
FTP_HOST = "ftp.mtps.gov.br"
FTP_PATH = "/portal/fiscalizacao/seguranca-e-saude-no-trabalho/caepi/"
FTP_FILENAME = "tgg_export_caepi.zip"

# Nomes das colunas, conforme a estrutura do ficheiro do MTE
COLUMNS = [
    'NRRegistroCA', 'DataValidade', 'Situacao', 'NRProcesso', 'CNPJ', 'RazaoSocial',
    'Natureza', 'NomeEquipamento', 'DescEquipamento', 'LocalMarcacaoCA', 'Referencia',
    'Cor', 'AprovadoParaLaudo', 'RestricaoLaudo', 'ObservacaoAnaliseLaudo',
    'CNPJLaboratorio', 'RazaoSocialLaboratorio', 'NRLaudo', 'Norma'
]

def consultar_ca(numero_ca):
    """
    Esta função baixa a base de dados e procura linha por linha pelo C.A. específico.
    """
    logging.info(f"Iniciando consulta para o C.A.: {numero_ca}...")
    try:
        # Conecta-se ao servidor FTP
        with FTP(FTP_HOST, timeout=60) as ftp:
            ftp.login()
            ftp.cwd(FTP_PATH)
            ftp_buffer = io.BytesIO()
            ftp.retrbinary(f"RETR {FTP_FILENAME}", ftp_buffer.write)
            ftp_buffer.seek(0)
            logging.info("Download do ficheiro .zip via FTP concluído.")

        # Extrai o ficheiro .txt do .zip em memória
        with zipfile.ZipFile(ftp_buffer) as z:
            txt_filename = [name for name in z.namelist() if name.endswith('.txt')][0]
            with z.open(txt_filename) as txt_file:
                # Lê o ficheiro linha por linha para poupar memória
                for line in io.TextIOWrapper(txt_file, encoding='latin1'):
                    # O ficheiro começa com uma linha de cabeçalho, que ignoramos
                    if line.startswith('#NRRegistroCA'):
                        continue
                    
                    # Verifica se a linha começa com o número do C.A. que procuramos
                    if line.strip().startswith(str(numero_ca) + '|'):
                        logging.info(f"C.A. {numero_ca} encontrado!")
                        # Separa a linha encontrada nas suas colunas
                        values = line.strip().split('|')
                        # Combina os nomes das colunas com os valores encontrados
                        resultado = dict(zip(COLUMNS, values))
                        resultado['status'] = 'sucesso'
                        return resultado

        # Se o loop terminar e não encontrarmos o C.A.
        logging.warning(f"C.A. {numero_ca} não encontrado na base de dados.")
        return {'status': 'erro', 'mensagem': 'C.A. não encontrado na nossa base de dados.'}

    except Exception as e:
        logging.error(f"Falha ao consultar o C.A. {numero_ca}: {e}")
        return {'status': 'erro', 'mensagem': f'Ocorreu um erro: {e}'}

@app.route('/')
def index():
    """Página inicial para verificar se o robô está no ar."""
    return "<h1>Robô ZapCA.I (Versão Super Leve) está no ar!</h1>"

@app.route('/consulta/<int:numero_ca>')
def api_consulta_ca(numero_ca):
    """Endpoint da API para consultar um C.A."""
    resultado = consultar_ca(numero_ca)
    return jsonify(resultado)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
