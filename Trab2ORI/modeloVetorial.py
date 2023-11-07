import math
import nltk
import sys
import os
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer
from nltk.tokenize import word_tokenize
from math import log10

nltk.download('stopwords')
nltk.download('rslp')
nltk.download('punkt')

# Carregando a lista de stopwords
stopwordsPt = set(stopwords.words('portuguese'))
# Dicionário p índice invertido
indiceInvertido = {}
pesos = []
pesosDocumento = {}
stemmer = RSLPStemmer()
pontos = ['!' ,'?' , ',', '.']
faixas = []  # Lista para armazenar nomes de faixas

def leConsulta(arquivoConsulta):
    with open(arquivoConsulta, 'r') as arquivoConsulta:
            consulta = arquivoConsulta.read().strip()
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
            termoDocs = indiceInvertido.get(termo, set())

            if operador is None:
                resultado.update(termoDocs)
            elif operador == 'AND':
                resultado.intersection_update(termoDocs)
            elif operador == 'OR':
                resultado.update(termoDocs)
            elif operador == 'NOT':
                resultado.difference_update(termoDocs)

            operador = None

    return resultado

def calculaTF(frequenciaTermo):
    return 0 if frequenciaTermo == 0 else 1 + math.log10(frequenciaTermo)

def calculaTFIDF(frequenciaTermo, frequenciaTermoInversa):
    return calculaTF(frequenciaTermo)*frequenciaTermoInversa

def escrevePesos(pesos):
    with open('pesos.txt', 'w') as arquivoPesos:
        for faixa, pesos_faixa in pesos.items():
            arquivoPesos.write(f"{faixa}: ")
            for termo, valor in pesos_faixa.items():
                arquivoPesos.write(f"{termo}, {valor} ")
            arquivoPesos.write("\n")

try:
    if len(sys.argv) != 3:
        print("Preciso de 3 argumentos sendo eles: nome do script.py, nome da base.txt, nome da consulta.txt")
    else:
        arquivoBase = sys.argv[1]
        arquivoConsulta = sys.argv[2]
        # Obtendo o diretório atual do script
        diretorioAtual = os.path.dirname(os.path.abspath(__file__))
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
                                arquivoPesos.write(f"{radical}, {tfidf} ")
                        arquivoPesos.write("\n")


            # Escreve o índice invertido no arquivo
            for radical, faixas_dict in indiceInvertido.items():
                if radical not in pontos:
                    arquivo.write(f"{radical}: ")
                    for faixa, contagem in faixas_dict.items():
                        arquivo.write(f"{faixas[faixa - 1]} ({contagem} vezes), ")  # Obtém o nome da faixa correspondente
                    arquivo.write("\n")

        consulta = leConsulta(arquivoConsulta)

        # Processa a consulta
        resultado = processarConsulta(consulta)

    # Abre o arquivo de resposta e escreve os nomes das faixas correspondentes
    with open('resposta.txt', 'w') as arquivoResposta:
        arquivoResposta.write(f"{len(resultado)}\n")
        # Obtém os nomes das faixas correspondentes
        nomes_faixas = [faixas[numero - 1] for numero in resultado]  
        resultadoString = "\n".join(nomes_faixas)
        arquivoResposta.write(resultadoString)


    

except FileNotFoundError as e:
    print(f"Erro para encontrar o arquivo: {e}")
except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}") 