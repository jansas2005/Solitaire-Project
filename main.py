import sys
import os
from PyQt5.QtWidgets import QApplication
from visual import SolitaireWindow

def main():
    if not os.path.exists('assets/cards'):
        print("Błąd krytyczny: Folder 'assets/cards' nie istnieje.")
        return False

    app = QApplication(sys.argv)
    window = SolitaireWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()