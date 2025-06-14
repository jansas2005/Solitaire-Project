import sys
import random
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
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
        self.setup_menu()  # <-- Dodane tu
        self.statusBar().showMessage("🟢 Gotowe do gry")

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # 🔹 Górny rząd: Stock, Waste, Foundations
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

        # 🔸 Tableau: 7 kolumn
        tableau_row = QHBoxLayout()
        self.tableau_columns = []
        for i in range(7):
            col = CardColumnWidget()
            col.setObjectName(f"tableau_{i+1}")
            tableau_row.addWidget(col)
            self.tableau_columns.append(col)

        # 🔻 Przyciski
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

        # Składamy wszystko razem
        main_layout.addLayout(top_row)
        main_layout.addSpacing(20)
        main_layout.addLayout(tableau_row)
        main_layout.addStretch()
        main_layout.addLayout(button_row)

        # 🔁 Talia kart
        suits = ['spades', 'hearts', 'diamonds', 'clubs']
        ranks = ['A'] + [str(n) for n in range(2, 11)] + ['J', 'Q', 'K']
        deck = [(suit, rank) for suit in suits for rank in ranks]
        random.shuffle(deck)
        self.card_stack = deck

    def setup_menu(self):
        menu_bar = self.menuBar()
        options_menu = menu_bar.addMenu("⚙️ Opcje")

        new_game_action = QAction("🎲 Nowa gra", self)
        exit_action = QAction("❌ Wyjście", self)
        help_action = QAction("❓ Pomoc", self)

        new_game_action.triggered.connect(self.start_new_game)
        exit_action.triggered.connect(self.close)
        help_action.triggered.connect(self.show_help)

        options_menu.addAction(new_game_action)
        options_menu.addAction(exit_action)
        options_menu.addSeparator()
        options_menu.addAction(help_action)

    def show_help(self):
        help_text = (
            "📜 Zasady Pasjansa Klondike:\n\n"
            "• Celem gry jest przeniesienie wszystkich kart na 4 stosy,\n"
            "  każdy rosnąco od Asa do Króla, w jednym kolorze.\n\n"
            "• Można przenosić karty między 7 kolumnami w porządku malejącym\n"
            "  i naprzemiennych kolorach (np. czarna 7 na czerwoną 8).\n\n"
            "• Tylko Król może zostać przeniesiony na puste miejsce kolumny.\n"
            "• Z talii możesz dobierać karty na stos odrzuconych.\n"
            "• Grę wygrywasz, jeśli uda ci się ułożyć wszystkie 52 karty na 4 stosach.\n"
        )
        QMessageBox.information(self, "Pomoc - Zasady gry", help_text)

    def draw_card(self):
        if self.card_stack:
            card_data = self.card_stack.pop(0)

            for child in self.waste.children():
                if isinstance(child, CardWidget):
                    child.close()

            new_card = CardWidget(card_data, QPixmap("cards/AS.png"), parent=self.waste)
            new_card.move(0, 0)
            new_card.show()

    def start_new_game(self):
        QMessageBox.information(self, "Nowa gra", "Rozpoczęto nową grę (logika jeszcze niezaimplementowana).")

    def undo_move(self):
        QMessageBox.information(self, "Cofnij", "Cofanie ruchów jeszcze niezaimplementowane.")
