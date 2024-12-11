import os
from flask import Flask, request, jsonify
from carteirinhas import gerar_carteirinhas  # Importa a função de geração de carteirinhas
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

app = Flask(__name__)

# Credenciais do Google Sheets em formato de dicionário
GOOGLE_CREDENTIALS = {
  "type": "service_account",
  "project_id": "presencaapi",
  "private_key_id": "12e7e65ba009c8f658f71511a6686e62171b96f1",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCuM7+Kgp+pBnET\n7tXNyXI4RHOFlGo+fyAmXqY2XHOyXBbMQpnOpjb6TxSxRq/NPdOYCkoUJRV5Sfzv\nmr/Iyw9Vn3kdh0zWSOV6X877seZdCG3QBy3m+XINv6vjGiAYsU0agPkROxLuR8EB\nwnWzXd4ZxNStJYOw+AAn2zsYHZvt3BOqQfBAHO+BGvysgX6s1x5q/AAhuL94BFOd\nZjLpGsfzp7YyYcHRsI6Im5N6USOYtdT5zOs2XTQWT2coWnDvBLdfOyH4rsrsc5d4\nYnxJQNP1YkTkb0LW5arzy1uSARbih9OICJ/2i/Z8ZlW8N01YOs0wOLXZwUdNFnLo\nwTcWFd4JAgMBAAECggEADhYFIPrFqkc+Ztw4fEwTvlUFT6yGmB3IyGbS4zEVRzuH\nDxE7mqgkvezIbDqeWzw/8IVfJBiI5KaE8LhUqwnbEuiy7x5SVOl5aix2cjJvwYoS\n8cVYLYXHdoZ51wKfzHSvGruJvZ5HPkPzFA9YsR5Kp/lwhmey1GEusgpaJu24qW0F\n9HhDH/hQYhzVYNq9wCQRSq1KmgSSCqoDfXUdKit/bp/fiw0X9liDEsT7kQDBl+bp\njccikEq486zDRMPniuKqlClV/DrvRSn2O5WaDwe8wDh5ytErL8zQmQf9gjhxPK71\nGMwunC+xg9E+2llltGk2xbNESF2aBdVPrN9hTqIMWQKBgQDpcb38OTYSbryxoizh\nF5OzbadSKUZTRSKb1mMs8J3nFDC3opDTz6A7rkus0faVOxrFU73ljBUGhSr1CW1Z\nGFR+yJjgO6HjxrA1lD5UvIevIoQXuNhB0M8hOEblegBP/W3emNuEVTPWgXQ62l+E\nWU5o+P2MTasxOkNJ185xBM/TzwKBgQC/CKXaUN9PegK5zzpfB6pXX26jwzgpDjJ7\nOYlzT2DADL8wyiQyJj1Xr6Mq7v8g7rLKX7ihiMprq/uxVJaCqF32XdPpCKf+4MjK\nMaKcGjYDr7yuq3aCN4XqvgiCWpLi7G9Pu5492MFB6oQ4Zt723YvpX2vjxqxeoI90\n1h9mzbSupwKBgQDjLb+3z21hrsaPD8YhH7KrcNDeUjCQJL2zboWBXIAuOyXV76yF\nlI7YxZv7iTEwtR4uXnp1A0gK2lmdsRjrFZRU9Z5gyWeYpOkimyu1hut8clieRVKf\najfIml3UQFBBh93+PD+Unt4dqEmWZKGDyO1XlsgYXBV3iL2nBQ9wSUB/XQKBgDnu\nQ21bDP0rANycDRV4W523YPPkZYl9tq1Lm3UOY0aaFviStDtJAV0v9Ak3BMNV334j\nXPgPZWMVenQiNKpWqHfnqDWI3HkcbYdzWd6AzFR93HgToxKGB+RR0H7HPLf3/yFs\nweX7b0+v8HyyJXczZBRXTX57ZxYjFp3VuRwR0XMNAoGBALHJ1NwnqXasDnHC6K76\nLkgw3XimKVsByr6mfai5Jq+dOesFq3Hrtv+31PT8HkKRNOLpPp37YcfxlV3M3wmj\nzjTFJ7ULj5F7eVD4giQvJlAvsMSp9O/v3rGRUgyiEOBERUBnE7pdOzn9XhpsU0tX\nqZFIMMyxm9VYFRn3ZUfmz7E9\n-----END PRIVATE KEY-----\n",
  "client_email": "registropresenca@presencaapi.iam.gserviceaccount.com",
  "client_id": "115810422270180480586",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/registropresenca%40presencaapi.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}


# Função para autenticação no Google Sheets
def autenticar_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(GOOGLE_CREDENTIALS, scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open("ListaPresenca2025")
    sheet = spreadsheet.worksheet("Página1")
    return sheet

# Rota para registrar a presença
@app.route('/validate', methods=['GET'])
def registrar_presenca():
    matricula = request.args.get('matricula').strip()
    aluno_id = request.args.get('id')

    if not matricula or not aluno_id:
        return jsonify({"error": "Parâmetros 'matricula' e 'id' são necessários"}), 400

    # Obter a planilha do Google Sheets
    sheet = autenticar_google_sheets()

    # Nome do aluno
    nome_aluno = request.args.get('nome', 'Aluno Desconhecido')

    # Registrar presença
    status = 'Presente'
    data_presenca = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    sheet.append_row([matricula, nome_aluno, status, data_presenca])  # Colunas: Matrícula, Nome, Presença

    return jsonify({"message": f"Presença de {nome_aluno} registrada com sucesso!"}), 200

if __name__ == "__main__":
    gerar_carteirinhas()  # Gera as carteirinhas quando o servidor iniciar
    port = int(os.environ.get('PORT', 8080))  # Usa a porta 8080, caso Railway não defina
    app.run(debug=True, host='0.0.0.0', port=port)
