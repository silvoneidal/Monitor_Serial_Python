import os
import requests
import configparser
from tkinter import messagebox
from dotenv import load_dotenv # pip install python-dotenv==0.15.0

# Carrega as variáveis do .env
load_dotenv()

# Declaração de variável para update
config = configparser.ConfigParser()
TOKEN = os.getenv('TOKEN')
github_token = TOKEN

# Função para obter o caminho da pasta do projeto
def obter_pasta_projeto():
    return os.path.dirname(os.path.abspath(__file__))

# Função para ler dados em config.ini
def read_config():
    global VERSION_LOCAL
    global FILE_LOCAL
    # Ler dados do arquivo
    config.read('config.ini')
    # Acessar os valores
    VERSION_LOCAL = config['UPDATE']['Version']
    FILE_LOCAL = config['UPDATE']['File']

# Função para gravar dados em config.ini
def write_config(VERSION_LOCAL, FILE_LOCAL):
    # Adicionar seções e atributos
    config['UPDATE'] = {
        'Version': VERSION_LOCAL,
        'File': FILE_LOCAL,
    }
    # Gravar no arquivo
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

# Download da versão
def download_versao(latest_version, response):
    write_config(latest_version, FILE_LOCAL)

    # Obter os ativos da release
    assets = response.json().get('assets')
    
    # Procurar o ativo desejado (Codigo Fonte.zip)
    download_url = None
    for asset in assets:
        if FILE_LOCAL in asset['name']:
            download_url = asset['browser_download_url']
            break

    if download_url:
        # Baixar o arquivo
        download_response = requests.get(download_url, stream=True)
        
        # Salvar o arquivo
        with open('update.zip', 'wb') as f:
            for chunk in download_response.iter_content(1024):
                f.write(chunk)
    else:
        messagebox.showinfo("DALÇÓQUIO AUTOMAÇÃO", "Não foi encontrado o arquivo desejado para download.")

# Função para executar o arquivo update.exe
def executar_update():
    # Endpoint para obter a última release
    read_config() # Leitura do arquivo de configuração
    global github_repo
    github_repo = 'silvoneidal/' + FILE_LOCAL
    response = requests.get(
        f'https://api.github.com/repos/{github_repo}/releases/latest',
        headers={'Authorization': f'token {github_token}'}
    )

    # Verificar o status da resposta
    if response.status_code == 200:
        # Obter a versão mais recente do repositório
        latest_version = response.json().get('tag_name')
        
        # Comparar versões (assumindo que estão no formato semântico)
        if latest_version > VERSION_LOCAL:
            download_versao(latest_version, response)
            pasta_projeto = obter_pasta_projeto()
            messagebox.showinfo("DALÇÓQUIO AUTOMAÇÃO", f"Efetuado download da versão mais recente {latest_version}\n" + 
                                f"Extraia os arquivos de update.zip e substitua pelos arquivos atuais em {pasta_projeto}")
                
        else:
            messagebox.showinfo("DALÇÓQUIO AUTOMAÇÃO", f"A versão atual {latest_version} é a mais recente. ")
            
    elif response.status_code == 404:
        messagebox.showinfo("DALÇÓQUIO AUTOMAÇÃO", "O repositório ou a release mais recente não foi encontrada!")
    else:
        messagebox.showinfo("DALÇÓQUIO AUTOMAÇÃO", f"Erro ao verificar a versão: {response.status_code}")

