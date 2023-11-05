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
stemmer = RSLPStemmer()
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

def calculaTFIDF(frequenciaTermo, frequenciaTermoInversa):
    return frequenciaTermo*frequenciaTermoInversa

def escrevePesos(pesos):
    with open('pesos.txt', 'w') as arquivoPesos:
        for i, peso in enumerate(pesos):
            if peso:
                nome_faixa = faixas[i]
                arquivoPesos.write(f"{nome_faixa}: ")
                for termo, valor in peso.items():
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
            with open("base_samba/" + arquivoBase, 'r') as album:
                numeroFaixa = 1
                for faixa in album:
                    faixa = faixa.strip()
                    # Caminho relativo para a faixa
                    faixaPath = os.path.join(diretorioAtual, 'base_samba', faixa)  
                    # Adiciona o nome da faixa à lista
                    faixas.append(faixa)  
                    with open(faixaPath, 'r') as arquivoFaixa:
                        for letra in arquivoFaixa:
                            palavras = word_tokenize(letra.lower())
                            pesosDocumento = {}
                            for palavra in palavras:
                                print(palavra)
                                # Verifica se não é uma stopword
                                if palavra not in stopwordsPt:
                                    # Tira o radical
                                    radical = stemmer.stem(palavra)
                                    frequenciaTermo = palavras.count(palavra)
                                    print(faixas)
                                    divisor = max(sum([1 for faixa in faixas if palavra in faixa.lower()]), 1)
                                    print(divisor)
                                    frequenciaTermoInversa = math.log10(len(faixas) / (divisor + 0.1))
                                    if frequenciaTermoInversa <= 0:
                                        frequenciaTermoInversa = 1
                                    tfidf = calculaTFIDF(frequenciaTermo, frequenciaTermoInversa)
                                    if tfidf != 0:
                                        pesosDocumento[palavra] = tfidf
                                    # Verifica se o radical já está no dicionário da faixa
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
                    pesos.append(pesosDocumento)
                escrevePesos(pesos)

            # Escreve o índice invertido no arquivo
            for radical, faixas_dict in indiceInvertido.items():
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
