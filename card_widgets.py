import os
import ast
from PyQt5.QtWidgets import QLabel, QWidget
from PyQt5.QtCore import Qt, QMimeData, pyqtSignal
from PyQt5.QtGui import QPixmap, QDrag


class CardWidget(QLabel):
    """Widget reprezentujący pojedyńczą kartę do gry, obsługa przeciągania i kliknięcia podwójnego."""

    # Sygnał emitowany przy podwójnym kliknięciu karty
    card_double_clicked = pyqtSignal(tuple)

    def __init__(self, card_data, parent=None, source=None, draggable=True):
        """
        Inicjalizacja widgetu karty
        :param card_data: Krotka (typ_karty, wartość) np. ('serce', 'A')
        :param parent: Widget rodzic
        :param source_location: Lokalizacja źródłowa karty (do identyfikacji)
        :param draggable: Czy karta może być przeciągana
        """
        super().__init__(parent)
        self.card_data = card_data
        self.source = source
        self.is_draggable = draggable

        # Podstawowa konfiguracja wyglądu
        self.setFixedSize(100, 145)
        self.setScaledContents(True)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setStyleSheet("border-radius: 5px; border: 1px solid black;")
        self.load_texture()

    def mousePressEvent(self, event):
        """Obsługa kliknięcia myszą - rozpoczyna przeciąganie"""
        if event.button() == Qt.LeftButton and self.is_draggable:
            self.drag_start_position = event.pos()
        else:
            super().mousePressEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        """Obsługa podwójnego kliknięcia - emituje sygnał"""
        if event.button() == Qt.LeftButton and self.is_draggable:
            self.card_double_clicked.emit(self.source)
        super().mouseDoubleClickEvent(event)

    def mouseMoveEvent(self, event):
        """Obsługa przeciągania karty"""
        if not (event.buttons() & Qt.LeftButton and self.is_draggable):
            return
        
        # Minimalny ruch potrzebny do rozpoczęcia przeciągania
        if (event.pos() - self.drag_start_position).manhattanLength() < 10:
            return
        
        # Przygotowanie operacji przeciągania
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(repr(self.source))
        drag.setMimeData(mime_data)

        # Ustawienie podglądu przeciąganej karty
        pix = self.pixmap()
        if pix and not pix.isNull():
            drag.setPixmap(pix.scaled(100, 145, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            drag.setHotSpot(event.pos())
            drag.exec_(Qt.MoveAction)

    def load_texture(self):
        """Ładuje odpowiednią teksturę karty na podstawie danych"""
        card_type, card_value = self.card_data

        # Ścieżka do pliku z teksturą
        if card_type == 'tył_karty':
            texture_path = "resources/cards/tył_karty.png"
        else:
            texture_path = f"resources/cards/{card_type}_{card_value}.png"

        # Próba załadowania tekstury
        if os.path.exists(texture_path):
            pixmap = QPixmap(texture_path)
            if not pixmap.isNull():
                self.setPixmap(pixmap.scaled(100, 145, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                return
            
        # Fallback - wyświetlanie tekstu gdy brak tekstury
        self.set_fallback_style(card_type, card_value)

    def set_fallback_style(self, card_type, card_value):
        """Styl awaryjny gdy nie można załadować tekstury karty"""
        colors = {'diament': 'red', 'serce': 'red', 'wino': 'black', 'żołędź': 'black'}
        self.setStyleSheet(f"""
            background-color: white; color: {colors.get(card_type, 'gray')};
            border: 1px solid black; border-radius: 5px;
            font-weight: bold; font-size: 16px;
        """)
        self.setText(f"{card_value}\n{card_type}")
        self.setAlignment(Qt.AlignCenter)


class DropPlaceholder(QWidget):
    """Obszar, na który można upuszczać karty"""
    clicked = pyqtSignal()
    card_dropped = pyqtSignal(tuple, QWidget)

    def __init__(self, label="", parent=None):
        """Konfiguracja podstawowych właściwości obszaru drop"""
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setFixedSize(100, 145)
        self.setStyleSheet("background-color: rgba(255, 255, 255, 0.1); border: 2px dashed rgba(255, 255, 255, 0.4); border-radius: 5px;")
        
        # Etykieta obszaru
        self.label = QLabel(label, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("background: transparent; border: none; color: rgba(255,255,255,0.4); font-size: 12px;")
        self.label.setGeometry(0, 0, 100, 145)
        
    def mousePressEvent(self, event):
        """Obsługa kliknięcia na obszarze"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit()

    def dragEnterEvent(self, event):
        """Akceptuj przeciąganie jeśli obiekt zawiera dane tekstowe"""
        if event.mimeData().hasText(): event.acceptProposedAction()

    def dropEvent(self, event):
        """Obsługa upuszczenia karty"""
        source_info = ast.literal_eval(event.mimeData().text())
        self.card_dropped.emit(source_info, self)
        event.acceptProposedAction()


class CardColumnWidget(QWidget):
    """Specjalny obszar drop reprezentujący kolumnę"""
    card_dropped = pyqtSignal(tuple, QWidget)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setMinimumSize(120, 600)
        self.cards = []
        self.setStyleSheet("background-color: transparent;")
        
        # Konfiguracja podstawowych właściwości
        self.placeholder = QLabel(self)
        self.placeholder.setGeometry(10, 10, 100, 145)
        self.placeholder.setStyleSheet("""
            background-color: rgba(0, 0, 0, 0.15); 
            border: 2px dashed rgba(255, 255, 255, 0.2); 
            border-radius: 5px;
        """)
        self.placeholder.hide() 

    def dragEnterEvent(self, event):
        """Obsługa zdarzenia najechania przeciąganym obiektem"""
        if event.mimeData().hasText(): event.acceptProposedAction()

    def dropEvent(self, event):
        """Obsługa zdarzenia upuszczenia karty"""
        source_info = ast.literal_eval(event.mimeData().text())
        self.card_dropped.emit(source_info, self)
        event.acceptProposedAction()