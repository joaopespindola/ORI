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
pesosDocumentos = {}
# Lista para armazenar nomes de arquivo
nomesArquivo = []
# Stemmer para lematização das palavras
stemmer = RSLPStemmer()
# Pontuações a serem ignoradas
pontuacoesIgnoradas = ['!', '?', ',', '.']

# Função para ler a consulta de um arquivo
def lerConsulta(arquivoConsulta):
    with open(arquivoConsulta, 'r') as arquivoConsulta:
        consulta = arquivoConsulta.read().strip()
    return consulta

# Função para calcular os pesos da consulta
def calcularPesosConsulta(consulta):
    pesosConsulta = {}
    termosConsulta = word_tokenize(consulta.lower())

    for termo in termosConsulta:
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
            frequenciaTermoInversa = math.log10(len(nomesArquivo) / len(indiceInvertido[radical]))
            tfidf = calcularTFIDF(frequenciaTermo, frequenciaTermoInversa)
            
            # Verifica se o TFIDF é diferente de zero antes de adicionar ao dicionário
            if tfidf != 0 and radical not in pontuacoesIgnoradas:
                pesosConsulta[radical] = tfidf
            else:
                del pesosConsulta[radical]  # Remove o termo se o TFIDF for zero

    return pesosConsulta

# Função para calcular a similaridade entre dois conjuntos de pesos
def calcularSimilaridade(pesosConsulta, pesosDocumento):
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
    termosConsulta = word_tokenize(query.lower())
    resultado_final = set()
    operador = None

    for termo in termosConsulta:
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
def calcularTFIDF(frequenciaTermo, frequenciaTermoInversa):
    return 0 if frequenciaTermo == 0 else calcularTF(frequenciaTermo) * frequenciaTermoInversa

# Função para calcular o TF de um termo
def calcularTF(frequenciaTermo):
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
        with open('indice.txt', 'w') as arquivoIndice:
            # Fazendo a leitura da base de dados
            with open("base1/" + arquivoBase, 'r') as arquivosPasta:
                numeroArquivo = 1
                for arquivo in arquivosPasta:
                    arquivo = arquivo.strip()
                    # Caminho relativo para a arquivo
                    arquivoPath = os.path.join(diretorioAtual, 'base1', arquivo)  
                    # Adiciona o nome do arquivo à lista
                    nomesArquivo.append(arquivo)  
                    with open(arquivoPath, 'r') as arquivoFaixa:
                        for letra in arquivoFaixa:
                            palavras = word_tokenize(letra.lower())
                            for palavra in palavras:
                                # Verifica se não é uma stopword
                                if palavra not in stopwordsPt:
                                    # Tira o radical
                                    radical = stemmer.stem(palavra)
                                    
                                    if radical in indiceInvertido: 
                                        # Se já tá, atualiza a contagem do arquivo
                                        if numeroArquivo in indiceInvertido[radical]:
                                            indiceInvertido[radical][numeroArquivo] += 1
                                        else:
                                            indiceInvertido[radical][numeroArquivo] = 1
                                    else:
                                        # Se não tá, cria a entrada para o radical na faixa
                                        indiceInvertido[radical] = {numeroArquivo: 1}
                    numeroArquivo += 1
            
            # Abre o arquivo pesos.txt para escrita
            with open('pesos.txt', 'w') as arquivoPesos:
                # Fazendo a leitura da base de dados
                with open("base1/" + arquivoBase, 'r') as arquivosPasta:
                    numeroArquivo = 1
                    for arquivo in arquivosPasta:
                        arquivo = arquivo.strip()
                        # Caminho relativo para o arquivo
                        arquivoPath = os.path.join(diretorioAtual, 'base1', arquivo)
                        # Adiciona o nome do arquivo à lista
                        pesosDocumento = {}
                        with open(arquivoPath, 'r') as arquivoFaixa:
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
                        arquivoPesos.write(f"{arquivo}: ")
                        for radical, frequenciaTermo in pesosDocumento.items():
                            frequenciaTermoInversa = math.log10(len(nomesArquivo) / len(indiceInvertido[radical]))
                            tfidf = calcularTFIDF(frequenciaTermo, frequenciaTermoInversa)
                            if tfidf != 0 and radical not in pontuacoesIgnoradas:
                                if arquivo not in pesosDocumentos:
                                    pesosDocumentos[arquivo] = {}
                                pesosDocumentos[arquivo][radical] = tfidf
                                arquivoPesos.write(f"{radical}, {tfidf} ")
                        arquivoPesos.write("\n")

            # Escreve o índice invertido no arquivo
            for radical, arquivo_dict in indiceInvertido.items():
                if radical not in pontuacoesIgnoradas:
                    arquivoIndice.write(f"{radical}: ")
                    for arquivo, contagem in arquivo_dict.items():
                        arquivoIndice.write(f"{nomesArquivo[arquivo - 1]} ({contagem} vezes), ")  # Obtém o nome da faixa correspondente
                    arquivoIndice.write("\n")

        # Leitura da consulta
        consulta = lerConsulta(arquivoConsulta)

        # Cálculo dos pesos da consulta
        pesosConsulta = calcularPesosConsulta(consulta)

        # Processamento da consulta
        resultado = processarConsulta(consulta)

        # Abre o arquivo de resposta e escreve os nomes das arquivo correspondentes
        with open('resposta.txt', 'w') as arquivoResposta:
            similaridades = []
            for numero in resultado:
                arquivo = nomesArquivo[numero - 1]
                similaridade = calcularSimilaridade(pesosConsulta, pesosDocumentos[arquivo])
                similaridades.append((arquivo, similaridade))

            similaridades = sorted(similaridades, key=lambda x: x[1], reverse=True)

            arquivoResposta.write(f"{len(resultado)}\n")
            for arquivo, similaridade in similaridades:
                arquivoResposta.write(f"{arquivo}: {similaridade}\n")  

except FileNotFoundError as e:
    print(f"Erro para encontrar o arquivo: {e}")
