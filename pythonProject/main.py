from reldi_tokeniser.tokeniser import ReldiTokeniser, tokenize

text = "Nikola Tesla je rođen u Smiljanu."

# Inicijalizacija tokenizatora
reldi = ReldiTokeniser(lang='sr')

# Dobijamo listu tokena
tokens = tokenize(reldi.tokenizer, text)

print("Tokeni:", [t[0] for t in tokens])
print("Broj tokena:", len(tokens))
