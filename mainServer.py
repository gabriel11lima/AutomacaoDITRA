import pandas as pd
import qrcode
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from PIL import Image
from io import BytesIO
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import uuid
from flask import Flask, request, jsonify
import datetime
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# Configuração do Flask
app = Flask(__name__)

# Função para autenticação no Google Sheets
def autenticar_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('presencaapi-8ad73dbbe053.json', scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open("ListaPresenca2025")
    sheet = spreadsheet.worksheet("Página1")
    return sheet


# Rota para registrar a presença
@app.route('/validate', methods=['GET'])
def registrar_presenca():
    matricula = request.args.get('matricula').strip()  # Remover espaços extras
    aluno_id = request.args.get('id')

    if not matricula or not aluno_id:
        return jsonify({"error": "Parâmetros 'matricula' e 'id' são necessários"}), 400

    # Obter a planilha do Google Sheets
    sheet = autenticar_google_sheets()

    # Nome do aluno (gerado no momento da carteirinha)
    # Aqui, vamos colocar o nome diretamente na URL (se você quiser, pode alterar a maneira de gerar o nome)
    nome_aluno = request.args.get('nome', 'Aluno Desconhecido')

    # Registrar presença (não há verificação de se o aluno existe, apenas adiciona uma nova linha)
    status = 'Presente'
    data_presenca = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

    # Adicionar nova linha com o registro da presença
    sheet.append_row([matricula, nome_aluno, status, data_presenca])  # Colunas: Matrícula, Nome, Presença

    return jsonify({"message": f"Presença de {nome_aluno} registrada com sucesso!"}), 200





# Função para gerar as carteirinhas e QR Codes
def gerar_carteirinhas():
    # Leitura do arquivo CSV
    tabela = pd.read_csv('CredenciamentoTeste.csv')

    # Caminho para a imagem do modelo
    imagem_modelo = "CarteirinhaModeloTeste.png"

    # Carregar a imagem com Pillow para obter as dimensões
    img = Image.open(imagem_modelo)
    largura, altura = img.size  # Dimensões em pixels

    # Converter pixels para pontos (1 pixel = 1 ponto em PDF)
    largura_pontos = largura
    altura_pontos = altura

    # Autenticar no Google Sheets
    sheet = autenticar_google_sheets()

    # Loop para gerar um PDF único para cada aluno
    for index, row in tabela.iterrows():
        try:
            nome = row['Nome']
            matricula = row['Matrícula']
            validade = "31/12/2025"

            # Nome do arquivo PDF de saída
            pdf_saida = f"carteirinha_{matricula}.pdf"

            # Criar o PDF com o mesmo tamanho da imagem
            c = canvas.Canvas(pdf_saida, pagesize=(largura_pontos, altura_pontos))

            # Adicionar a imagem de fundo
            c.drawImage(
                imagem_modelo, 0, 0,
                width=largura_pontos,
                height=altura_pontos,
                preserveAspectRatio=True,
                anchor='c'  # Garante qualidade e proporção
            )

            # Definir o estilo do texto
            c.setFont("Times-Roman", 50)
            c.setFillColorRGB(0.1098, 0.1098, 0.4)  # Cor personalizada

            # Adicionar os textos na carteirinha
            c.drawString(250, altura_pontos - 297, f"{nome}")
            c.drawString(330, altura_pontos - 411, f"{matricula}")
            c.drawString(305, altura_pontos - 524, f"{validade}")

            # Gerar o QR code com link único para a API Flask
            qr_data = f"http://192.168.15.20:5000/validate?matricula={matricula}&id={uuid.uuid4()}&nome={nome}"
            qr = qrcode.make(qr_data)

            # Salvar o QR code em memória usando BytesIO
            qr_buffer = BytesIO()
            qr.save(qr_buffer, format="PNG")
            qr_buffer.seek(0)  # Voltar ao início do buffer

            # Converter o QR code para um objeto ImageReader
            qr_image = ImageReader(qr_buffer)

            # Inserir o QR code no PDF
            qr_x = 750  # Coordenada X
            qr_y = 65  # Coordenada Y
            qr_size = 170  # Tamanho do QR code
            c.drawImage(qr_image, qr_x, qr_y, width=qr_size, height=qr_size)

            # Finalizar o PDF
            c.save()

            print(f"PDF gerado com sucesso: {pdf_saida}")

        except Exception as e:
            # Registro do erro com detalhes
            print(f"Erro ao gerar carteirinha para {nome} (Matrícula: {matricula}): {e}")


# Roda o Flask
if __name__ == "__main__":
    gerar_carteirinhas()  # Gerar as carteirinhas antes de rodar o servidor Flask
    app.run(debug=True, host='0.0.0.0', port=5000)
