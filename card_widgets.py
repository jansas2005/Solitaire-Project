import sys
import random
from PyQt5.QtWidgets import (
    QApplication, QLabel, QWidget, QVBoxLayout,
    QMainWindow, QHBoxLayout, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, QMimeData, pyqtSignal
from PyQt5.QtGui import QPixmap, QDrag


class CardWidget(QLabel):
    def __init__(self, card_data, pixmap, parent=None):
        super().__init__(parent)
        self.card_data = card_data
        self.setPixmap(pixmap)
        self.setScaledContents(True)
        self.setFixedSize(100, 145)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setStyleSheet("border: 1px solid black;")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton) and \
            (event.pos() - self.drag_start_position).manhattanLength() > 10:

            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText(str(self.card_data))
            drag.setMimeData(mime_data)

            drag.setPixmap(self.pixmap())
            drag.setHotSpot(event.pos())

            result = drag.exec_(Qt.MoveAction)

            if result == Qt.MoveAction:
                self.close()




class DropPlaceholder(QWidget):
    clicked = pyqtSignal()

    def __init__(self, label="", parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setFixedSize(100, 145)
        self.setStyleSheet("""
            background-color: rgba(200, 200, 200, 0.3);
            border: 2px dashed gray;
        """)

        self.label = QLabel(label, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color: gray; font-size: 12px;")
        self.label.setGeometry(0, 0, 100, 145)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        card_info = event.mimeData().text()
        print(f"Upuszczono kartę do: {self.objectName()} ->", card_info)

        new_card = CardWidget(eval(card_info), QPixmap("cards/AS.png"), parent=self)
        new_card.move(0, 0)
        new_card.show()
        event.acceptProposedAction()


class CardColumnWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setFixedSize(120, 600)
        self.cards = []

        self.setStyleSheet("background-color: rgba(0,100,0,0.4);")

        self.placeholder = QLabel(self)
        self.placeholder.setFixedSize(100, 145)
        self.placeholder.move(10, 10)
        self.placeholder.setStyleSheet("""
            background-color: rgba(200, 200, 200, 0.2);
            border: 2px dashed gray;
        """)
        self.placeholder.show()

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        card_info = event.mimeData().text()
        print("Upuszczono kartę do kolumny:", card_info)

        new_card = CardWidget(eval(card_info), QPixmap("cards/AS.png"))
        new_card.setParent(self)

        if not self.cards:
            new_card.move(10, 10)
        else:
            offset = 10 + len(self.cards) * 30
            new_card.move(10, offset)

        new_card.show()
        self.cards.append(new_card)
        event.acceptProposedAction()



def main():
    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle("Pasjans - Widok startowy")
    window.setGeometry(100, 100, 1200, 800)

    central = QWidget()
    central.setStyleSheet("background-color: green;")
    window.setCentralWidget(central)

    main_layout = QVBoxLayout(central)

    # Górny rząd
    top_row = QHBoxLayout()
    top_row.setSpacing(30)
    top_row.setContentsMargins(20, 20, 20, 20)

    # Tworzenie pełnej talii 52 kart
    suits = ['spades', 'hearts', 'diamonds', 'clubs']
    ranks = ['A'] + [str(n) for n in range(2, 11)] + ['J', 'Q', 'K']

    deck = [(suit, rank) for suit in suits for rank in ranks]
    random.shuffle(deck)

    card_stack = deck


    stock = DropPlaceholder("STOCK")
    stock.setObjectName("stock")

    waste = DropPlaceholder("WASTE")
    waste.setObjectName("waste")

    top_row.addWidget(stock)
    top_row.addWidget(waste)
    top_row.addSpacerItem(QSpacerItem(100, 20, QSizePolicy.Expanding))

    for i in range(4):
        f = DropPlaceholder(f"F{i+1}")
        f.setObjectName(f"foundation_{i+1}")
        top_row.addWidget(f)

    main_layout.addLayout(top_row)

    # Dolny rząd: 7 kolumn
    columns_row = QHBoxLayout()
    columns_row.setSpacing(20)
    columns_row.setContentsMargins(20, 10, 20, 20)

    for i in range(7):
        col = CardColumnWidget()
        columns_row.addWidget(col)

    main_layout.addLayout(columns_row)

    #  Obsługa kliknięcia w STOCK – pokazuje kolejną kartę w WASTE
    def show_next_card():
        if card_stack:
            card_data = card_stack.pop(0)

            # Usuń poprzednią kartę w WASTE
            for child in waste.children():
                if isinstance(child, CardWidget):
                    child.close()

            new_card = CardWidget(card_data, QPixmap("cards/AS.png"), parent=waste)
            new_card.move(0, 0)
            new_card.show()

    stock.clicked.connect(show_next_card)

    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
