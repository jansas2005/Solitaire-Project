# game_logic.py
import random

class GameLogic:
    """
    Zarządza stanem i logiką gry. Używa nazw kolorów zgodnych z plikami graficznymi.
    """
    def __init__(self):
        # Używamy nazw, których oczekują pliki graficzne w card_widgets
        self.suits = ['wino', 'serce', 'diament', 'żołędź']
        self.ranks = ['A'] + [str(n) for n in range(2, 11)] + ['J', 'Q', 'K']
        self.rank_values = {rank: i for i, rank in enumerate(self.ranks, 1)}
        self.card_colors = {
            'wino': 'black', 'żołędź': 'black',
            'serce': 'red', 'diament': 'red'
        }
        self.new_game()

    def new_game(self):
        """ Inicjalizuje i rozpoczyna nową grę. """
        full_deck = [{'suit': s, 'rank': r, 'face_up': False} for s in self.suits for r in self.ranks]
        random.shuffle(full_deck)

        self.stock = full_deck
        self.waste = []
        self.foundations = [[] for _ in range(4)]
        self.tableau = [[] for _ in range(7)]

        for i in range(7):
            for j in range(i + 1):
                card = self.stock.pop()
                if j == i:
                    card['face_up'] = True
                self.tableau[i].append(card)

    def draw_from_stock(self):
        """ Dobiera kartę ze stocku do waste lub odwraca waste. """
        if not self.stock:
            self.stock = self.waste[::-1]
            for card in self.stock:
                card['face_up'] = False
            self.waste = []
            return True

        card = self.stock.pop()
        card['face_up'] = True
        self.waste.append(card)
        return True

    def attempt_move(self, card_stack, source, destination):
        """ Próbuje przenieść stos kart. Zwraca True jeśli się udało. """
        source_type, source_idx = source
        dest_type, dest_idx = destination

        is_valid = False
        if dest_type == 'foundation':
            if len(card_stack) == 1: # Na fundament można przenosić tylko pojedyncze karty
                is_valid = self.is_valid_for_foundation(card_stack[0], dest_idx)
        elif dest_type == 'tableau':
            is_valid = self.is_valid_for_tableau(card_stack[0], dest_idx)

        if is_valid:
            self.perform_move(card_stack, source, destination)
            return True
        return False

    def perform_move(self, card_stack, source, destination):
        """ Wykonuje przeniesienie kart i odkrywa nową kartę w tableau. """
        source_type, source_idx = source
        dest_type, dest_idx = destination

        # Usuń karty ze źródła
        if source_type == 'waste':
            self.waste.pop()
        elif source_type == 'foundation':
            self.foundations[source_idx].pop()
        elif source_type == 'tableau':
            num_to_move = len(card_stack)
            self.tableau[source_idx] = self.tableau[source_idx][:-num_to_move]
            # KLUCZOWE: Odkryj nową wierzchnią kartę, jeśli jest zakryta
            if self.tableau[source_idx] and not self.tableau[source_idx][-1]['face_up']:
                self.tableau[source_idx][-1]['face_up'] = True

        # Dodaj karty do celu
        if dest_type == 'foundation':
            self.foundations[dest_idx].extend(card_stack)
        elif dest_type == 'tableau':
            self.tableau[dest_idx].extend(card_stack)
            
    def auto_move_to_foundation(self, source_info):
        """ Próbuje automatycznie przenieść kartę na odpowiedni fundament. """
        source_type, source_idx, card_idx = source_info

        if source_type == 'tableau':
            # Możemy przenosić tylko wierzchnią kartę ze stosu
            if card_idx != len(self.game.tableau[source_idx]) - 1:
                return False
            card = self.game.tableau[source_idx][-1]
        elif source_type == 'waste':
            if not self.game.waste: return False
            card = self.game.waste[-1]
        else:
            return False

        # Znajdź pasujący fundament
        for i in range(4):
            if self.is_valid_for_foundation(card, i):
                self.perform_move([card], (source_type, source_idx), ('foundation', i))
                return True
        return False


    def is_valid_for_foundation(self, card, foundation_index):
        """ Sprawdza, czy karta może być położona na danym fundamencie. """
        foundation_pile = self.foundations[foundation_index]
        if not foundation_pile:
            return card['rank'] == 'A'
        
        top_card = foundation_pile[-1]
        return (card['suit'] == top_card['suit'] and
                self.rank_values[card['rank']] == self.rank_values[top_card['rank']] + 1)

    def is_valid_for_tableau(self, card, tableau_index):
        """ Sprawdza, czy karta może być położona w danej kolumnie tableau. """
        tableau_pile = self.tableau[tableau_index]
        if not tableau_pile:
            return card['rank'] == 'K'

        top_card = tableau_pile[-1]
        if not top_card['face_up']: return False

        return (self.card_colors[card['suit']] != self.card_colors[top_card['suit']] and
                self.rank_values[card['rank']] == self.rank_values[top_card['rank']] - 1)

    def check_win_condition(self):
        """ Sprawdza, czy gra została wygrana. """
        return all(len(f) == 13 for f in self.foundations)