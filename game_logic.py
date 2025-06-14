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
        if self.ranga in tl.keys():
            wartosc = tl[self.ranga]
        else:
            wartosc = self.ranga
        return f"{wartosc} {self.kolor} {'widoczna' if self.widoczna else 'niewidoczna'}"
    
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
        self._zacznij_gre()
    
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
            self.odrzucone.append(karta)
    
    
    def przenies_ze_stosu_do_kolumny(self, docelowa: int):
        """Przenieś odkrytą kartę ze stosu do wybranej kolumny"""
        if not self.odrzucone: 
            return False
        karta = self.odrzucone[-1]
        k_docelowa = self.kolumny[docelowa]

        if (not k_docelowa and karta.ranga == 13) or \
            (k_docelowa and karta.kolor_podstawowy() != k_docelowa[-1].kolor_podstawowy() and karta.ranga == k_docelowa[-1].ranga - 1): #Pusta kolumna i król
            self.odrzucone.pop()
            k_docelowa.append(karta)
            return True
        
        return False
    
    def przenies_ze_stosu_do_fundamentu(self):
        """Przenieś odkrytą kartę ze stosu do fundamentu"""
        if not self.odrzucone:
            return False
        karta = self.odrzucone[-1]
        fundament = self.fundamenty[karta.kolor]
        if (not fundament and karta.ranga == 1) or  (fundament and karta.ranga == fundament[-1].ranga + 1):
            self.odrzucone.pop()
            fundament.append(karta)
            return True
        return False
    
    def przenies_z_kolumny_do_fundamentu(self, zrodlowa: int):
        """Przenieś jedną kartę z wybranej kolumny, jeśli to możliwe"""
        kolumna = self.kolumny[zrodlowa]
        if not kolumna:
            return False
        
        karta = kolumna[-1]
        fundament = self.fundamenty[karta.kolor]

        if (not fundament and karta.ranga == 1) or (fundament and karta.ranga == fundament[-1].ranga + 1):
            fundament.append(karta)
            kolumna.pop()
            self._odkryj_ostania(zrodlowa)
            return True
        return False

    def przenies_miedzy_kolumnami(self, zrodlowa: int, docelowa: int, ile_kart = 1):
        k_zrodlowa = self.kolumny[zrodlowa]
        k_docelowa = self.kolumny[docelowa]
        karty_przenoszone = k_zrodlowa[-ile_kart:] #Wybieram ostanie ile_kart elementów
        if karty_przenoszone[0].widoczna == False:
            return False #Zapobiegamy przeniesieniu zakrytych kart

        if (not k_docelowa and karty_przenoszone[0].ranga == 13) or \
            (k_docelowa and k_docelowa[-1].widoczna and karty_przenoszone[0].kolor_podstawowy() != k_docelowa[-1].kolor_podstawowy() and karty_przenoszone[0].ranga == k_docelowa[-1].ranga - 1):
            k_docelowa.extend(karty_przenoszone)
            k_zrodlowa = k_zrodlowa[:-ile_kart] 
            self._odkryj_ostatnia(zrodlowa)
            return True
        return False

    def _odkryj_ostatnia(self, indeks: int):
        kolumna = self.kolumny[indeks]
        if kolumna and kolumna[-1].widoczna:
            kolumna[-1].widoczna = True 

    def czy_gra_wygrana(self):
        for lista in self.fundamenty.values():
            if len(lista) !=13:
                return False
        return True 