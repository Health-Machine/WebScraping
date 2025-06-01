import re
import ply.lex as lex
from levenshtein import levenshtein
import unicodedata
import json

swear_words = [
    "foda",
    "puta",
    "cuzão",
    "desgraçado",   
    "droga", 
    "mijo",
    "boceta",
    "buceta",
    "vagabunda",    
    "bosta",
    "babaca",       
    "veado",
    "viado",
    "filho da puta",
    "otário",       
    "prostituta",   
    "idiota",       
    "besteira",     
    "caralho",  
    "retardado",    
    "estúpido",     
    "mané",
    "covarde"
]

token_dict_with_sentiment = json.load(open('tokens.json', 'r', encoding='utf-8'))

def remover_acentos(texto):
    texto_normalizado = unicodedata.normalize('NFKD', texto)
    texto_sem_acentos = ''.join(
        c for c in texto_normalizado if not unicodedata.combining(c)
    )
    return texto_sem_acentos.lower()


tokens = ("POSITIVO", "NEGATIVO")

t_ignore = " \n\t\r"

positive_words = [remover_acentos(word) for word, sentiment in token_dict_with_sentiment.items() if sentiment == 1]
negative_words = [remover_acentos(word) for word, sentiment in token_dict_with_sentiment.items() if sentiment == 0]

def t_POSITIVO(t):
    r'|'.join(positive_words)
    return t

t_POSITIVO.__doc__ = r'|'.join(positive_words)

def t_NEGATIVO(t):
    r'|'.join(negative_words)
    return t

t_NEGATIVO.__doc__ = r'|'.join(negative_words)


def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lineno}, column {t.lexpos}")
    t.lexer.skip(1)


def normalize_text(text):
    words = re.findall(r'\w+|\S', text)
    return remover_acentos(' '.join(words)).strip().lower()

def analyze_sentiment(text):
    lexer = lex.lex()
    lexer.input(text)

    lex_positive = []
    lex_negative = []

    while True:
        tok = lexer.token()
        if not tok:
            break
        if tok.type == "POSITIVO":
            lex_positive.append(tok.value)
        elif tok.type == "NEGATIVO":
            lex_negative.append(tok.value)

    return {'pos': len(lex_positive), 'neg': len(lex_negative)}



def remove_swearword(text):
    words = text.lower().split()
    for swearword in swear_words:
        if any(levenshtein(word,swearword) <= 2 for word in words):
            text = text.replace(swearword,"")
            return normalize_text(text)
        
    return normalize_text(text)
