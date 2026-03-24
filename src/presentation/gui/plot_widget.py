# src/presentation/gui/plot_widget.py
"""
PlotWidget — matplotlib canvas embedded in Qt.
Supports: empty state, loading state, error state, 2D/3D UMAP plot.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np


class PlotWidget(QWidget):

    def __init__(self, panel_index: int = 0, parent=None):
        super().__init__(parent)
        self.panel_index = panel_index
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.figure = Figure(figsize=(5, 4), tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.ax = self.figure.add_subplot(111)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

        self._show_empty()

    # ── Public API ────────────────────────────────────────────────────────────

    def show_loading(self):
        self._clear()
        self.ax.text(
            0.5, 0.5, "Computing UMAP…",
            ha="center", va="center",
            transform=self.ax.transAxes,
            fontsize=13, color="#888888",
            style="italic"
        )
        self.ax.set_axis_off()
        self.canvas.draw()

    def show_error(self, msg: str):
        self._clear()
        self.ax.text(
            0.5, 0.5, f"Error:\n{msg}",
            ha="center", va="center",
            transform=self.ax.transAxes,
            fontsize=10, color="#cc3333",
            wrap=True
        )
        self.ax.set_axis_off()
        self.canvas.draw()

    def update_plot(self, embedding: np.ndarray, title: str = "UMAP"):
        self._clear()

        if embedding.ndim != 2 or embedding.shape[1] < 2:
            self.show_error(f"Unexpected embedding shape: {embedding.shape}")
            return

        if embedding.shape[1] >= 3:
            # 2D scatter, UMAP3 as color
            sc = self.ax.scatter(
                embedding[:, 0],
                embedding[:, 1],
                c=embedding[:, 2],
                s=1,
                cmap="Spectral_r",
                alpha=0.7,
                linewidths=0,
                rasterized=True,
            )
            self.figure.colorbar(sc, ax=self.ax, label="UMAP 3", fraction=0.03, pad=0.02)
            self.ax.set_xlabel("UMAP 1", fontsize=9)
            self.ax.set_ylabel("UMAP 2", fontsize=9)
        else:
            # plain 2D
            self.ax.scatter(
                embedding[:, 0],
                embedding[:, 1],
                s=1,
                alpha=0.6,
                linewidths=0,
                rasterized=True,
            )
            self.ax.set_xlabel("UMAP 1", fontsize=9)
            self.ax.set_ylabel("UMAP 2", fontsize=9)

        self.ax.set_title(title, fontsize=10, fontweight="bold", pad=6)
        self.ax.tick_params(labelsize=8)

        n_cells = embedding.shape[0]
        self.ax.text(
            0.01, 0.01, f"n = {n_cells:,}",
            transform=self.ax.transAxes,
            fontsize=8, color="#888888",
            va="bottom"
        )

        self.canvas.draw()

    # ── Private ───────────────────────────────────────────────────────────────

    def _clear(self):
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)

    def _show_empty(self):
        self.ax.text(
            0.5, 0.5, f"Panel {self.panel_index + 1}\n\nSelect files and press Run UMAP",
            ha="center", va="center",
            transform=self.ax.transAxes,
            fontsize=11, color="#aaaaaa",
            multialignment="center"
        )
        self.ax.set_axis_off()
        self.canvas.draw()