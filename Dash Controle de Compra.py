import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# Defina o escopo de acesso
scope = [
    "https://spreadsheets.google.com/feeds",
    'https://www.googleapis.com/auth/spreadsheets',
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

# Faça autenticação com as credenciais
creds = ServiceAccountCredentials.from_json_keyfile_name('controle-de-receitas-360613-2a184c3658f2.json', scope)
client = gspread.authorize(creds)

# Abra a planilha e selecione a aba específica
spreadsheet_name = "Banco de Dados - Papieri"  # Substitua pelo nome da sua planilha
worksheet_name = "Faturamento vs Compra"             # Substitua pelo nome da aba específica
sheet = client.open(spreadsheet_name).worksheet(worksheet_name)

# Obtenha todos os valores da aba como uma lista de listas
values_list = sheet.get_all_values()

# Crie um DataFrame e trate nomes de colunas duplicados
df = pd.DataFrame(values_list[1:], columns=values_list[0])

# Verifica se há colunas duplicadas e renomeia
cols = pd.Series(df.columns)
for dup in cols[cols.duplicated()].unique():
    cols[cols[cols == dup].index.values.tolist()] = [dup + '_' + str(i) if i != 0 else dup for i in range(sum(cols == dup))]

df.columns = cols

# Função para aplicar estilo às células
def highlight_buy_sell(value):
    if value == "Comprar":
        return 'background-color: #66ba65'  # Um verde mais claro
    elif value == "Não comprar":
        return 'background-color: #f590a0'  # Um vermelho mais claro
    else:
        return ''
    
# Função para destacar a linha inteira
def highlight_row(row, highlight_index):
    return ['background-color: #ffff99' if row.name == highlight_index else '' for _ in row]  

# Função para estilizar a linha em negrito
def bold_line(row, highlight_index):
    return ['font-weight: bold' if row.name == highlight_index else '' for _ in row]

# Aplica o estilo na coluna 'AÇÃO', se ela existir
if 'AÇÃO' in df.columns:
    # Estiliza o cabeçalho
    header_style = [{
        'selector': 'thead th',
        'props': [('background-color', '#f4f4f4'), ('color', 'black')]
    }]


    # Combina estilos de cabeçalho com estilos de célula
    styled_df = df.style.map(highlight_buy_sell, subset=['AÇÃO']).set_table_styles(header_style)

    # Estiliza cada coluna individualmente
    # Você precisa definir os seletores CSS de acordo com a estrutura HTML gerada pelo Streamlit
    column_styles = [
        {'selector': f'.col{df.columns.get_loc("CNPJ")}', 'props': [('min-width', '170px'), ('max-width', '250px')]},
        {'selector': f'.col{df.columns.get_loc("EMPRESA")}', 'props': [('min-width', '180px'), ('max-width', '250px')]},
        {'selector': f'.col{df.columns.get_loc("COMPRA")}', 'props': [('min-width', '180px'), ('max-width', '250px')]},
        {'selector': f'.col{df.columns.get_loc("FATURAMENTO")}', 'props': [('min-width', '150px'), ('max-width', '250px')]},
        # Adicione mais estilos conforme necessário
    ]

    additional_styles = [
        
        {'selector': f'th.colname-{df.columns.get_loc("% PERCENTUAL DE COMPRA")}', 'props': [('text-align', 'center')]},
]

    # Aplicar estilos de coluna com overwrite=False para manter os estilos de cabeçalho
    styled_df = styled_df.set_table_styles(column_styles, additional_styles, overwrite=False)

    # Aplica o estilo de linha em negrito na linha 4 (índice 4)
    styled_df = styled_df.apply(bold_line, highlight_index=4, axis=1)

# Exibe a tabela estilizada usando st.write com HTML
st.title('Controle de Compras')
st.write(styled_df.to_html(escape=False), unsafe_allow_html=True)