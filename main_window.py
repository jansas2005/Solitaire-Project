from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QAction, QMessageBox, QApplication, QLabel
from PyQt5.QtCore import QTimer, QTime, Qt
from PyQt5.QtGui import QFont
from card_widgets import CardWidget, DropPlaceholder, CardColumnWidget
from game_logic import GameLogic


class MainWindow(QMainWindow):
    """Główne okno aplikacji pasjansa Klondike"""
    def __init__(self):
        super().__init__()
        # Inicjalizacja podstawowych komponentów gry
        self.game = GameLogic()  # Logika gry
        self.foundation_symbols = ['♠', '♥', '♦', '♣']  # Symbole dla stosów docelowych
        
        self.setup_window_properties()  # Konfiguracja właściwości okna
        
        # Przygotowanie obu widoków: ekranu startowego i widoku gry
        self.setup_splash_screen()
        self.setup_game_ui()
        
        self.init_menu()  # Inicjalizacja menu
        self.connect_signals()  # Podłączenie sygnałów
        
        # Na starcie pokaż ekran powitalny
        self.setCentralWidget(self.splash_widget)

    def setup_window_properties(self):
        """Konfiguracja podstawowych właściwości okna głównego"""
        self.setWindowTitle("Pasjans Klondike")
        self.setGeometry(100, 100, 1200, 850)
        self.timer = QTimer(self)  # Timer do pomiaru czasu gry
        self.seconds_played = 0  # Licznik sekund gry

    def setup_splash_screen(self):
        """Budowa ekranu startowego"""
        self.splash_widget = QWidget()
        self.splash_widget.setObjectName("mainWidget") # Używamy tej samej nazwy, by odziedziczyć tło
        self.set_style_sheet(self.splash_widget) # Aplikujemy ten sam arkusz stylów

        layout = QVBoxLayout(self.splash_widget)
        layout.addStretch()

        # Tytuł gry
        title_label = QLabel("Pasjans Klondike")
        title_font = QFont("Arial", 60, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("""
            color: white; 
            background: rgba(0, 0, 0, 0.4); 
            padding: 20px; 
            border-radius: 15px;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(title_label)
        layout.addSpacing(40)

        # Przyciski na ekranie startowym
        splash_buttons_layout = QHBoxLayout()
        splash_new_game_btn = QPushButton("🚀 Rozpocznij Grę")
        splash_exit_btn = QPushButton("❌ Wyjście")
        
        splash_buttons_layout.addStretch()
        splash_buttons_layout.addWidget(splash_new_game_btn)
        splash_buttons_layout.addSpacing(20)
        splash_buttons_layout.addWidget(splash_exit_btn)
        splash_buttons_layout.addStretch()
        
        layout.addLayout(splash_buttons_layout)
        layout.addStretch()
        
        # Podłączenie sygnałów dla przycisków na ekranie startowym
        splash_new_game_btn.clicked.connect(self.show_game_and_start)
        splash_exit_btn.clicked.connect(self.close)

    def setup_game_ui(self):
        """Budowa głównego interfejsu użytkownika gry""" # <<< ZMIENIONO NAZWĘ z setup_ui
        self.main_game_widget = QWidget() # <<< ZMIENIONO central_widget na self.main_game_widget
        self.main_game_widget.setObjectName("mainWidget")
        self.set_style_sheet(self.main_game_widget)
        # self.setCentralWidget(self.main_game_widget) # <<< USUNIĘTO - ustawimy widget później

        # Główne layouty
        main_layout = QVBoxLayout(self.main_game_widget)
        top_row = QHBoxLayout()  # Górny wiersz (talia, stos odrzuconych, fundamenty)
        tableau_row = QHBoxLayout()  # Wiersz kolumn roboczych
        stats_row = QHBoxLayout()  # Wiersz statystyk
        button_row = QHBoxLayout()  # Wiersz przycisków

        # Inicjalizacja i konfiguracja widgetów
        self.init_stock_and_waste(top_row)
        self.init_foundations(top_row)
        self.init_tableau(tableau_row)
        self.init_stats(stats_row)
        self.init_buttons(button_row)

        # Składanie layoutów
        main_layout.addLayout(top_row)
        main_layout.addSpacing(20)
        main_layout.addLayout(tableau_row)
        main_layout.addStretch()
        main_layout.addLayout(stats_row)
        main_layout.addLayout(button_row)

    def set_style_sheet(self, widget):
        """Ustawienie stylów CSS dla aplikacji"""
        # Dodajemy import czcionki na górze pliku
        from PyQt5.QtCore import Qt
        widget.setStyleSheet("""
            QWidget#mainWidget { 
                border-image: url(resources/background.png) 0 0 0 0 stretch stretch;
            }
            QPushButton { 
                background-color: white; 
                border: 1px solid #888; 
                padding: 10px 15px; /* Lekko powiększone dla lepszego wyglądu */
                border-radius: 5px; 
                min-width: 120px; /* Lekko poszerzone */
                font-size: 14px; /* Dodano dla spójności */
                font-weight: bold;
            }
            QPushButton:hover { background-color: #f0f0f0; }
            QPushButton:disabled { background-color: #d0d0d0; color: #888888; }
            QLabel#StatsLabel {
                color: white;
                font-size: 14px;
                font-weight: bold;
                background: rgba(0, 0, 0, 0.5);
                padding: 5px;
                border-radius: 4px;
            }           
        """)

    def init_stock_and_waste(self, layout):
        """Inicjalizacja widgetów talii i stosu odrzuconych"""
        self.stock_placeholder = DropPlaceholder()
        self.waste_placeholder = DropPlaceholder()
        layout.addWidget(self.stock_placeholder)
        layout.addWidget(self.waste_placeholder)
        layout.addStretch()

    def init_foundations(self, layout):
        """Inicjalizacja widgetów stosów docelowych"""
        self.foundations_placeholders = []
        for i in range(4):
            f = DropPlaceholder(label="") 
            f.setObjectName(f"foundation_{i}")
            layout.addWidget(f)
            self.foundations_placeholders.append(f)

    def init_tableau(self, layout):
        """Inicjalizacja widgetów kolumn roboczych"""
        self.tableau_columns = []
        for i in range(7):
            col = CardColumnWidget()
            col.setObjectName(f"tableau_{i}")
            layout.addWidget(col)
            self.tableau_columns.append(col)

    def init_stats(self, layout):
        """Inicjalizacja widgetów statystyk"""
        self.time_label = QLabel("Czas: 00:00")
        self.time_label.setObjectName("StatsLabel")
        self.score_label = QLabel("Punkty: 0")
        self.score_label.setObjectName("StatsLabel")
        self.moves_label = QLabel("Ruchy: 0")
        self.moves_label.setObjectName("StatsLabel")
        self.undo_label = QLabel("Cofnięć: 3/3")
        self.undo_label.setObjectName("StatsLabel")

        layout.addStretch()
        layout.addWidget(self.time_label)
        layout.addSpacing(20)
        layout.addWidget(self.score_label)
        layout.addSpacing(20)
        layout.addWidget(self.moves_label)
        layout.addSpacing(20)
        layout.addWidget(self.undo_label)
        layout.addStretch()

    def init_buttons(self, layout):
        """Inicjalizacja przycisków sterujących"""
        self.new_game_btn = QPushButton("🎲 Nowa gra")
        self.undo_btn = QPushButton("⏪ Cofnij")
        self.exit_btn = QPushButton("❌ Wyjście")
        layout.addWidget(self.new_game_btn)
        layout.addWidget(self.undo_btn)
        layout.addStretch()
        layout.addWidget(self.exit_btn)

    def init_menu(self):
        """Inicjalizacja menu głównego"""
        menu = self.menuBar()
        menu.setStyleSheet("color: black; background-color: white;")
        help_menu = menu.addMenu("⚙️ Ustawienia")
        help_action = QAction("❓ Pomoc", self)
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)

    def connect_signals(self):
        """Podłączenie sygnałów do slotów"""
        # Sygnały dla przycisków w grze
        self.new_game_btn.clicked.connect(self.start_new_game)
        self.undo_btn.clicked.connect(self.undo_move)
        self.exit_btn.clicked.connect(self.close)
        self.timer.timeout.connect(self.timer_tick)
        self.stock_placeholder.clicked.connect(self.handle_stock_click)
        
        for col in self.tableau_columns:
            col.card_dropped.connect(self.handle_drop_on_tableau)
            
        for f in self.foundations_placeholders:
            f.card_dropped.connect(self.handle_drop_on_foundation)

    def clear_all_cards(self):
        """Usuwa wszystkie karty z interfejsu"""
        for placeholder in [self.stock_placeholder, self.waste_placeholder] + self.foundations_placeholders:
            for child in placeholder.findChildren(CardWidget):
                child.deleteLater()
                
        for column in self.tableau_columns:
            column.cards.clear()
            for child in column.findChildren(CardWidget):
                child.deleteLater()

    def update_board_from_logic(self):
        """Aktualizuje interfejs na podstawie stanu logiki gry"""
        self.clear_all_cards()
        QApplication.processEvents()
        
        # Aktualizacja talii i stosu odrzuconych
        if self.game.stock:
            CardWidget(('tył_karty', ''), parent=self.stock_placeholder, draggable=False).show()
            
        if self.game.waste:
            top_card = self.game.waste[-1]
            card_data = (top_card['suit'], top_card['rank'])
            widget = CardWidget(card_data, parent=self.waste_placeholder, source=('waste', 0))
            widget.card_double_clicked.connect(self.handle_card_double_click)
            widget.show()

        # Aktualizacja stosów docelowych
        for i, pile in enumerate(self.game.foundations):
            placeholder = self.foundations_placeholders[i]
            if not pile:
                symbol = self.foundation_symbols[i]
                placeholder.label.setText(symbol)
                placeholder.label.setStyleSheet("""
                    background-color: rgba(255, 255, 255, 0.4); 
                    border: 2px dashed rgba(0, 0, 0, 0.4); 
                    border-radius: 8px;
                    color: rgba(0,0,0,0.5); 
                    font-size: 70px; 
                    font-family: 'Times New Roman';
                """)
                placeholder.label.show()
            else:
                placeholder.label.hide()
                top_card = pile[-1]
                card_data = (top_card['suit'], top_card['rank'])
                CardWidget(card_data, parent=placeholder, source=('foundation', i)).show()

        # Aktualizacja kolumn roboczych
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
                
        self.update_stats_display()
        QApplication.processEvents()

    def update_stats_display(self):
        """Aktualizuje wyświetlane statystyki gry"""
        time_str = QTime(0, 0).addSecs(self.seconds_played).toString("mm:ss")
        self.time_label.setText(f"Czas: {time_str}")
        self.score_label.setText(f"Punkty: {self.game.score}")
        self.moves_label.setText(f"Ruchy: {self.game.moves}")
        self.undo_label.setText(f"Cofnięć: {self.game.undo_count}/3")
        self.undo_btn.setEnabled(self.game.undo_count > 0 and bool(self.game.history))

    # Metody obsługi zdarzeń
    def timer_tick(self):
        """Aktualizacja czasu gry"""
        self.seconds_played += 1
        self.update_stats_display()

    def handle_stock_click(self):
        """Obsługa kliknięcia na stosie kart"""
        if self.game.draw_from_stock():
            self.update_board_from_logic()

    def handle_card_double_click(self, source_info):
        """Obsługa podwójnego kliknięcia na karcie"""
        moved = False
        card_to_move = None
        source_type, source_idx, *rest = source_info
        
        if source_type == 'tableau':
            card_idx = rest[0]
            if card_idx == len(self.game.tableau[source_idx]) - 1:
                card_to_move = self.game.tableau[source_idx][card_idx]
        elif source_type == 'waste' and self.game.waste:
            card_to_move = self.game.waste[-1]
            
        if card_to_move:
            self.game.save_state()
            for i in range(4):
                if self.game.is_valid_for_foundation(card_to_move, i):
                    self.game.perform_move([card_to_move], (source_type, source_idx), ('foundation', i))
                    moved = True
                    break
                    
            if not moved:
                self.game.history.pop()
                
        if moved:
            self.update_board_from_logic()
            if self.game.check_win_condition(): 
                self.show_win_message()

    def handle_drop(self, source_info, destination_info):
        """Obsługa upuszczenia karty"""
        card_stack_to_move = []
        source_type, source_idx, *rest = source_info
        
        if source_type == 'tableau':
            card_idx_in_stack = rest[0]
            card_stack_to_move = self.game.tableau[source_idx][card_idx_in_stack:]
        elif source_type == 'waste' and self.game.waste:
            card_stack_to_move = [self.game.waste[-1]]
        elif source_type == 'foundation' and self.game.foundations[source_idx]:
            card_stack_to_move = [self.game.foundations[source_idx][-1]]
            
        if not card_stack_to_move: 
            return
            
        if self.game.attempt_move(card_stack_to_move, (source_type, source_idx), destination_info):
            self.update_board_from_logic()
            if self.game.check_win_condition(): 
                self.show_win_message()

    def handle_drop_on_tableau(self, source, dest_widget):
        """Obsługa upuszczenia na kolumnę roboczą"""
        dest_index = self.tableau_columns.index(dest_widget)
        self.handle_drop(source, ('tableau', dest_index))

    def handle_drop_on_foundation(self, source, dest_widget):
        """Obsługa upuszczenia na stos docelowy"""
        dest_index = self.foundations_placeholders.index(dest_widget)
        self.handle_drop(source, ('foundation', dest_index))

    def show_game_and_start(self):
        """Zamienia widget na widok gry i rozpoczyna nową grę."""
        self.setCentralWidget(self.main_game_widget)
        self.start_new_game()
        
    def start_new_game(self):
        """Rozpoczęcie nowej gry"""
        self.game.new_game()
        self.seconds_played = 0
        self.timer.start(1000)
        self.update_board_from_logic()

    def undo_move(self):
        """Cofnięcie ostatniego ruchu"""
        if self.game.undo():
            self.update_board_from_logic()

    def show_help(self):
        """Wyświetlenie okna pomocy"""
        help_text = """
    <p style='margin-top:10px; margin-bottom:10px;'><b>🎯 Cel gry:</b><br>
    Ułóż wszystkie karty na czterech stosach fundamentowych (pola w prawym górnym rogu), posortowane według kolorów od Asa do Króla.</p>

    <p style='margin-top:10px; margin-bottom:10px;'><b>📝 Zasady:</b><br>
    - W kolumnach roboczych układaj karty malejąco, naprzemiennie kolorami.<br>
    - Możesz przenosić pojedyncze karty lub całe, poprawnie ułożone stosy kart.<br>
    - Kliknięcie na stos po lewej dobiera kartę.<br>
    - Podwójne kliknięcie na karcie przeniesie ją na fundament, jeśli to możliwe.</p>

    <p style='margin-top:10px; margin-bottom:10px;'><b>💰 Punktacja:</b><br>
    - Przeniesienie karty na fundament: <b>+10 pkt</b><br>
    - Przeniesienie karty ze stosu odrzuconych do kolumny: <b>+5 pkt</b><br>
    - Odkrycie nowej karty w kolumnie roboczej: <b>+5 pkt</b><br>
    - Przeniesienie karty z fundamentu do kolumny: <b>-15 pkt</b></p>
    """
        QMessageBox.information(self, "Pomoc", help_text)

    def show_win_message(self):
        """Wyświetlenie komunikatu o wygranej"""
        self.timer.stop()
        final_score = self.game.score
        final_time = QTime(0, 0).addSecs(self.seconds_played).toString("mm:ss")
        final_moves = self.game.moves
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Gratulacje!")
        msg_box.setText("🎉 Wygrałeś! 🎉")
        msg_box.setInformativeText(f"Twój wynik: {final_score} pkt\nCzas: {final_time}\nRuchy: {final_moves}\n\nCzy chcesz rozpocząć nową grę?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.Yes)
        
        if msg_box.exec_() == QMessageBox.Yes:
            self.start_new_game()
