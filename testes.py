import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Escopos necessários para acessar o Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

# Carregar as credenciais
creds = ServiceAccountCredentials.from_json_keyfile_name('presencaapi-8ad73dbbe053.json', scope)
client = gspread.authorize(creds)

# Listar todas as planilhas acessíveis
spreadsheets = client.openall()
for sheet in spreadsheets:
    print(sheet.title)

spreadsheet = client.open("ListaPresenca2025")
worksheets = spreadsheet.worksheets()

print("Abas disponíveis:")
for ws in worksheets:
    print(ws.title)

