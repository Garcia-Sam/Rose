## ROSE

<div align='center'>
    <img src='https://github.com/user-attachments/assets/c84fde7d-68eb-4ace-ab6b-33fd53a6d9fd' alt='Ícone do Robô ROSE' width='1500px' />
</div>

Esta aplicação Python processa arquivos Excel para organizar e estruturar dados de IDs. Ela oferece funcionalidades para filtrar, classificar e agrupar as colunas correlacionadas em fases, chamadas de MODELO. A aplicação identifica e separa automaticamente os IDs únicos dos duplicados em cada fase, permitindo um controle eficiente sobre dados repetidos e melhorando a integridade das informações.

<div align='center'>
    <img src='https://github.com/user-attachments/assets/dbe3d601-3248-46ff-a273-f4560161ca43' alt='Imagem do Front-End do Robô ROSE' width='800px' />
</div>


## Arquivo de Entrada

O robô ROSE processa arquivos Excel no formato ".xlsx". Independentemente do número de colunas presentes no arquivo, apenas as seguintes colunas são obrigatórias:

    ORIENTAÇÃO | OBSERVAÇÃO | ETIQUETA NACIONAL ou LEMBRETE

## Funcionalidades

- **Agrupamento por Fases (MODELO):** Agrupa colunas relacionadas (ORIENTAÇÃO | OBSERVAÇÃO) em fases identificadas como MODELO, criando uma estrutura organizada para o conjunto de dados.

- **Filtragem e Classificação:** Filtra e classifica os dados de acordo com critérios definidos, facilitando a análise dos IDs. A formatação dos MODELOS devem seguir o padrão: ID sequenciando de um espaço e 05 ou 06 dígitos. Exs: ID 12345 ou ID 123456;

- **Identificação e Separação de Duplicados:** Identifica IDs duplicados tanto em uma única coluna quanto entre colunas distintas e os separa em colunas exclusivas para duplicados, mantendo apenas IDs únicos na coluna principal.

### Este projeto requer as seguintes bibliotecas:

#### Para gerar o executável:

- pyinstaller e/ou auto-py-to-exe. (Use o arquivo **main.py** como principal)

#### Back-end:

- Pandas: Para manipulação de dados e operações com arquivos Excel.


- Openpyxl: Para leitura e escrita de arquivos Excel.


- re (Regex): Para formatação de números de processos usando expressões regulares.

 Para facilitar, todas as dependências podem ser instaladas usando o comando abaixo.
 As dependências usadas estão no arquivo **requirements.txt**.

    python -m pip install -r requirements.txt

Se novas bibliotecas forem inclusas no projeto, pode ser necessário atualizar o arquivo **requirements.txt**. Se for esse o caso atualize com o comando abaixo:

    python -m pip freeze > requirements.txt

## Personalização

Você pode personalizar as funções no arquivo **routes.py** para adaptar o processamento às suas necessidades específicas. 

## Contribuição

Contribuições são bem-vindas!
Se você encontrar bugs ou tiver sugestões de melhorias, sinta-se à vontade para abrir uma issue ou enviar um pull request.

## Licença

Este projeto é distribuído sob a licença MIT. Consulte o arquivo **LICENSE** para obter mais informações.
