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
        if not self.stos and self.odrzucone:
            self.stos = self.odrzucone[::-1]
            for karta in self.stos:
                karta.widoczna = False
            self.odrzucone = [] ###
        elif self.stos:
            karta = self.stos.pop(0)
            karta.widoczna = True
            self.waste.append(karta)
    
    def przenies_miedzy_kolumnami(self, zrodlowa: int, docelowa: int, ile_kart = 1):
        k_zrodlowa = self.kolumny[zrodlowa]
        k_docelowa = self.kolumny[docelowa]
        karty_przenoszone = k_zrodlowa[-ile_kart:] #Wybieram ostanie ile_kart elementów
        if karty_przenoszone[0].widoczna == False:
            return False #Zapobiegamy przeniesieniu zakrytych kart
        wierzchnia_karta = k_docelowa[-1] if k_docelowa else None #None, jeśli kolumna jest pusta

        if not k_docelowa:
            if karty_przenoszone[0].ranga == 13:
                k_docelowa.extend(karty_przenoszone)
                k_zrodlowa = k_zrodlowa[:-ile_kart] 
                self._odkryj_ostatnia(zrodlowa)
                return True
            return False
        
        if wierzchnia_karta.widoczna and karty_przenoszone[0].kolor_podstawowy() != wierzchnia_karta.kolor_podstawowy() and karty_przenoszone[0].ranga == wierzchnia_karta.ranga - 1:
            k_docelowa.extend(karty_przenoszone)
            k_zrodlowa = k_zrodlowa[:-ile_kart] 
            self._odkryj_ostatnia(zrodlowa)
            return True
        return False

    def _odkryj_ostania(self, indeks: int):
        kolumna = self.kolumny[indeks]
        if kolumna and kolumna[-1].widoczna:
            kolumna[-1].widoczna = True