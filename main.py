import pandas as pd
import qrcode
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from PIL import Image
from io import BytesIO

# Leitura do arquivo CSV
tabela = pd.read_csv('DadosTesteCadastro.csv')

# Caminho para a imagem do modelo
imagem_modelo = "CarteirinhaModeloTeste.png"

# Carregar a imagem com Pillow para obter as dimensões
img = Image.open(imagem_modelo)
largura, altura = img.size  # Dimensões em pixels

# Converter pixels para pontos (1 pixel = 1 ponto em PDF)
largura_pontos = largura
altura_pontos = altura

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

        # Gerar o QR code
        qr_data = f"https://example.com/validate?matricula={matricula}"
        qr = qrcode.make(qr_data)

        # Salvar o QR code em memória usando BytesIO
        qr_buffer = BytesIO()
        qr.save(qr_buffer, format="PNG")
        qr_buffer.seek(0)  # Voltar ao início do buffer

        # Converter o QR code para um objeto ImageReader
        qr_image = ImageReader(qr_buffer)

        # Inserir o QR code no PDF
        qr_x = 750  # Coordenada X
        qr_y = 65   # Coordenada Y
        qr_size = 170  # Tamanho do QR code
        c.drawImage(qr_image, qr_x, qr_y, width=qr_size, height=qr_size)

        # Finalizar o PDF
        c.save()

        print(f"PDF gerado com sucesso: {pdf_saida}")

    except Exception as e:
        # Registro do erro com detalhes
        print(f"Erro ao gerar carteirinha para {nome} (Matrícula: {matricula}): {e}")
