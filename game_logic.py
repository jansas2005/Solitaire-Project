import random

class Karta:
    def __init__(self, kolor: str, ranga: int, widoczna: bool = False):
        kolory = ['pik', 'kier','karo','trefl']
        if kolor not in kolory:
            raise ValueError("Nieprawidlowy kolor karty")
        if not (1 <= ranga <= 13):
            raise ValueError("Nieprawidlowa wartość karty (dozwolone od 1 do 13)")
        
        self.kolor = kolor #pik, kier, karo, trefl
        self.ranga = ranga  #1-13 (As = 1, Walet = 11, Dama = 12, Król = 13)
        self.widoczna = widoczna

    def __repr__(self):
        tl = {1:'A', 11:'J', 12:'Q', 13:'K'}
        if self.ranga in tl.keys:
            wartosc = tl[self.ranga]
        else:
            wartosc = self.ranga
        return f"{wartosc} {self.suit} {'widoczna' if self.widoczna else 'niewidoczna'}"
    
    def kolor_podstawowy(self):
        return 'czerwony' if self.kolor in ['karo', 'kier'] else 'czarny'
    
class Gra:
    def __init__(self):
        self.stos = [] #Stock
        self.odrzucone = [] #Waste
        self.kolumny = [[] for i in range(7)]
        self.fundamenty = {
            'pik': [], 'kier': [], 'karo': [], 'trefl':[]
        }
        self._zacznij_gre
    
    def _zacznij_gre(self):
        kolory = ['pik', 'kier','karo','trefl']
        talia = [Karta(kolor, ranga) for kolor in kolory for ranga in range(1,14)]
        random.shuffle(talia)
        for i in range(7):
            for j in range(i+1):
                karta = talia.pop(0) #Wyciągam kartę z talii
                karta.widoczna = True if j==i else False #Karta widoczna tylko jeśli będzie z przodu
                self.kolumny[i].append(karta) #Wrzucam kartę do kolumny
        self.stos = talia #Reszta kart trafia do stosu

    def dobierz_ze_stosu(self): 
        """Wyciąganie karty ze stosu zakrytych i odlożenie jej na stos odkrytych"""
        if not self.stos and self.odrzucone:
            self.stos = self.odrzucone[::-1]
            for karta in self.stos:
                karta.widoczna = False
            self.odrzucone = [] ###
        elif self.stos:
            karta = self.stos.pop(0)
            karta.widoczna = True
            self.waste.append(karta)
    
    
    def przenies_ze_stosu_do_kolumny(self, docelowa: int):
        """Przenieś odkrytą kartę ze stosu do wybranej kolumny"""
        if not self.odrzucone: 
            return False
        karta = self.odrzucone[-1]
        k_docelowa = self.kolumny[docelowa]

        if (not k_docelowa and karta.ranga == 13) or (k_docelowa and karta.kolor_podstawowy() != k_docelowa[-1].kolor_podstawowy() and karta.ranga == k_docelowa[-1].ranga - 1): #Pusta kolumna i król
            self.odrzucone.pop()
            k_docelowa.append(karta)
            return True
        
        return False
    