import nltk
import sys
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer
from nltk.tokenize import word_tokenize

nltk.download('stopwords')
nltk.download('rslp')
nltk.download('punkt')


# Carregando a lista de stopwords
stopwordsPt = set(stopwords.words('portuguese'))
indiceInvertido = {}
stemmer = RSLPStemmer()

# def dividirTextoEmPalavras(texto):
#     texto = ' '.join(texto.split())
#     caracteresSeparadores = ".,...,!?"
#     for separador in caracteresSeparadores:
#         texto = texto.replace(separador, ' ')
#     palavras = texto.lower().split()
#     return palavras

def lerConsulta():
    consulta = ""
    try:
        with open("consulta.txt", "r") as arquivo_consulta:
            consulta = arquivo_consulta.read().strip()
    except FileNotFoundError as e:
        print(f"Erro para encontrar o arquivo de consulta: {e}")
    return consulta

def processarConsulta(query):
    query_terms = word_tokenize(query.lower())
    resultado = set()
    operador = None

    for termo in query_terms:
        if termo == '&':
            operador = 'AND'
        elif termo == '|':
            operador = 'OR'
        elif termo == '!':
            operador = 'NOT'
        else:
            termo = stemmer.stem(termo)  # Lematização do termo
            termo_docs = indiceInvertido.get(termo, set())

            if operador is None:
                resultado.update(termo_docs)
            elif operador == 'AND':
                resultado.intersection_update(termo_docs)
            elif operador == 'OR':
                resultado.update(termo_docs)
            elif operador == 'NOT':
                resultado.difference_update(termo_docs)

            operador = None

    return resultado

try:
    if len(sys.argv) != 2:
        print("Uso: python script.py base.txt")
    else:
        arquivo_base = sys.argv[1]
        with open('indice.txt', 'w') as arquivo:
            # Fazendo a leitura da base de dados
            with open(arquivo_base, 'r') as album:
                numeroFaixa = 1
                for faixa in album:
                    faixa = faixa.strip()
                    with open(f'C:/Users/joaop/OneDrive - Universidade Federal de Uberlândia/É O PROGRAMAS/Faculdade/ORI/Trab1ORI/base_samba/{faixa}', 'r') as arquivoFaixa:
                        for letra in arquivoFaixa:
                            palavras = word_tokenize(letra.lower())
                            for palavra in palavras:
                                # Verifica se não é uma stopword
                                if palavra not in stopwordsPt:
                                    # Tira o radical
                                    radical = stemmer.stem(palavra)
                                    # Verifica se o radical já está no dicionário da faixa
                                    if radical in indiceInvertido:
                                        # Se já está, atualiza a contagem da faixa
                                        if numeroFaixa in indiceInvertido[radical]:
                                            indiceInvertido[radical][numeroFaixa] += 1
                                        else:
                                            indiceInvertido[radical][numeroFaixa] = 1
                                    else:
                                        # Se não está, cria a entrada para o radical na faixa
                                        indiceInvertido[radical] = {numeroFaixa: 1}
                    numeroFaixa += 1

            # Escreve o índice invertido no arquivo
            for radical, faixas in indiceInvertido.items():
                arquivo.write(f"{radical}: ")
                for faixa, contagem in faixas.items():
                    arquivo.write(f"{faixa},{contagem} ")
                arquivo.write("\n")

        # Lê a consulta
        consulta = lerConsulta()
        print(consulta)

        # Processa a consulta
        resultado = processarConsulta(consulta)
    resultadoString = ", ".join(map(str, resultado))

    with open('resposta.txt', 'w') as arquivoResposta:
        arquivoResposta.write(f"{len(resultado)}\n")
        arquivoResposta.write(resultadoString)

except FileNotFoundError as e:
    print(f"Erro para encontrar o arquivo: {e}")
except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")