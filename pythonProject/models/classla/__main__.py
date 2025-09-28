#type: ignore
import classla
from pathlib import Path

classla.download('sr')

model = classla.Pipeline('sr')

data = "Ovo je primer recenica. Aleksa Vuckovic putuje u Berlin."
output = model(data)
conllu = output.to_conll()


