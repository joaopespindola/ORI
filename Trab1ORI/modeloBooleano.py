import nltk
import sys
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer
nltk.download('stopwords')
nltk.download('rslp')
#carregando a lista de stopwords
stopwordsPt = set(stopwords.words('portuguese'))
indiceInvertido = {}
stemmer = RSLPStemmer()

def dividirTextoEmPalavras(texto):
    texto = ' '.join(texto.split())
    caracteresSeparadores = ".,...,!?" 
    for separador in caracteresSeparadores:
        # Realiza a substituição de todos os caracteres no texto que correspondem ao valor da variável separador por um espaço em branco.
        texto = texto.replace(separador, ' ')
    palavras = texto.lower().split()
    return palavras

try:
    if len(sys.argv) != 2:
        print("Uso: python script.py base.txt")
    else:
        arquivo_base = sys.argv[1]
        with open('indice.txt', 'w') as arquivo:
            # Fazendo a leitura da base de dados
            with open(arquivo_base, 'r') as album:
                i = 1
                for faixa in album:
                    # Remove qualquer espaço em branco no início ou final da linha
                    faixa = faixa.strip()
                    with open(f'C:/Users/joaop/OneDrive - Universidade Federal de Uberlândia/É O PROGRAMAS/Faculdade/ORI/Trab1ORI/base_samba/{faixa}', 'r') as arquivoFaixa:
                        for letra in arquivoFaixa:
                            palavras = dividirTextoEmPalavras(letra)
                            for palavra in palavras:
                                indiceInvertido[faixa] = i
                            # verifica se não é uma stopword e então coloca na estrutura de indiceInvertido
                                if palavra not in stopwordsPt:    
                                        arquivo.write(stemmer.stem(palavra) + ': \n')
                                        if palavra not in indiceInvertido:
                                            indiceInvertido[palavra] = 1
                                        else:
                                            # Se a palavra já existir no dicionário, incrementa o valor
                                            indiceInvertido[palavra] += 1
                        i += 1
    print(indiceInvertido, end="\n")
                    
except FileNotFoundError as e:
    print(f"Erro para encontrar o arquivo: {e}")
except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")

