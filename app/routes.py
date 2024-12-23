from app import app
import pandas as pd
from io import BytesIO
from flask import session, render_template, request, send_file, Response, request
import re, time, os, signal, threading

# Habilitar a utilização de sessões no Flask
app.secret_key = 'beterraba'

# Função para remover espaços em branco
def remove_espacos(texto):
    return re.sub(r'[^0-9IiDd ]', '', str(texto))

# Função para separar IDs
def separa_ids(numero_id):
    # Remove espaços extras
    numero_id = remove_espacos(numero_id)
    
    # Padrões para IDs válidos e inválidos
    padrao_ids_invalidos = r'\b\d{7}\d{2}\d{4}\d\d\d{2}\d{4}|\d{5}\d{6}\d{4}\d{2}\b'  # IDs inválidos no formato original
    padrao_ids_validos = r'(?i)\bID\s*\d{5,6}(?!\d)'  # IDs válidos com prefixo "ID"

    # Captura IDs válidos e inválidos
    ids_invalidos = re.findall(padrao_ids_invalidos, numero_id)
    ids_validos = re.findall(padrao_ids_validos, numero_id)

    # Processa IDs válidos removendo "ID" e outros caracteres não numéricos
    ids_validos_formatados = [re.sub(r'\D+', '', id_[2:]) if id_.startswith("ID") else re.sub(r'\D+', '', id_)
                              for id_ in ids_validos]
    
    # Segunda verificação nos IDs inválidos
    for id_invalido in ids_invalidos[:]:  # Cria uma cópia para iteração enquanto remove
        id_numerico = re.sub(r'\D+', '', id_invalido)  # Remove caracteres extras
        if re.match(r'^\d{5,6}$', id_numerico):  # IDs inválidos que são na verdade válidos
            ids_validos_formatados.append(id_numerico)
            ids_invalidos.remove(id_invalido)

    # Retorna a lista de IDs válidos como string, preservando a duplicidade
    return ', '.join(ids_validos_formatados)


# Rota para a página principal
@app.route('/', methods=['GET', 'POST'])
def index():
    data = None

    if request.method == 'POST':
        arquivo = request.files['arquivo']
        if arquivo:
            # Ler o arquivo Excel
            df = pd.read_excel(arquivo)

            # Salvar o DataFrame na sessão para ser usado posteriormente
            session['df'] = df.to_dict()  # Convertendo o DataFrame para dicionário para armazenar na sessão

            # Converte o DataFrame para HTML para exibição
            data = df.to_html(classes='tabela tabela_listada', index=False)

    return render_template('index.html', data=data)

# Função para identificar colunas
def identificar_colunas(df, padroes_colunas):
    todas_colunas = []
    for padrao in padroes_colunas:
        colunas_encontradas = [col for col in df.columns if col.startswith(padrao)]
        todas_colunas.extend(colunas_encontradas)

    colunas_adicionais = []
    if 'ETIQUETA NACIONAL' in df.columns:
        df['ETIQUETA NACIONAL'] = df['ETIQUETA NACIONAL'].apply(lambda x: x.strip() if isinstance(x, str) else x)
        colunas_adicionais.append('ETIQUETA NACIONAL')

    elif 'Etiqueta Nacional' in df.columns:
        df['Etiqueta Nacional'] = df['Etiqueta Nacional'].apply(lambda x: x.strip() if isinstance(x, str) else x)
        colunas_adicionais.append('Etiqueta Nacional')

    elif 'LEMBRETE' in df.columns:
        df['LEMBRETE'] = df['LEMBRETE'].apply(lambda x: x.strip() if isinstance(x, str) else x)
        colunas_adicionais.append('LEMBRETE')
        
    elif 'Lembrete' in df.columns:
        df['Lembrete'] = df['Lembrete'].apply(lambda x: x.strip() if isinstance(x, str) else x)
        colunas_adicionais.append('Lembrete')

    todas_colunas.extend(colunas_adicionais)
    todas_colunas = list(dict.fromkeys(todas_colunas))  # Remove duplicatas mantendo a ordem

    return todas_colunas

# Função para processar colunas aplicando remove_espacos e separa_ids
def processar_colunas(df, colunas_encontradas):
    colunas_excluidas = ['ID','ETIQUETA NACIONAL','Etiqueta Nacional' ,'LEMBRETE', 'Lembrete']
    for coluna in colunas_encontradas:
        if coluna not in colunas_excluidas:
            df[coluna] = df[coluna].apply(lambda x: separa_ids(x))
    return df

# Função para agrupar colunas por número final e criar novas colunas "MODELO"
def agrupar_por_fase(df, colunas_encontradas):
    colunas_por_numero = {}
    for coluna in colunas_encontradas:
        numero = ''.join([char for char in coluna if char.isdigit()])
        if numero:
            if numero not in colunas_por_numero:
                colunas_por_numero[numero] = []
            colunas_por_numero[numero].append(coluna)

    for numero, colunas in colunas_por_numero.items():
        nova_coluna = f'MODELO{numero}'
        df[nova_coluna] = df[colunas].apply(lambda row: ', '.join(row.dropna().astype(str).replace('', pd.NA).dropna()), axis=1)

    return df

# Função para salvar apenas as colunas "MODELO" e "ETIQUETA NACIONAL" ou "LEMBRETE"
def salvar_arquivo_excel_filtrado(df):
    colunas_fase = [col for col in df.columns if col.startswith('MODELO') or col.startswith('Duplicados')]

    if 'ETIQUETA NACIONAL' in df.columns:
        colunas_fase.append('ETIQUETA NACIONAL')        
    elif 'LEMBRETE' in df.columns:
        colunas_fase.append('LEMBRETE')
    elif 'Etiqueta Nacional' in df.columns:
        colunas_fase.append('Etiqueta Nacional')
    elif 'Lembrete' in df.columns:
        colunas_fase.append('Lembrete')

    if 'ID' in df.columns:
        colunas_fase.append('ID')

    df_filtrado = df[colunas_fase]

    # Criar um objeto BytesIO para salvar o arquivo em memória
    output = BytesIO()
    
    try:
        df_filtrado.to_excel(output, index=False)
        output.seek(0)  # Move o cursor para o início do buffer
        return output  # Retorna o arquivo em memória
    except Exception as e:
        raise Exception(f"Erro ao salvar o arquivo: {e}")

# Função para identificar e separar IDs duplicados dentro e entre colunas "MODELO"
def verificar_duplicatas_entre_colunas(df):
    todos_ids = []
    for coluna in df.columns:
        if coluna.startswith('MODELO'):
            ids_coluna = df[coluna].dropna().str.split(', ').sum()  # Extrair todos os IDs
            todos_ids.extend(ids_coluna)

    ids_duplicados = set([id_ for id_ in todos_ids if todos_ids.count(id_) > 1])

    for coluna in df.columns:
        if coluna.startswith('MODELO'):
            df[f'Duplicados {coluna}'] = df[coluna].apply(lambda x: ', '.join([id_ for id_ in x.split(', ') if id_ in ids_duplicados]) if pd.notna(x) else '')
            df[coluna] = df[coluna].apply(lambda x: ', '.join([id_ for id_ in x.split(', ') if id_ not in ids_duplicados]) if pd.notna(x) else '')
    
    return df

# Rota para salvar o arquivo Excel
@app.route('/salvar_excel', methods=['POST'])
def salvar_excel():
    try:
        if 'df' in session:
            df = pd.DataFrame(session['df'])  # Recarregar o DataFrame da sessão
        else:
            return "Nenhum arquivo foi processado para salvar.", 400

        # Identificar e processar colunas
        padroes_colunas = ['ORIENTAÇÃO', 'OBSERVAÇÃO', 'Orientação', 'Observação']
        colunas_encontradas = identificar_colunas(df, padroes_colunas)

        if not colunas_encontradas:
            return "Nenhuma coluna correspondente foi encontrada no arquivo.", 400

        # Processar colunas
        df_processado = processar_colunas(df, colunas_encontradas)

        # Agrupar colunas por fase
        df_agrupado = agrupar_por_fase(df_processado, colunas_encontradas)

        # Verificar e separar duplicatas entre colunas
        df_verificado = verificar_duplicatas_entre_colunas(df_agrupado)

        # Salvar o arquivo final
        output = salvar_arquivo_excel_filtrado(df_verificado)

        return send_file(output, as_attachment=True, download_name="dados_processados.xlsx",
                         mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    except Exception as e:
        return f"Erro ao salvar o arquivo: {e}", 500

# Rota para simular o progresso do carregamento
@app.route('/start_processo_carregar')
def start_processo_carregar():
    def carregar_tarefa_longa():
        global progresso_carregar
        progresso_carregar = 0

        for i in range(1, 11):  # Simula um processo longo com 10 etapas
            time.sleep(1)
            progresso_carregar = i * 10  # Incrementa o progresso em 10%
            yield f"data:{progresso_carregar}\n\n"
        progresso_carregar = 100  # Finaliza o progresso em 100%

    return Response(carregar_tarefa_longa(), mimetype='text/event-stream')

# Rota para simular o progresso do salvamento
@app.route('/start_processo_salvar')
def start_processo_salvar():
    def salvar_tarefa_longa():
        global progresso_salvar
        progresso_salvar = 0

        for i in range(1, 11):  # Simula um processo longo com 10 etapas
            time.sleep(1)
            progresso_salvar = i * 10  # Incrementa o progresso em 10%
            yield f"data:{progresso_salvar}\n\n"
        progresso_salvar = 100  # Finaliza o progresso em 100%

    return Response(salvar_tarefa_longa(), mimetype='text/event-stream')


# Rota para encerrar o servidor Flask
@app.route('/desligar_servidor', methods=['POST'])
def shutdown():
    def delayed_shutdown():
        time.sleep(2)  # Pequeno atraso de 1 segundo
        os.kill(os.getpid(), signal.SIGINT)
    
    threading.Thread(target=delayed_shutdown).start()
    return 'Servidor desligando...', 200  # Envia resposta ao cliente

# Inicialização da aplicação Flask
if __name__ == '__main__':
    app.run(debug=False)
