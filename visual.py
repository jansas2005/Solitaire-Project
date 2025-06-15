import os
from PyQt5.QtWidgets import QMainWindow, QLabel, QMessageBox, QPushButton
from PyQt5.QtGui import QPixmap, QDrag
from PyQt5.QtCore import Qt, QMimeData, QPoint
import game_logic

CARD_WIDTH = 100
CARD_HEIGHT = 145
HORIZONTAL_SPACING = 120
VERTICAL_SPACING = 35
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700
TOP_MARGIN = 20
LEFT_MARGIN = 20

class CardLabel(QLabel):
    """Etykieta karty i jej przeciąganie"""
    def __init__(self, parent, card_object, pile_info):
        super().__init__(parent)
        self.main_window = parent
        self.card = card_object
        self.pile_info = pile_info
        self.setScaledContents(True)
        self.setFixedSize(CARD_WIDTH, CARD_HEIGHT)
        self.set_pixmap()

    def set_pixmap(self):
        """Ustawia obrazek karty"""
        image_path = self.main_window.get_card_image_path(self.card)
        pixmap = QPixmap(image_path)
        self.setPixmap(pixmap)

    def mousePressEvent(self, event):
        """Rozpoczyna przeciąganie karty jeśli możliwe"""
        if not self.card or not self.card.widoczna:
            return

        if event.button() == Qt.LeftButton:
            self.main_window.start_drag(self)

class SolitaireWindow(QMainWindow):
    """Główne okno pasjansa"""
    def __init__(self):
        super().__init__()
        self.dragged_cards_info = None
        self.init_ui()
        self.new_game()

    def init_ui(self):
        """Inicjalizuje interfejs użytkownika."""
        self.setWindowTitle('Pasjans Klondike')
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setStyleSheet("background-color: #006400;")
        self.setAcceptDrops(True)
        self.card_labels = []

        self.stock_label = QLabel(self)
        self.stock_label.setGeometry(LEFT_MARGIN, TOP_MARGIN, CARD_WIDTH, CARD_HEIGHT)
        self.stock_label.mousePressEvent = self.stock_clicked

        button_width = 110
        button_height = 40
        right_margin = 20
        bottom_margin = 20
        self.new_game_button = QPushButton('Nowa Gra', self)
        self.new_game_button.setGeometry(
            WINDOW_WIDTH - button_width - right_margin,
            WINDOW_HEIGHT - button_height - bottom_margin,
            button_width,
            button_height
        )
        self.new_game_button.setStyleSheet("font-size: 16px; background-color: #c0c0c0; border-radius: 5px;")
        self.new_game_button.clicked.connect(self.new_game)

    def new_game(self):
        """Rozpoczyna nową grę"""
        self.game = game_logic.Gra()
        self.update_ui()

    def update_ui(self):
        """Odświeża interfejs graficzny"""
        for label in self.card_labels:
            label.deleteLater()
        self.card_labels.clear()

        if self.game.stos:
            self.stock_label.setPixmap(QPixmap('assets/cards/back.png').scaled(CARD_WIDTH, CARD_HEIGHT, Qt.KeepAspectRatio))
        #else:

        # Rysowanie kart odrzuconych
        if self.game.odrzucone:
            card = self.game.odrzucone[-1]
            label = CardLabel(self, card, ('odrzucone',))
            label.move(LEFT_MARGIN + HORIZONTAL_SPACING, TOP_MARGIN)
            self.card_labels.append(label)

        # Rysowanie fundamentów
        for i, color in enumerate(self.game.fundamenty):
            if self.game.fundamenty[color]:
                card = self.game.fundamenty[color][-1]
                label = CardLabel(self, card, ('fundament', i))
                x = LEFT_MARGIN + (3 + i) * HORIZONTAL_SPACING
                label.move(x, TOP_MARGIN)
                self.card_labels.append(label)

        # Rysowanie kolumn
        for i, column in enumerate(self.game.kolumny):
            for j, card in enumerate(column):
                label = CardLabel(self, card, ('kolumna', i))
                x = LEFT_MARGIN + i * HORIZONTAL_SPACING
                y = TOP_MARGIN + CARD_HEIGHT + 40 + j * VERTICAL_SPACING
                label.move(x, y)
                self.card_labels.append(label)

        for label in self.card_labels:
            label.show()
            label.raise_()

        if self.game.czy_gra_wygrana():
            self.show_win_message()

    def get_card_image_path(self, card):
        """Zwraca ścieżkę do pliku z obrazkiem karty."""
        if not card.widoczna:
            return 'assets/cards/back.png'
        
        kolor = card.kolor
        ranga = card.ranga
        path = f'assets/cards/{kolor}_{ranga}.png'

        return path
    
    def stock_clicked(self, event):
        """Obsługuje kliknięcie na stos."""
        self.game.dobierz_ze_stosu()
        self.update_ui()

    def start_drag(self, card_label):
        """Inicjuje operację przeciągania."""
        if not card_label.pile_info: return
        source_type = card_label.pile_info[0]
        cards_to_drag = []

        if source_type == 'odrzucone':
            cards_to_drag.append(card_label)
        elif source_type == 'kolumna':
            source_index = card_label.pile_info[1]
            column = self.game.kolumny[source_index]
            card_idx = column.index(card_label.card)
            for lbl in self.card_labels:
                if lbl.pile_info == ('kolumna', source_index) and lbl.card in column[card_idx:]:
                    cards_to_drag.append(lbl)

        if not cards_to_drag: return
            
        self.dragged_cards_info = { "labels": cards_to_drag, "source_pile": card_label.pile_info, "card_count": len(cards_to_drag) }
        
        drag = QDrag(self)
        drag.setPixmap(cards_to_drag[0].grab())
        drag.setHotSpot(QPoint(CARD_WIDTH // 2, CARD_HEIGHT // 2))
        drag.setMimeData(QMimeData())
        
        for lbl in cards_to_drag: lbl.hide()
        
        if drag.exec_(Qt.MoveAction) == Qt.IgnoreAction:
            for lbl in cards_to_drag: lbl.show()
        
        self.dragged_cards_info = None

    def dragEnterEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        """Obsługuje upuszczenie karty."""
        if not self.dragged_cards_info:
            event.ignore()
            return
            
        pos = event.pos()
        success = False

        source_pile = self.dragged_cards_info["source_pile"]
        source_type = source_pile[0]
        card_count = self.dragged_cards_info["card_count"]

        # do fundamentu
        for i in range(4):
            x = LEFT_MARGIN + (3 + i) * HORIZONTAL_SPACING
            y = TOP_MARGIN
            if x <= pos.x() < x + CARD_WIDTH and y <= pos.y() < y + CARD_HEIGHT:
                if card_count == 1:
                    if source_type == 'kolumna':
                        source_idx = source_pile[1]
                        success = self.game.przenies_z_kolumny_do_fundamentu(source_idx)
                    elif source_type == 'odrzucone':
                        success = self.game.przenies_ze_stosu_do_fundamentu()
                break
        
        # do kolumny
        if not success:
            for i in range(7):
                x = LEFT_MARGIN + i * HORIZONTAL_SPACING
                y_top = TOP_MARGIN + CARD_HEIGHT + 40
                
                column_height = y_top + CARD_HEIGHT
                if self.game.kolumny[i]:
                    column_height = y_top + (len(self.game.kolumny[i]) - 1) * VERTICAL_SPACING + CARD_HEIGHT

                if x <= pos.x() < x + CARD_WIDTH and y_top <= pos.y() < column_height + VERTICAL_SPACING:
                    if source_type == 'kolumna':
                        source_idx = source_pile[1]
                        if source_idx != i:
                            success = self.game.przenies_miedzy_kolumnami(source_idx, i, card_count)
                    elif source_type == 'odrzucone':
                        success = self.game.przenies_ze_stosu_do_kolumny(i)
                    break

        self.update_ui()
        event.accept()

    def show_win_message(self):
        """Wyświetla komunikat o wygranej."""
        msg = QMessageBox(self)
        msg.setWindowTitle("Gratulacje!")
        msg.setText("Wygrałeś! 🎉")
        msg.setInformativeText("Czy chcesz zagrać jeszcze raz?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.Yes)
        
        if msg.exec_() == QMessageBox.Yes:
            self.new_game()
        else:
            self.close()