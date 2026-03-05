# main.py (w UMAP_analyzer/)
"""
Entry point for UMAP Analyzer GUI
"""

import sys
from PySide6.QtWidgets import QApplication
from src.presentation.gui.main_window import MainWindow


def main():
    """Launch GUI application"""

    app = QApplication(sys.argv)

    # Set app metadata
    app.setApplicationName("DiaNA - UMAP Analyzer")
    app.setOrganizationName("ICCVS")

    # Create and show main window
    window = MainWindow()
    window.show()


    sys.exit(app.exec())


if __name__ == "__main__":
    main()