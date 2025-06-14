import os
from PyQt5.QtWidgets import QLabel, QWidget
from PyQt5.QtCore import Qt, QMimeData, pyqtSignal
from PyQt5.QtGui import QPixmap, QDrag


class CardWidget(QLabel):
    def __init__(self, card_data, pixmap=None, parent=None):
        super().__init__(parent)
        self.card_data = card_data
        self.setFixedSize(100, 145)
        self.setScaledContents(True)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setStyleSheet("border-radius: 5px; border: 1px solid black;")

        if pixmap:
            self.setPixmap(pixmap.scaled(100, 145, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        self.load_texture()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton) and \
           (event.pos() - self.drag_start_position).manhattanLength() > 10:

            pix = self.pixmap()
            if pix and not pix.isNull():
                drag = QDrag(self)
                mime_data = QMimeData()
                mime_data.setText(str(self.card_data))
                drag.setMimeData(mime_data)

                drag.setPixmap(pix.scaled(100, 145, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                drag.setHotSpot(event.pos())

                result = drag.exec_(Qt.MoveAction)
                if result == Qt.MoveAction:
                    self.close()
            else:
                print("⚠️ Brak pixmapy, nie można przeciągnąć.")

    def load_texture(self):
        card_type, card_value = self.card_data

        # mapowanie wartości
        value_map = {
            'A': 'A', '2': '2', '3': '3', '4': '4',
            '5': '5', '6': '6', '7': '7', '8': '8',
            '9': '9', '10': '10', 'J': 'J', 'Q': 'Q', 'K': 'K'
        }

        if card_type not in ['diament', 'serce', 'wino', 'żołędź', 'tył_karty']:
            raise ValueError(f"Nieznany typ karty: {card_type}")

        if card_value not in value_map and card_type != 'tył_karty':
            raise ValueError(f"Nieznana wartość karty: {card_value}")

        # wybór pliku
        if card_type == 'tył_karty':
            texture_path = "resources/cards/tył_karty.png"
        else:
            texture_path = f"resources/cards/{card_type}_{value_map[card_value]}.png"

        if os.path.exists(texture_path):
            pixmap = QPixmap(texture_path)
            if not pixmap.isNull():
                self.setPixmap(pixmap.scaled(100, 145, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                return
            else:
                print(f"⚠️ Nie udało się załadować pliku: {texture_path}")
        else:
            print(f"❌ Brak pliku: {texture_path}")

        self.set_fallback_style(card_type, card_value)

    def set_fallback_style(self, card_type, card_value):
        colors = {
            'diament': 'red',
            'serce': 'red',
            'wino': 'black',
            'żołędź': 'black'
        }

        self.setStyleSheet(f"""
            background-color: white;
            color: {colors.get(card_type, 'gray')};
            border: 1px solid black;
            border-radius: 5px;
            font-weight: bold;
            font-size: 16px;
        """)
        self.setText(f"{card_value}\n{card_type}")
        self.setAlignment(Qt.AlignCenter)


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

        new_card = CardWidget(eval(card_info), parent=self)
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

        new_card = CardWidget(eval(card_info), parent=self)

        if not self.cards:
            new_card.move(10, 10)
        else:
            offset = 10 + len(self.cards) * 30
            new_card.move(10, offset)

        new_card.show()
        self.cards.append(new_card)
        event.acceptProposedAction()
