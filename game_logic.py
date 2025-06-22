import random
import copy

# Główna klasa odpowiedzialna za logikę gry w pasjansa
class GameLogic:
    def __init__(self):
        """Inicjalizacja podstawowych parametrów gry"""
        self.suits = ['wino', 'serce', 'diament', 'żołędź']  # Kolory kart
        self.ranks = ['A'] + [str(n) for n in range(2, 11)] + ['J', 'Q', 'K']  # Wartości kart
        self.rank_values = {rank: i for i, rank in enumerate(self.ranks, 1)}  # Wartości numeryczne kart
        self.card_colors = {  # Przypisanie kolorów do typów kart
            'wino': 'black', 'żołędź': 'black',
            'serce': 'red', 'diament': 'red'
        }
        self.foundation_suits = ['wino', 'serce', 'diament', 'żołędź']  # Kolory dla stosów docelowych
        self.new_game()  # Rozpoczęcie nowej gry

    # Metoda inicjalizująca nową grę
    def new_game(self):
        """Przygotowanie talii i rozdanie kart"""
        full_deck = [{'suit': s, 'rank': r, 'face_up': False} for s in self.suits for r in self.ranks]
        random.shuffle(full_deck)  # Tasowanie kart

        # Inicjalizacja podstawowych obszarów gry
        self.stock = full_deck  # Nieodkryta talia
        self.waste = []  # Stos odrzuconych kart
        self.foundations = [[] for _ in range(4)]  # Stosy docelowe (4 stosy)
        self.tableau = [[] for _ in range(7)]  # Kolumny robocze (7 kolumn)

        # Rozdanie kart do kolumn roboczych
        for i in range(7):
            for j in range(i + 1):
                card = self.stock.pop()
                if j == i:  # Ostatnia karta w kolumnie jest odkryta
                    card['face_up'] = True
                self.tableau[i].append(card)

        # Inicjalizacja statystyk gry
        self.score = 0
        self.moves = 0
        self.history = []  # Historia stanów gry (dla funkcji cofnij)
        self.undo_count = 3  # Limit cofnięć

    # Metody zarządzania stanem gry
    def save_state(self):
        """Zapisywanie aktualnego stanu gry"""
        state = {
            'stock': copy.deepcopy(self.stock),
            'waste': copy.deepcopy(self.waste),
            'foundations': copy.deepcopy(self.foundations),
            'tableau': copy.deepcopy(self.tableau),
            'score': self.score,
            'moves': self.moves,
        }
        self.history.append(state)

    def undo(self):
        """Cofanie ostatniego ruchu"""
        if not self.history or self.undo_count <= 0:
            return False
        
        self.undo_count -= 1
        last_state = self.history.pop()
        # Przywracanie poprzedniego stanu
        self.stock = last_state['stock']
        self.waste = last_state['waste']
        self.foundations = last_state['foundations']
        self.tableau = last_state['tableau']
        self.score = last_state['score']
        self.moves = last_state['moves']
        return True

    # Metody obsługi ruchów w grze
    def draw_from_stock(self):
        """Dobieranie karty z talii"""
        self.save_state()
        
        if not self.stock:  # Jeśli talia pusta, odtwórz ją z odrzuconych
            if not self.waste: 
                self.history.pop()
                return False
            self.stock = self.waste[::-1]
            for card in self.stock:
                card['face_up'] = False
            self.waste = []
            self.moves += 1
            return True
        
        # Standardowe dobranie karty
        card = self.stock.pop()
        card['face_up'] = True
        self.waste.append(card)
        self.moves += 1
        return True

    # Metody walidacji i wykonywania ruchów
    def attempt_move(self, card_stack, source, destination):
        """Próba wykonania ruchu z walidacją"""
        source_type, source_idx = source
        dest_type, dest_idx = destination

        is_valid = False
        if dest_type == 'foundation':  # Ruch na stos docelowy
            if len(card_stack) == 1:
                is_valid = self.is_valid_for_foundation(card_stack[0], dest_idx)
        elif dest_type == 'tableau':  # Ruch na kolumnę roboczą
            is_valid = self.is_valid_for_tableau(card_stack[0], dest_idx)

        if is_valid:
            self.save_state()
            self.perform_move(card_stack, source, destination)
            return True
        return False

    def perform_move(self, card_stack, source, destination):
        """Fizyczne wykonanie ruchu i aktualizacja punktacji"""
        source_type, source_idx = source
        dest_type, dest_idx = destination

        # Usuwanie kart ze źródła
        if source_type == 'waste': self.waste.pop()
        elif source_type == 'foundation': 
            self.foundations[source_idx].pop()
            self.score -= 15  # Kara za cofnięcie ze stosu docelowego
        elif source_type == 'tableau':
            num_to_move = len(card_stack)
            self.tableau[source_idx] = self.tableau[source_idx][:-num_to_move]
            # Odkrywanie nowej karty w kolumnie jeśli potrzeba
            if self.tableau[source_idx] and not self.tableau[source_idx][-1]['face_up']:
                self.tableau[source_idx][-1]['face_up'] = True
                self.score += 5  # Nagroda za odkrycie karty

        # Dodawanie kart do celu
        if dest_type == 'foundation': 
            self.foundations[dest_idx].extend(card_stack)
            self.score += 10  # Nagroda za ruch na stos docelowy
        elif dest_type == 'tableau': 
            self.tableau[dest_idx].extend(card_stack)
            if source_type == 'waste':
                self.score += 5  # Nagroda za ruch z odrzuconych
        
        self.moves += 1
        if self.score < 0:  # Zabezpieczenie przed ujemną punktacją
            self.score = 0

    # Metody walidacyjne
    def is_valid_for_foundation(self, card, foundation_index):
        """Sprawdza czy karta może być położona na stos docelowy"""
        foundation_pile = self.foundations[foundation_index]
        expected_suit = self.foundation_suits[foundation_index]
        if not foundation_pile:  # Pusty stos - tylko as
            return card['rank'] == 'A' and card['suit'] == expected_suit
        top_card = foundation_pile[-1]
        return (card['suit'] == expected_suit and
                self.rank_values[card['rank']] == self.rank_values[top_card['rank']] + 1)

    def is_valid_for_tableau(self, card, tableau_index):
        """Sprawdza czy karta może być położona na kolumnę roboczą"""
        tableau_pile = self.tableau[tableau_index]
        if not tableau_pile:  # Pusta kolumna - tylko król
            return card['rank'] == 'K'
        top_card = tableau_pile[-1]
        if not top_card['face_up']: return False  # Nie można kłaść na zakrytą kartę
        return (self.card_colors[card['suit']] != self.card_colors[top_card['suit']] and
                self.rank_values[card['rank']] == self.rank_values[top_card['rank']] - 1)

    def check_win_condition(self):
        """Sprawdza warunek zwycięstwa (wszystkie stosy pełne)"""
        return all(len(f) == 13 for f in self.foundations)