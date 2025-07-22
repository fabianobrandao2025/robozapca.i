# -*- coding: utf-8 -*-
import os
import requests
import pandas as pd
import zipfile
import io
from flask import Flask, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
import logging

# Configura o logging para vermos o que o robô está a fazer
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# URL oficial para o download da base de dados
FTP_URL = "ftp://ftp.mtps.gov.br/portal/fiscalizacao/seguranca-e-saude-no-trabalho/caepi/tgg_export_caepi.zip"

# Variável global para guardar os dados dos C.A.s em memória
ca_data = pd.DataFrame()

def atualizar_base_de_dados():
    """
    Esta função baixa a base de dados do governo, processa-a e
    guarda na memória para consultas ultra-rápidas.
    """
    global ca_data
    logging.info("A iniciar a atualização da base de dados do CAEPI...")
    try:
        # Baixa o ficheiro .zip
        response = requests.get(FTP_URL, timeout=300) # Timeout de 5 minutos
        response.raise_for_status()
        logging.info("Download do ficheiro .zip concluído com sucesso.")

        # Extrai o ficheiro .txt do .zip em memória
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            # Encontra o nome do ficheiro .txt dentro do zip
            txt_filename = [name for name in z.namelist() if name.endswith('.txt')][0]
            with z.open(txt_filename) as txt_file:
                # Lê o ficheiro .txt com o Pandas, que é ótimo para lidar com dados
                # Usamos 'latin1' que é a codificação comum para ficheiros de governos brasileiros
                # O separador é o '|' (pipe), como vimos no documento do MTE
                df = pd.read_csv(txt_file, sep='|', encoding='latin1', on_bad_lines='skip')
                
                # Renomeia a primeira coluna que vem com um caractere estranho
                df = df.rename(columns={df.columns[0]: 'NRRegistroCA'})
                
                # Define a coluna do C.A. como o nosso índice para buscas rápidas
                df.set_index('NRRegistroCA', inplace=True)
                
                ca_data = df
                logging.info(f"Base de dados atualizada com sucesso! {len(ca_data)} registos carregados.")

    except Exception as e:
        logging.error(f"Falha ao atualizar a base de dados: {e}")

@app.route('/')
def index():
    """Página inicial para verificar se o robô está no ar."""
    if not ca_data.empty:
        return f"<h1>Robô ZapCA.I está no ar!</h1><p>Base de dados carregada com {len(ca_data)} registos.</p>"
    else:
        return "<h1>Robô ZapCA.I está no ar!</h1><p>A aguardar o carregamento da base de dados. Por favor, tente novamente em alguns minutos.</p>"

@app.route('/consulta/<int:numero_ca>')
def api_consulta_ca(numero_ca):
    """Endpoint da API para consultar um C.A. na nossa base de dados local."""
    if ca_data.empty:
        return jsonify({'status': 'erro', 'mensagem': 'A base de dados ainda está a ser carregada. Por favor, tente novamente em breve.'}), 503

    try:
        # Procura o C.A. na nossa base de dados em memória
        resultado = ca_data.loc[numero_ca].to_dict()
        resultado['status'] = 'sucesso'
        return jsonify(resultado)
    except KeyError:
        return jsonify({'status': 'erro', 'mensagem': 'C.A. não encontrado na nossa base de dados.'})
    except Exception as e:
        return jsonify({'status': 'erro', 'mensagem': f'Ocorreu um erro inesperado: {str(e)}'})

# --- Agendador para Atualização Automática ---
scheduler = BackgroundScheduler(daemon=True)
# Agenda a atualização para acontecer todos os dias às 3 da manhã
scheduler.add_job(atualizar_base_de_dados, 'cron', hour=3, minute=0)
scheduler.start()

# Inicia a primeira atualização assim que o robô liga
try:
    atualizar_base_de_dados()
except Exception as e:
    logging.error(f"Erro na primeira carga da base de dados: {e}")


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
