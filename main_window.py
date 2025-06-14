# main_window.py
import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QAction, QMessageBox, QApplication
)
from PyQt5.QtCore import Qt

from card_widgets import CardWidget, DropPlaceholder, CardColumnWidget
from game_logic import GameLogic


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.game = GameLogic()

        # Kolejność symboli odpowiada kolejności kolorów w self.game.foundation_suits
        self.foundation_symbols = ['♠', '♥', '♦', '♣'] 

        self.setWindowTitle("Pasjans Klondike")
        self.setGeometry(100, 100, 1200, 800)
        
        self.setup_ui()
        self.init_menu()
        self.connect_signals()
        self.update_board_from_logic()

    def setup_ui(self):
        central_widget = QWidget()
        central_widget.setStyleSheet("""
            QWidget { background-color: #0b6623; }
            QPushButton { background-color: white; border: 1px solid #888; padding: 5px 10px;
                          border-radius: 4px; min-width: 80px; }
            QPushButton:hover { background-color: #f0f0f0; }
        """)
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        top_row = QHBoxLayout()

        self.stock_placeholder = DropPlaceholder()
        self.waste_placeholder = DropPlaceholder()

        top_row.addWidget(self.stock_placeholder)
        top_row.addWidget(self.waste_placeholder)
        top_row.addStretch()

        self.foundations_placeholders = []
        for i in range(4):
            f = DropPlaceholder(label="") 
            f.setObjectName(f"foundation_{i}")
            top_row.addWidget(f)
            self.foundations_placeholders.append(f)

        tableau_row = QHBoxLayout()
        self.tableau_columns = []
        for i in range(7):
            col = CardColumnWidget()
            col.setObjectName(f"tableau_{i}")
            tableau_row.addWidget(col)
            self.tableau_columns.append(col)

        button_row = QHBoxLayout()
        self.new_game_btn = QPushButton("🎲 Nowa gra")
        self.undo_btn = QPushButton("⏪ Cofnij")
        self.exit_btn = QPushButton("❌ Wyjście")
        button_row.addWidget(self.new_game_btn); button_row.addWidget(self.undo_btn)
        button_row.addStretch(); button_row.addWidget(self.exit_btn)

        main_layout.addLayout(top_row); main_layout.addSpacing(20)
        main_layout.addLayout(tableau_row); main_layout.addStretch()
        main_layout.addLayout(button_row)

    def connect_signals(self):
        self.new_game_btn.clicked.connect(self.start_new_game)
        self.undo_btn.clicked.connect(self.undo_move)
        self.exit_btn.clicked.connect(self.close)
        self.stock_placeholder.clicked.connect(self.handle_stock_click)

        for col in self.tableau_columns:
            col.card_dropped.connect(self.handle_drop_on_tableau)
        for f in self.foundations_placeholders:
            f.card_dropped.connect(self.handle_drop_on_foundation)

    def init_menu(self):
        menu = self.menuBar()
        help_menu = menu.addMenu("⚙️ Ustawienia")
        help_action = QAction("❓ Pomoc", self)
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)

    def show_help(self):
        QMessageBox.information(self, "Pomoc",
            "🎯 Cel gry:\nUłóż wszystkie karty na czterech stosach fundamentowych (pola w prawym górnym rogu), posortowane według kolorów od Asa do Króla.\n\n"
            "🃏 Zasady:\n- W kolumnach roboczych (tableau) układaj karty malejąco, naprzemiennymi kolorami (czerwona na czarną, czarna na czerwoną).\n"
            "- Możesz przenosić pojedyncze karty lub całe, poprawnie ułożone stosy kart.\n"
            "- Kliknięcie na stos po lewej (stock) dobiera kartę.\n"
            "- Podwójne kliknięcie na karcie przeniesie ją na fundament, jeśli to możliwe.\n\n"
            "Powodzenia!"
        )

    def clear_all_cards(self):
        for placeholder in [self.stock_placeholder, self.waste_placeholder] + self.foundations_placeholders:
            for child in placeholder.findChildren(CardWidget):
                child.deleteLater()
        for column in self.tableau_columns:
            column.cards.clear()
            for child in column.findChildren(CardWidget):
                child.deleteLater()

    def update_board_from_logic(self):
        self.clear_all_cards()
        QApplication.processEvents()

        # STOCK
        if self.game.stock:
            CardWidget(('tył_karty', ''), parent=self.stock_placeholder, draggable=False).show()

        # WASTE
        if self.game.waste:
            top_card = self.game.waste[-1]
            card_data = (top_card['suit'], top_card['rank'])
            widget = CardWidget(card_data, parent=self.waste_placeholder, source=('waste', 0))
            widget.card_double_clicked.connect(self.handle_card_double_click)
            widget.show()

        # FOUNDATIONS
        for i, pile in enumerate(self.game.foundations):
            placeholder = self.foundations_placeholders[i]
            
            if not pile:
                symbol = self.foundation_symbols[i]
                placeholder.label.setText(symbol)
                # ZMIANA: Styl etykiety z symbolem. Usunęliśmy 'border: none', aby ramka widgetu była widoczna.
                placeholder.label.setStyleSheet("""
                    background: transparent;
                    color: rgba(0, 0, 0, 0.35);
                    font-size: 70px;
                    font-family: 'Times New Roman', serif;
                """)
                placeholder.label.show()
                placeholder.show() # Upewniamy się, że cały placeholder jest widoczny
            else:
                placeholder.label.hide()
                top_card = pile[-1]
                card_data = (top_card['suit'], top_card['rank'])
                CardWidget(card_data, parent=placeholder, source=('foundation', i)).show()

        # TABLEAU
        for i, pile in enumerate(self.game.tableau):
            column_widget = self.tableau_columns[i]
            if not pile:
                column_widget.placeholder.show()
            else:
                column_widget.placeholder.hide()

            for j, card_info in enumerate(pile):
                card_data = (card_info['suit'], card_info['rank'])
                is_draggable = card_info['face_up']
                display_data = card_data if is_draggable else ('tył_karty', '')
                source_id = ('tableau', i, j)
                
                widget = CardWidget(display_data, parent=column_widget, source=source_id, draggable=is_draggable)
                widget.card_double_clicked.connect(self.handle_card_double_click)
                
                y_offset = 10 + j * 30
                widget.move(10, y_offset)
                widget.show()
                column_widget.cards.append(widget)
        
        QApplication.processEvents()

    def handle_stock_click(self):
        self.game.draw_from_stock()
        self.update_board_from_logic()

    def handle_card_double_click(self, source_info):
        moved = False
        card_to_move = None
        source_type, source_idx, *rest = source_info

        if source_type == 'tableau':
            card_idx = rest[0]
            if card_idx == len(self.game.tableau[source_idx]) - 1:
                card_to_move = self.game.tableau[source_idx][card_idx]
        elif source_type == 'waste':
            if self.game.waste:
                card_to_move = self.game.waste[-1]
        
        if card_to_move:
            for i in range(4):
                if self.game.is_valid_for_foundation(card_to_move, i):
                    self.game.perform_move([card_to_move], (source_type, source_idx), ('foundation', i))
                    moved = True
                    break
        if moved:
            self.update_board_from_logic()
            if self.game.check_win_condition(): self.show_win_message()

    def handle_drop(self, source_info, destination_info):
        card_stack_to_move = []
        source_type, source_idx, *rest = source_info

        if source_type == 'tableau':
            card_idx_in_stack = rest[0]
            card_stack_to_move = self.game.tableau[source_idx][card_idx_in_stack:]
        elif source_type == 'waste' and self.game.waste:
            card_stack_to_move = [self.game.waste[-1]]
        elif source_type == 'foundation' and self.game.foundations[source_idx]:
            card_stack_to_move = [self.game.foundations[source_idx][-1]]
        
        if not card_stack_to_move: return

        if self.game.attempt_move(card_stack_to_move, (source_type, source_idx), destination_info):
            self.update_board_from_logic()
            if self.game.check_win_condition(): self.show_win_message()

    def handle_drop_on_tableau(self, source, dest_widget):
        dest_index = self.tableau_columns.index(dest_widget)
        self.handle_drop(source, ('tableau', dest_index))

    def handle_drop_on_foundation(self, source, dest_widget):
        dest_index = self.foundations_placeholders.index(dest_widget)
        self.handle_drop(source, ('foundation', dest_index))

    def start_new_game(self):
        self.game.new_game()
        self.update_board_from_logic()

    def undo_move(self):
        QMessageBox.information(self, "Cofnij", "Cofanie ruchów jeszcze niezaimplementowane.")
    
    def show_win_message(self):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Gratulacje!")
        msg_box.setText("🎉 Wygrałeś! 🎉")
        msg_box.setInformativeText("Czy chcesz rozpocząć nową grę?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.Yes)
        
        if msg_box.exec_() == QMessageBox.Yes:
            self.start_new_game()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())