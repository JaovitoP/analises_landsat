def ndvi(b08,b04):
    ndvi=(b08-b04)/(b08+b04)
    return ndvi

def nbr(b8A,b12):
    nbr=(b8A-b12)/(b8A+b12)
    return nbr

def nbrswir(b12,b11):
    nbrswir = (b12 - b11 - 0.02)/(b12 + b11 + 0.1)
    return nbrswir