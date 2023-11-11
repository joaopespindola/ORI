import math
import nltk
import sys
import os
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer
from nltk.tokenize import word_tokenize

# Downloads necessários para a biblioteca NLTK
nltk.download('stopwords')
nltk.download('rslp')
nltk.download('punkt')

# Carregando a lista de stopwords
stopwordsPt = set(stopwords.words('portuguese'))
# Dicionário para o índice invertido
indiceInvertido = {}
# Dicionário para os pesos dos termos nos documentos
pesos = {}
# Lista para armazenar nomes de faixas
faixas = []
# Stemmer para lematização das palavras
stemmer = RSLPStemmer()
# Pontuações a serem ignoradas
pontos = ['!', '?', ',', '.']

# Função para ler a consulta de um arquivo
def leConsulta(arquivoConsulta):
    with open(arquivoConsulta, 'r') as arquivoConsulta:
        consulta = arquivoConsulta.read().strip()
    return consulta

# Função para calcular os pesos da consulta
def calcularPesosConsulta(consulta):
    pesosConsulta = {}
    query_terms = word_tokenize(consulta.lower())

    for termo in query_terms:
        if termo not in stopwordsPt:
            radical = stemmer.stem(termo)
            # Verifica se o radical existe no índice invertido
            if radical in indiceInvertido:  
                if radical in pesosConsulta:
                    pesosConsulta[radical] += 1
                else:
                    pesosConsulta[radical] = 1

    # Crie uma cópia do dicionário antes de iterar sobre ele
    for radical, frequenciaTermo in list(pesosConsulta.items()):
        if radical in indiceInvertido:  # Verifica se o radical existe no índice invertido
            frequenciaTermoInversa = math.log10(len(faixas) / len(indiceInvertido[radical]))
            tfidf = calculaTFIDF(frequenciaTermo, frequenciaTermoInversa)
            
            # Verifica se o TFIDF é diferente de zero antes de adicionar ao dicionário
            if tfidf != 0 and radical not in pontos:
                pesosConsulta[radical] = tfidf
            else:
                del pesosConsulta[radical]  # Remove o termo se o TFIDF for zero

    return pesosConsulta

# Função para calcular a similaridade entre dois conjuntos de pesos
def calculaSimilaridade(pesosConsulta, pesosDocumento):
    produtoEscalar = 0
    moduloPesosConsulta = 0
    moduloPesosDocumento = 0

    for termo, pesoConsulta in pesosConsulta.items():
        if termo in pesosDocumento:
            pesoDocumento = pesosDocumento[termo]
            produtoEscalar += pesoConsulta * pesoDocumento
        moduloPesosConsulta += pesoConsulta ** 2

    for peso in pesosDocumento.values():
        moduloPesosDocumento += peso ** 2

    moduloPesosConsulta = math.sqrt(moduloPesosConsulta)
    moduloPesosDocumento = math.sqrt(moduloPesosDocumento)

    if moduloPesosConsulta != 0 and moduloPesosDocumento != 0:
        similaridade = produtoEscalar / (moduloPesosConsulta * moduloPesosDocumento)
    else:
        similaridade = 0

    return similaridade

# Função para processar a consulta e obter o resultado
def processarConsulta(query):
    query_terms = word_tokenize(query.lower())
    resultado_final = set()
    operador = None

    for termo in query_terms:
        if termo == '&':
            operador = 'AND'
        else:
            termo = stemmer.stem(termo)
            termoDocs = indiceInvertido.get(termo, set())

            if operador is None:
                resultado_final.update(termoDocs)
            elif operador == 'AND':
                resultado_final.intersection_update(termoDocs)
            operador = None

    return resultado_final

# Função para calcular o TFIDF de um termo
def calculaTFIDF(frequenciaTermo, frequenciaTermoInversa):
    return 0 if frequenciaTermo == 0 else calculaTF(frequenciaTermo) * frequenciaTermoInversa

# Função para calcular o TF de um termo
def calculaTF(frequenciaTermo):
    return 0 if frequenciaTermo == 0 else 1 + math.log10(frequenciaTermo)

# Esse bloco é executado apenas se o script for chamado diretamente, não se for importado como um módulo
try:
    # Verifica se foram passados os argumentos corretos
    if len(sys.argv) != 3:
        print("Preciso de 3 argumentos: nome do script.py, nome da base.txt, nome da consulta.txt")
    else:
        # Obtendo o diretório atual do script
        diretorioAtual = os.path.dirname(os.path.abspath(__file__))
        
        # Nome do arquivo da base
        arquivoBase = sys.argv[1]
        
        # Nome do arquivo da consulta
        arquivoConsulta = "base1/" + sys.argv[2]

        # Abre o arquivo índice.txt para escrita
        with open('indice.txt', 'w') as arquivo:
            # Fazendo a leitura da base de dados
            with open("base1/" + arquivoBase, 'r') as album:
                numeroFaixa = 1
                for faixa in album:
                    faixa = faixa.strip()
                    # Caminho relativo para a faixa
                    faixaPath = os.path.join(diretorioAtual, 'base1', faixa)  
                    # Adiciona o nome da faixa à lista
                    faixas.append(faixa)  
                    with open(faixaPath, 'r') as arquivoFaixa:
                        for letra in arquivoFaixa:
                            palavras = word_tokenize(letra.lower())
                            for palavra in palavras:
                                # Verifica se não é uma stopword
                                if palavra not in stopwordsPt:
                                    # Tira o radical
                                    radical = stemmer.stem(palavra)
                                    
                                    if radical in indiceInvertido: 
                                        # Se já tá, atualiza a contagem da faixa
                                        if numeroFaixa in indiceInvertido[radical]:
                                            indiceInvertido[radical][numeroFaixa] += 1
                                        else:
                                            indiceInvertido[radical][numeroFaixa] = 1
                                    else:
                                        # Se não tá, cria a entrada para o radical na faixa
                                        indiceInvertido[radical] = {numeroFaixa: 1}
                    numeroFaixa += 1
            
            # Abre o arquivo pesos.txt para escrita
            with open('pesos.txt', 'w') as arquivoPesos:
                # Fazendo a leitura da base de dados
                with open("base1/" + arquivoBase, 'r') as album:
                    numeroFaixa = 1
                    for faixa in album:
                        faixa = faixa.strip()
                        # Caminho relativo para a faixa
                        faixaPath = os.path.join(diretorioAtual, 'base1', faixa)
                        # Adiciona o nome da faixa à lista
                        pesosDocumento = {}
                        with open(faixaPath, 'r') as arquivoFaixa:
                            for letra in arquivoFaixa:
                                palavras = word_tokenize(letra.lower())
                                for palavra in palavras:
                                    # Verifica se não é uma stopword
                                    if palavra not in stopwordsPt:
                                        # Tira o radical
                                        radical = stemmer.stem(palavra)
                                        if radical in pesosDocumento:
                                            pesosDocumento[radical] += 1
                                        else:
                                            pesosDocumento[radical] = 1
                        arquivoPesos.write(f"{faixa}: ")
                        for radical, frequenciaTermo in pesosDocumento.items():
                            frequenciaTermoInversa = math.log10(len(faixas) / len(indiceInvertido[radical]))
                            tfidf = calculaTFIDF(frequenciaTermo, frequenciaTermoInversa)
                            if tfidf != 0 and radical not in pontos:
                                if faixa not in pesos:
                                    pesos[faixa] = {}
                                pesos[faixa][radical] = tfidf
                                arquivoPesos.write(f"{radical}, {tfidf} ")
                        arquivoPesos.write("\n")

            # Escreve o índice invertido no arquivo
            for radical, faixas_dict in indiceInvertido.items():
                if radical not in pontos:
                    arquivo.write(f"{radical}: ")
                    for faixa, contagem in faixas_dict.items():
                        arquivo.write(f"{faixas[faixa - 1]} ({contagem} vezes), ")  # Obtém o nome da faixa correspondente
                    arquivo.write("\n")

        # Leitura da consulta
        consulta = leConsulta(arquivoConsulta)

        # Cálculo dos pesos da consulta
        pesosConsulta = calcularPesosConsulta(consulta)

        # Processamento da consulta
        resultado = processarConsulta(consulta)

        # Abre o arquivo de resposta e escreve os nomes das faixas correspondentes
        with open('resposta.txt', 'w') as arquivoResposta:
            similaridades = []
            for numero in resultado:
                faixa = faixas[numero - 1]
                similaridade = calculaSimilaridade(pesosConsulta, pesos[faixa])
                similaridades.append((faixa, similaridade))

            similaridades = sorted(similaridades, key=lambda x: x[1], reverse=True)

            arquivoResposta.write(f"{len(resultado)}\n")
            for faixa, similaridade in similaridades:
                arquivoResposta.write(f"{faixa}: {similaridade}\n")  

except FileNotFoundError as e:
    print(f"Erro para encontrar o arquivo: {e}")
