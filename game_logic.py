# game_logic.py
import random

class GameLogic:
    def __init__(self):
        self.suits = ['wino', 'serce', 'diament', 'żołędź']
        self.ranks = ['A'] + [str(n) for n in range(2, 11)] + ['J', 'Q', 'K']
        self.rank_values = {rank: i for i, rank in enumerate(self.ranks, 1)}
        self.card_colors = {
            'wino': 'black', 'żołędź': 'black',
            'serce': 'red', 'diament': 'red'
        }
        
        # ZMIANA: Definiujemy, jaki kolor należy do którego fundamentu.
        # Kolejność MUSI odpowiadać symbolom w MainWindow: ♠, ♥, ♦, ♣
        self.foundation_suits = ['wino', 'serce', 'diament', 'żołędź']
        
        self.new_game()

    def new_game(self):
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
        source_type, source_idx = source
        dest_type, dest_idx = destination

        is_valid = False
        if dest_type == 'foundation':
            if len(card_stack) == 1:
                is_valid = self.is_valid_for_foundation(card_stack[0], dest_idx)
        elif dest_type == 'tableau':
            is_valid = self.is_valid_for_tableau(card_stack[0], dest_idx)

        if is_valid:
            self.perform_move(card_stack, source, destination)
            return True
        return False

    def perform_move(self, card_stack, source, destination):
        source_type, source_idx = source
        dest_type, dest_idx = destination

        if source_type == 'waste': self.waste.pop()
        elif source_type == 'foundation': self.foundations[source_idx].pop()
        elif source_type == 'tableau':
            num_to_move = len(card_stack)
            self.tableau[source_idx] = self.tableau[source_idx][:-num_to_move]
            if self.tableau[source_idx] and not self.tableau[source_idx][-1]['face_up']:
                self.tableau[source_idx][-1]['face_up'] = True

        if dest_type == 'foundation': self.foundations[dest_idx].extend(card_stack)
        elif dest_type == 'tableau': self.tableau[dest_idx].extend(card_stack)

    def is_valid_for_foundation(self, card, foundation_index):
        foundation_pile = self.foundations[foundation_index]
        
        # ZMIANA: Sprawdzamy oczekiwany kolor dla danego fundamentu
        expected_suit = self.foundation_suits[foundation_index]

        if not foundation_pile:
            # Na pusty fundament można położyć tylko pasującego Asa
            return card['rank'] == 'A' and card['suit'] == expected_suit
        
        top_card = foundation_pile[-1]
        # Karta musi być tego samego koloru co fundament i o jeden stopień wyższa
        return (card['suit'] == expected_suit and
                self.rank_values[card['rank']] == self.rank_values[top_card['rank']] + 1)

    def is_valid_for_tableau(self, card, tableau_index):
        tableau_pile = self.tableau[tableau_index]
        if not tableau_pile:
            return card['rank'] == 'K'

        top_card = tableau_pile[-1]
        if not top_card['face_up']: return False

        return (self.card_colors[card['suit']] != self.card_colors[top_card['suit']] and
                self.rank_values[card['rank']] == self.rank_values[top_card['rank']] - 1)

    def check_win_condition(self):
        return all(len(f) == 13 for f in self.foundations)