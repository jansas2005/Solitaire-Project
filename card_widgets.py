import os
import ast
from PyQt5.QtWidgets import QLabel, QWidget
from PyQt5.QtCore import Qt, QMimeData, pyqtSignal
from PyQt5.QtGui import QPixmap, QDrag

# Klasa reprezentująca widżet pojedynczej karty z funkcją przeciągania i podwójnego kliknięcia
class CardWidget(QLabel):
    card_double_clicked = pyqtSignal(tuple)

    def __init__(self, card_data, parent=None, source=None, draggable=True):
        super().__init__(parent)
        self.card_data = card_data
        self.source = source
        self.is_draggable = draggable
        self.setup_card_appearance()

    # Konfiguracja podstawowego wyglądu i zachowania karty
    def setup_card_appearance(self):
        self.setFixedSize(100, 145)
        self.setScaledContents(True)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setStyleSheet("border-radius: 5px; border: 1px solid black;")
        self.load_texture()

    # Obsługa zdarzeń myszy dla przeciągania karty
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.is_draggable:
            self.drag_start_position = event.pos()
        else:
            super().mousePressEvent(event)
    
    # Obsługa podwójnego kliknięcia na kartę
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton and self.is_draggable:
            self.card_double_clicked.emit(self.source)
        super().mouseDoubleClickEvent(event)

    # Logika przeciągania karty
    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton and self.is_draggable):
            return
        if (event.pos() - self.drag_start_position).manhattanLength() < 10:
            return
        
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(repr(self.source))
        drag.setMimeData(mime_data)
        
        pix = self.pixmap()
        if pix and not pix.isNull():
            drag.setPixmap(pix.scaled(100, 145, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            drag.setHotSpot(event.pos())
            drag.exec_(Qt.MoveAction)

    # Ładowanie obrazka karty z pliku
    def load_texture(self):
        card_type, card_value = self.card_data
        if card_type == 'tył_karty':
            texture_path = "resources/cards/tył_karty.png"
        else:
            texture_path = f"resources/cards/{card_type}_{card_value}.png"
        
        if os.path.exists(texture_path):
            pixmap = QPixmap(texture_path)
            if not pixmap.isNull():
                self.setPixmap(pixmap.scaled(100, 145, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                return
        
        self.set_fallback_style(card_type, card_value)

    # Awaryjny styl gdy nie znaleziono obrazka karty
    def set_fallback_style(self, card_type, card_value):
        colors = {'diament': 'red', 'serce': 'red', 'wino': 'black', 'żołędź': 'black'}
        self.setStyleSheet(f"""
            background-color: white; color: {colors.get(card_type, 'gray')};
            border: 1px solid black; border-radius: 5px;
            font-weight: bold; font-size: 16px;
        """)
        self.setText(f"{card_value}\n{card_type}")
        self.setAlignment(Qt.AlignCenter)


# Klasa reprezentująca obszar do upuszczania kart (stosy docelowe)
class DropPlaceholder(QWidget):
    clicked = pyqtSignal()
    card_dropped = pyqtSignal(tuple, QWidget)

    def __init__(self, label="", parent=None):
        super().__init__(parent)
        self.setup_drop_area(label)

    # Konfiguracja wyglądu obszaru drop
    def setup_drop_area(self, label):
        self.setAcceptDrops(True)
        self.setFixedSize(100, 145)
        self.setObjectName("DropPlaceholder")
        self.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.4); 
            border: 2px dashed rgba(0, 0, 0, 0.4); 
            border-radius: 8px;
        """)
        
        self.label = QLabel(label, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.4); 
            border: 2px dashed rgba(0, 0, 0, 0.4); 
            border-radius: 8px;
        """)
        self.label.setGeometry(0, 0, 100, 145)
        
    # Obsługa zdarzenia kliknięcia
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()

    # Obsługa zdarzenia przeciągania nad obszarem
    def dragEnterEvent(self, event):
        if event.mimeData().hasText(): 
            event.acceptProposedAction()

    # Obsługa upuszczenia karty
    def dropEvent(self, event):
        source_info = ast.literal_eval(event.mimeData().text())
        self.card_dropped.emit(source_info, self)
        event.acceptProposedAction()


# Klasa reprezentująca kolumnę roboczą (specjalny obszar drop)
class CardColumnWidget(QWidget):
    card_dropped = pyqtSignal(tuple, QWidget)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_column()
        self.cards = []

    # Konfiguracja wyglądu kolumny
    def setup_column(self):
        self.setAcceptDrops(True)
        self.setMinimumSize(120, 600)
        self.setStyleSheet("background-color: transparent;")
        
        self.placeholder = QLabel(self)
        self.placeholder.setGeometry(10, 10, 100, 145)
        self.placeholder.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.4); 
            border: 2px dashed rgba(0, 0, 0, 0.4); 
            border-radius: 8px;
        """)
        self.placeholder.hide()

    # Obsługa przeciągania nad kolumną
    def dragEnterEvent(self, event):
        if event.mimeData().hasText(): 
            event.acceptProposedAction()

    # Obsługa upuszczenia karty w kolumnie
    def dropEvent(self, event):
        source_info = ast.literal_eval(event.mimeData().text())
        self.card_dropped.emit(source_info, self)
        event.acceptProposedAction()