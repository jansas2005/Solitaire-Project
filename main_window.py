from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QAction
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🃏 Pasjans Klondike")
        self.setGeometry(100, 100, 1024, 768)

        self.setup_ui()
        self.setup_menu()
        self.statusBar().showMessage("🟢 Gotowe do gry")

    def setup_ui(self):
        # Główne "płótno"
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Główny pionowy layout (całe okno)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # 🔹 Górna część: Stock, Waste, Foundationy
        top_row = QHBoxLayout()

        self.stock_label = QLabel("Stock")
        self.stock_label.setFixedSize(80, 120)
        self.stock_label.setStyleSheet("background-color: lightgray; border: 1px solid black;")
        self.stock_label.setAlignment(Qt.AlignCenter)

        self.waste_label = QLabel("Waste")
        self.waste_label.setFixedSize(80, 120)
        self.waste_label.setStyleSheet("background-color: lightgray; border: 1px solid black;")
        self.waste_label.setAlignment(Qt.AlignCenter)

        # 4 foundation slots
        self.foundations = []
        for i in range(4):
            label = QLabel(f"Foundation {i+1}")
            label.setFixedSize(80, 120)
            label.setStyleSheet("background-color: white; border: 1px dashed black;")
            label.setAlignment(Qt.AlignCenter)
            self.foundations.append(label)

        # Dodaj do top row
        top_row.addWidget(self.stock_label)
        top_row.addWidget(self.waste_label)
        top_row.addStretch()  # Odstęp między lewą a prawą stroną
        for foundation in self.foundations:
            top_row.addWidget(foundation)

        # 🔸 Dolna część: Tableau (7 kolumn)
        tableau_row = QHBoxLayout()
        self.tableau_columns = []
        for i in range(7):
            column = QVBoxLayout()
            placeholder = QLabel(f"Col {i+1}")
            placeholder.setFixedSize(80, 120)
            placeholder.setStyleSheet("background-color: white; border: 1px solid gray;")
            placeholder.setAlignment(Qt.AlignCenter)
            column.addWidget(placeholder)
            tableau_row.addLayout(column)
            self.tableau_columns.append(column)

        # 🔻 Przyciski na dole
        button_row = QHBoxLayout()
        self.new_game_btn = QPushButton("🎲 Nowa gra")
        self.undo_btn = QPushButton("⏪ Cofnij")
        self.exit_btn = QPushButton("❌ Wyjście")

        self.new_game_btn.clicked.connect(self.start_new_game)
        self.undo_btn.clicked.connect(self.undo_move)  # Placeholder
        self.exit_btn.clicked.connect(self.close)

        button_row.addWidget(self.new_game_btn)
        button_row.addWidget(self.undo_btn)
        button_row.addStretch()
        button_row.addWidget(self.exit_btn)

        # 🔲 Dodaj wszystkie sekcje do głównego layoutu
        main_layout.addLayout(top_row)
        main_layout.addSpacing(20)
        main_layout.addLayout(tableau_row)
        main_layout.addStretch()
        main_layout.addLayout(button_row)

    def setup_menu(self):
        menu_bar = self.menuBar()

        # Menu "Plik"
        file_menu = menu_bar.addMenu("⚙️ Opcje")

        new_game_action = QAction("🎲 Nowa gra", self)
        exit_action = QAction("❌ Wyjście", self)

        new_game_action.triggered.connect(self.start_new_game)
        exit_action.triggered.connect(self.close)

        file_menu.addAction(new_game_action)
        file_menu.addAction(exit_action)

    def start_new_game(self):
        print("TODO: Połączyć z logiką gry (Marcel)")

    def undo_move(self):
        print("Cofnij ruch - do podpięcia z logiką (Marcel)")
