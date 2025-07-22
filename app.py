# -*- coding: utf-8 -*-
import os
from flask import Flask, jsonify
import logging

# Configura o logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
# --- Linha para corrigir os acentos na resposta ---
app.config['JSON_AS_ASCII'] = False
# ---------------------------------------------------

# --- NOSSA BASE DE DADOS DE DEMONSTRAÇÃO ---
# Aqui temos 5 C.A.s pré-selecionados para o nosso teste.
DADOS_DEMO = {
    41430: {
        "status": "sucesso",
        "situacao": "Válido",
        "data_validade": "22/09/2027",
        "razao_social": "MARLUVAS EQUIPAMENTOS DE SEGURANCA LTDA",
        "equipamento": "BOTINA - TIPO B"
    },
    10346: {
        "status": "sucesso",
        "situacao": "Válido",
        "data_validade": "08/03/2029",
        "razao_social": "KALIPSO EQUIPAMENTOS INDIVIDUAIS DE PROTECAO LTDA",
        "equipamento": "ÓCULOS"
    },
    36033: {
        "status": "sucesso",
        "situacao": "Válido",
        "data_validade": "19/01/2029",
        "razao_social": "MONTANA QUIMICA LTDA.",
        "equipamento": "CAPACETE"
    },
    29014: {
        "status": "sucesso",
        "situacao": "Válido",
        "data_validade": "25/09/2025",
        "razao_social": "DVT COMERCIO, IMPORTACAO E EXPORTACAO LTDA",
        "equipamento": "LUVA PARA PROTEÇÃO CONTRA AGENTES TÉRMICOS E MECÂNICOS"
    },
    37692: {
        "status": "sucesso",
        "situacao": "Válido",
        "data_validade": "20/04/2028",
        "razao_social": "KALIPSO EQUIPAMENTOS INDIVIDUAIS DE PROTECAO LTDA",
        "equipamento": "LUVA TIPO A"
    }
}
# -----------------------------------------

@app.route('/')
def index():
    """Página inicial para verificar se o robô está no ar."""
    return "<h1>Robô ZapCA.I (Versão de Demonstração) está no ar!</h1>"

@app.route('/consulta/<int:numero_ca>')
def api_consulta_ca(numero_ca):
    """Endpoint da API que consulta a nossa base de dados de demonstração."""
    logging.info(f"Recebida consulta para o C.A. de demonstração: {numero_ca}")
    
    # Procura o C.A. na nossa lista de demonstração
    resultado = DADOS_DEMO.get(numero_ca)
    
    if resultado:
        return jsonify(resultado)
    else:
        # Se o C.A. não estiver na nossa lista, devolve uma mensagem de erro amigável
        return jsonify({'status': 'erro', 'mensagem': 'C.A. não encontrado na nossa base de demonstração.'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
