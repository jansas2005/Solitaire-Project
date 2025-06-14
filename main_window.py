import random
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QAction, QMessageBox
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

from card_widgets import CardWidget, DropPlaceholder, CardColumnWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pasjans Klondike")
        self.setGeometry(100, 100, 1200, 800)
        self.setup_ui()
        self.init_menu()
        self.init_game()

    def setup_ui(self):
        central_widget = QWidget()
        central_widget.setStyleSheet("""
            QWidget {
                background-color: #0b6623;
                background-image:
                    radial-gradient(rgba(255,255,255,0.05) 10%, transparent 11%),
                    radial-gradient(rgba(0,0,0,0.1) 10%, transparent 11%);
                background-position: 0 0, 5px 5px;
                background-repeat: repeat;
            }
            QPushButton {
                background-color: white;
                border: 1px solid #888;
                padding: 5px 10px;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Górny rząd: Stock, Waste, Foundations
        top_row = QHBoxLayout()

        self.stock = DropPlaceholder("STOCK")
        self.stock.setObjectName("stock")
        self.stock.clicked.connect(self.draw_card)

        self.waste = DropPlaceholder("WASTE")
        self.waste.setObjectName("waste")

        top_row.addWidget(self.stock)
        top_row.addWidget(self.waste)
        top_row.addStretch()

        self.foundations = []
        for i in range(4):
            f = DropPlaceholder(f"F{i+1}")
            f.setObjectName(f"foundation_{i+1}")
            top_row.addWidget(f)
            self.foundations.append(f)

        # Tableau: 7 kolumn
        tableau_row = QHBoxLayout()
        self.tableau_columns = []
        for i in range(7):
            col = CardColumnWidget()
            col.setObjectName(f"tableau_{i+1}")
            tableau_row.addWidget(col)
            self.tableau_columns.append(col)

        # Przyciski
        button_row = QHBoxLayout()
        self.new_game_btn = QPushButton("🎲 Nowa gra")
        self.undo_btn = QPushButton("⏪ Cofnij")
        self.exit_btn = QPushButton("❌ Wyjście")

        self.new_game_btn.clicked.connect(self.start_new_game)
        self.undo_btn.clicked.connect(self.undo_move)
        self.exit_btn.clicked.connect(self.close)

        button_row.addWidget(self.new_game_btn)
        button_row.addWidget(self.undo_btn)
        button_row.addStretch()
        button_row.addWidget(self.exit_btn)

        main_layout.addLayout(top_row)
        main_layout.addSpacing(20)
        main_layout.addLayout(tableau_row)
        main_layout.addStretch()
        main_layout.addLayout(button_row)

    def init_menu(self):
        menu = self.menuBar()
        help_menu = menu.addMenu("⚙️ Ustawienia")

        help_action = QAction("❓ Pomoc", self)
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)

    def show_help(self):
        QMessageBox.information(self, " Ustawienia",
            "🎯 Cel gry:\n"
            "Ułóż wszystkie karty w czterech stosach (kolorami i rosnąco od Asa do Króla).\n\n"
            "🃏 Zasady:\n"
            "- Odkładaj naprzemienne kolory w kolumnach malejąco.\n"
            "- Można przenosić ciągi kart lub pojedyncze karty.\n"
            "- Kliknięcie na zakrytą kartę odkrywa ją.\n"
            "- Kliknięcie na STOCK dobiera kartę do WASTE.\n\n"
            "Powodzenia!"
        )

    def init_game(self):
        suits = ['żołędź', 'serce', 'diament', 'wino']
        ranks = ['A'] + [str(n) for n in range(2, 11)] + ['J', 'Q', 'K']
        deck = [(suit, rank) for suit in suits for rank in ranks]
        random.shuffle(deck)
        self.card_stack = deck
        self.clear_tableau()
        self.deal_initial_cards()

    def draw_card(self):
        if self.card_stack:
            card_data = self.card_stack.pop(0)

            for child in self.waste.children():
                if isinstance(child, CardWidget):
                    child.close()

            new_card = CardWidget(card_data, parent=self.waste)
            new_card.move(0, 0)
            new_card.show()

    def start_new_game(self):
        self.init_game()
        QMessageBox.information(self, "Nowa gra", "Rozpoczęto nową grę.")

    def undo_move(self):
        QMessageBox.information(self, "Cofnij", "Cofanie ruchów jeszcze niezaimplementowane.")
   
    def deal_initial_cards(self):
        for i in range(7):
            for j in range(i + 1):
                card_data = self.card_stack.pop(0)
                face_up = (j == i)  # tylko ostatnia karta w kolumnie ma być odkryta

                if face_up:
                    card = CardWidget(card_data, parent=self.tableau_columns[i])
                else:
                    card = CardWidget(('tył_karty', ''), parent=self.tableau_columns[i])
                    card.card_data = card_data  # zapamiętaj prawdziwą kartę

                y_offset = 10 + j * 30
                card.move(10, y_offset)
                card.show()
                self.tableau_columns[i].cards.append(card)
        
    def clear_tableau(self):
        for column in self.tableau_columns:
            for card in column.cards:
                card.setParent(None)
                card.deleteLater()
            column.cards.clear()