# Obrada prirodnih jezika – Projekat 2024/2025

## Opis projekta
Tema projekta u školskoj 2024/2025. godini je **prepoznavanje imenovanih entiteta (Named Entity Recognition – NER)** u tekstovima na srpskom jeziku.  
Cilj je implementacija **baseline pristupa** i evaluacija **naprednijih otvorenih rešenja** za NER zadatak.

Projekat se izrađuje u programskom jeziku **Python**.
Članovi tima su:
- Aleksa Vučković 2024/3040
- Milan Bogićević 2024/3056
- Milica Jevtović 2024/3113

## Faze projekta
1. **Prikupljanje podataka**
   - Tekstovi na srpskom jeziku iz više tematskih domena (novinski, književni, pravni, tviter).  
   - Minimalno 5000 tokena po domenu.  
   - Tokenizacija se vrši pomoću [ReLDI tokenizatora](https://pypi.org/project/reldi-tokeniser/).  

2. **Anotacija podataka**  
   - Ručno obeležavanje entiteta:  
     - **PER** – osobe  
     - **LOC** – lokacije  
     - **ORG** – organizacije  
   - Korišćenje **IOB2 sistema**.  

3. **Evaluacija modela**  
   - Razmatrani modeli:  
     - CLASSLA (standardni i nestandardni jezik)  
     - BERTić-NER  
     - COMtext.SR NER (ekavica)
   - Poređenje sa **baseline pristupom** zasnovanim na multinomijalnom naivnom Bajesu.  
   - Evaluacija metrikama preciznosti, odziva i F1 mere.  

## Tehnologije
- Python  
- ReLDI tokenizator  
- Simple Transformers  
- HuggingFace modeli  

## Mentor
**dr Vuk Batanović**
