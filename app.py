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
