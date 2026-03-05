from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np


class PlotWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Create matplotlib figure
        self.figure = Figure(figsize=(6, 5))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        # Initial empty plot
        self.ax.text(
            0.5, 0.5, 'No data loaded',
            ha='center', va='center',
            transform=self.ax.transAxes,
            fontsize=14, color='gray'
        )
        self.canvas.draw()

    def update_plot(self, embedding: np.ndarray, title: str = "UMAP"):

        # Clear previous plot
        self.ax.clear()

        # Check dimensions
        if embedding.shape[1] == 2:
            # 2D embedding
            self.ax.scatter(
                embedding[:, 0],
                embedding[:, 1],
                s=1,
                alpha=0.5
            )
            self.ax.set_xlabel('UMAP1')
            self.ax.set_ylabel('UMAP2')

        elif embedding.shape[1] == 3:
            #3D embedding → plot 2D with 3rd as color
            sc = self.ax.scatter(
                embedding[:, 0],  # UMAP1 (x)
                embedding[:, 1],  # UMAP2 (y)
                s=1,
                c=embedding[:, 2],  # UMAP3 (color)
                cmap='Spectral_r',
                alpha=0.7
            )

            self.ax.set_xlabel('UMAP1', fontsize=12)
            self.ax.set_ylabel('UMAP2', fontsize=12)

            #Colorbar
            self.figure.colorbar(sc, ax=self.ax, label='UMAP3')

        else:
            self.ax.text(
                0.5, 0.5, f'Unsupported dimensions: {embedding.shape}',
                ha='center', va='center',
                transform=self.ax.transAxes
            )

        # Title
        self.ax.set_title(title, fontsize=14, fontweight='bold')

        self.canvas.draw()