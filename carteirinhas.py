import pandas as pd
import qrcode
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from PIL import Image
from io import BytesIO
import uuid

def gerar_carteirinhas():
    tabela = pd.read_csv('CredenciamentoTeste.csv')
    imagem_modelo = "CarteirinhaModeloTeste.png"

    # Carregar a imagem com Pillow para obter as dimensões
    img = Image.open(imagem_modelo)
    largura, altura = img.size
    largura_pontos = largura
    altura_pontos = altura

    # Loop para gerar um PDF único para cada aluno
    for index, row in tabela.iterrows():
        try:
            nome = row['Nome']
            matricula = row['Matrícula']
            validade = "31/12/2025"
            pdf_saida = f"carteirinha_{matricula}.pdf"

            c = canvas.Canvas(pdf_saida, pagesize=(largura_pontos, altura_pontos))

            # Adicionar a imagem de fundo
            c.drawImage(imagem_modelo, 0, 0, width=largura_pontos, height=altura_pontos, preserveAspectRatio=True, anchor='c')

            # Definir o estilo do texto
            c.setFont("Times-Roman", 50)
            c.setFillColorRGB(0.1098, 0.1098, 0.4)

            # Adicionar os textos na carteirinha
            c.drawString(250, altura_pontos - 297, f"{nome}")
            c.drawString(330, altura_pontos - 411, f"{matricula}")
            c.drawString(305, altura_pontos - 524, f"{validade}")

            # Gerar o QR code
            qr_data = f"http://192.168.15.20:5000/validate?matricula={matricula}&id={uuid.uuid4()}&nome={nome}"
            qr = qrcode.make(qr_data)

            # Salvar o QR code em memória
            qr_buffer = BytesIO()
            qr.save(qr_buffer, format="PNG")
            qr_buffer.seek(0)
            qr_image = ImageReader(qr_buffer)

            # Inserir o QR code no PDF
            qr_x = 750
            qr_y = 65
            qr_size = 170
            c.drawImage(qr_image, qr_x, qr_y, width=qr_size, height=qr_size)

            # Finalizar o PDF
            c.save()
            print(f"PDF gerado com sucesso: {pdf_saida}")

        except Exception as e:
            print(f"Erro ao gerar carteirinha para {nome} (Matrícula: {matricula}): {e}")
