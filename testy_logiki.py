from game_logic import Karta
from game_logic import Gra

class TestGry(Gra):     
    def wyswietl_stan(self):
        print("\n--- STAN GRY ---")
        print("Stos zakryty: ", len(self.stos), "kart")
        print("Stos odkryty: ", self.odrzucone[-1] if self.odrzucone else "brak")
        
        print("\nFundamenty:")
        for kolor, stos in self.fundamenty.items():
            ostatnia = stos[-1] if stos else "pusty"
            print(f"  {kolor}: {ostatnia}")
        
        print("\nKolumny:")
        for i in range(7):
            kolumna_napis = f"KOLUMNA {i}: "
            for j in self.kolumny[i]:
                if not j.widoczna:
                    kolumna_napis += "X, "
                else:
                    kolumna_napis += f"{j}, 1"
            kolumna_napis = kolumna_napis.replace(" widoczna", "")
            print(kolumna_napis)
        

def graj():
    gra = TestGry()
    
    while not gra.czy_gra_wygrana():
        gra.wyswietl_stan()
        print("\nWybierz akcję:")
        print("1 - Dobierz ze stosu")
        print("2 - Przenieś ze stosu do kolumny")
        print("3 - Przenieś ze stosu do fundamentu")
        print("4 - Przenieś z kolumny do fundamentu")
        print("5 - Przenieś między kolumnami")
        print("0 - Zakończ grę")
        
        wybor = input("Akcja: ").strip()

        if wybor == "1":
            gra.dobierz_ze_stosu()
        elif wybor == "2":
            i = int(input("Do której kolumny (0-6)? "))
            gra.przenies_ze_stosu_do_kolumny(i)
        elif wybor == "3":
            gra.przenies_ze_stosu_do_fundamentu()
        elif wybor == "4":
            i = int(input("Z której kolumny (0-6)? "))
            gra.przenies_z_kolumny_do_fundamentu(i)
        elif wybor == "5":
            z = int(input("Z kolumny (0-6): "))
            d = int(input("Do kolumny (0-6): "))
            ile = int(input("Ile kart: "))
            gra.przenies_miedzy_kolumnami(z, d, ile)
        elif wybor == "0":
            print("Zakończono grę.")
            break
        else:
            print("Nieznana opcja!")

    if gra.czy_gra_wygrana():
        print("🎉 Gratulacje! Wygrałeś grę!")

if __name__ == "__main__":
    graj()