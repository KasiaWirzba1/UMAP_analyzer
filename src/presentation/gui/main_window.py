# src/presentation/gui/main_window.py
"""
DiaNA - UMAP Analyzer
4-panel comparison GUI. No config.py needed — user selects files directly.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QLabel, QGroupBox,
    QFileDialog, QScrollArea, QSizePolicy, QFrame, QSplitter, QDialog, QFormLayout, QSpinBox, QDoubleSpinBox, QTabWidget
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont
from src.services.umap_service import UMAPService
from .plot_widget import PlotWidget


# ── Background worker thread (keeps GUI responsive during UMAP) ──────────────

class UMAPWorker(QThread):
    finished = Signal(object, str)   # embedding, title
    error    = Signal(str)

    def __init__(self, service, stained_path, control_path, sample_name,
                 n_neighbors, min_dist, n_components, cofactor):
        super().__init__()
        self.service       = service
        self.stained_path  = stained_path
        self.control_path  = control_path
        self.sample_name   = sample_name
        self.n_neighbors   = n_neighbors
        self.min_dist      = min_dist
        self.n_components  = n_components
        self.cofactor      = cofactor

    def run(self):
        try:
            embedding = self.service.process_sample(
                stained_path  = self.stained_path,
                control_path  = self.control_path,
                sample_name   = self.sample_name,
                n_neighbors   = self.n_neighbors,
                min_dist      = self.min_dist,
                n_components  = self.n_components,
                cofactor      = self.cofactor,
                use_cache     = False,   # live computation, no precompute needed
            )
            title = f"{self.sample_name}  |  n={self.n_neighbors}"
            self.finished.emit(embedding, title)
        except Exception as e:
            self.error.emit(str(e))

# ── Parameters dialog ────────────────────────────────────────────────────────

class UMAPParamsDialog(QDialog):

    def __init__(self, current_params: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Modify graph")
        self.setFixedWidth(360)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 16, 16, 16)

        # ── Zakładki ──────────────────────────────────────────────────────────
        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_parameters_tab(current_params), "Parameters")
        self.tabs.addTab(self._build_visualization_tab(current_params), "Visualization")
        self.tabs.addTab(self._build_labels_tab(current_params), "Axes & Labels")
        self.tabs.addTab(self._build_color_tab(current_params), "Color")
        layout.addWidget(self.tabs)

        # ── Przyciski ─────────────────────────────────────────────────────────
        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("Cancel")
        btn_ok     = QPushButton("Apply")
        btn_ok.setDefault(True)
        btn_cancel.clicked.connect(self.reject)
        btn_ok.clicked.connect(self.accept)
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_ok)
        layout.addLayout(btn_layout)

    # ── Zakładka 1: Parameters ────────────────────────────────────────────────
    def _build_parameters_tab(self, p: dict) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        form.setSpacing(8)
        form.setContentsMargins(8, 12, 8, 8)

        self.neighbors_spin = QSpinBox()
        self.neighbors_spin.setRange(2, 200)
        self.neighbors_spin.setValue(p.get("n_neighbors", 15))
        form.addRow("n_neighbors:", self.neighbors_spin)

        self.min_dist_spin = QDoubleSpinBox()
        self.min_dist_spin.setRange(0.0, 1.0)
        self.min_dist_spin.setSingleStep(0.05)
        self.min_dist_spin.setDecimals(2)
        self.min_dist_spin.setValue(p.get("min_dist", 0.1))
        form.addRow("min_dist:", self.min_dist_spin)

        self.components_spin = QSpinBox()
        self.components_spin.setRange(2, 10)
        self.components_spin.setValue(p.get("n_components", 3))
        form.addRow("n_components:", self.components_spin)

        self.cofactor_spin = QDoubleSpinBox()
        self.cofactor_spin.setRange(1.0, 10000.0)
        self.cofactor_spin.setSingleStep(10.0)
        self.cofactor_spin.setDecimals(1)
        self.cofactor_spin.setValue(p.get("cofactor", 150.0))
        form.addRow("cofactor:", self.cofactor_spin)

        return w

    # ── Zakładka 2: Visualization ─────────────────────────────────────────────
    def _build_visualization_tab(self, p: dict) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(8, 12, 8, 8)
        layout.addWidget(QLabel("(wkrótce)"))
        layout.addStretch()
        return w

    # ── Zakładka 3: Axes & Labels ─────────────────────────────────────────────
    def _build_labels_tab(self, p: dict) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(8, 12, 8, 8)
        layout.addWidget(QLabel("(wkrótce)"))
        layout.addStretch()
        return w

    # ── Zakładka 4: Color ─────────────────────────────────────────────────────
    def _build_color_tab(self, p: dict) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(8, 12, 8, 8)
        layout.addWidget(QLabel("(wkrótce)"))
        layout.addStretch()
        return w

    # ── Getter ────────────────────────────────────────────────────────────────
    def get_params(self) -> dict:
        return {
            "n_neighbors":  self.neighbors_spin.value(),
            "min_dist":     self.min_dist_spin.value(),
            "n_components": self.components_spin.value(),
            "cofactor":     self.cofactor_spin.value(),
        }

# ── Single panel control block ───────────────────────────────────────────────

class PanelControl(QGroupBox):
    """Left-sidebar block for one panel (stained + control + params + run)."""

    run_requested = Signal(int)   # emits panel index

    def __init__(self, index: int, parent=None):
        super().__init__(f"Panel {index + 1}", parent)
        self.index         = index
        self.stained_path  = None
        self.control_path  = None
        self.umap_params = {
            "n_neighbors": 15,
            "min_dist": 0.1,
            "n_components": 3,
            "cofactor": 150.0,
        }
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(8, 12, 8, 8)

        # ── Stained file ──
        layout.addWidget(self._small_label("Stained file"))
        self.stained_lbl = self._path_label()
        layout.addWidget(self.stained_lbl)
        btn_s = QPushButton("Browse stained…")
        btn_s.setFixedHeight(24)
        btn_s.clicked.connect(self._browse_stained)
        layout.addWidget(btn_s)

        # ── Control file ──
        layout.addWidget(self._small_label("Control file"))
        self.control_lbl = self._path_label()
        layout.addWidget(self.control_lbl)
        btn_c = QPushButton("Browse control…")
        btn_c.setFixedHeight(24)
        btn_c.clicked.connect(self._browse_control)
        layout.addWidget(btn_c)

        # ── Run button ──
        self.run_btn = QPushButton("▶  Run UMAP")
        self.run_btn.setFixedHeight(28)
        self.run_btn.setEnabled(False)
        self.run_btn.clicked.connect(lambda: self.run_requested.emit(self.index))
        layout.addWidget(self.run_btn)

        # ── Modify params button ──
        self.modify_btn = QPushButton("⚙  Modify graph")
        self.modify_btn.setFixedHeight(24)
        self.modify_btn.setEnabled(False)
        self.modify_btn.clicked.connect(self._open_params_dialog)
        layout.addWidget(self.modify_btn)

        # ── Status line ──
        self.status_lbl = QLabel("no files selected")
        ...

        # ── Status line ──
        self.status_lbl = QLabel("no files selected")
        self.status_lbl.setWordWrap(True)
        self.status_lbl.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(self.status_lbl)

    def _open_params_dialog(self):
        dialog = UMAPParamsDialog(current_params=self.umap_params, parent=self)
        if dialog.exec():  # użytkownik kliknął Apply
            self.umap_params = dialog.get_params()
            n = self.umap_params["n_neighbors"]
            d = self.umap_params["min_dist"]
            self.status_lbl.setText(
                f"params: n={n}, dist={d}"
            )

    # ── helpers ──────────────────────────────────────────────────────────────

    def _small_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet("font-size: 10px; color: gray; margin-top: 4px;")
        return lbl

    def _path_label(self) -> QLabel:
        lbl = QLabel("—")
        lbl.setStyleSheet(
            "font-size: 10px; background: palette(base); "
            "border: 1px solid palette(mid); border-radius: 3px; padding: 2px 4px;"
        )
        lbl.setWordWrap(False)
        lbl.setTextFormat(Qt.PlainText)
        lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        return lbl

    def _browse_stained(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select stained FCS file", "", "FCS files (*.fcs);;All files (*)"
        )
        if path:
            self.stained_path = path
            self.stained_lbl.setText(path.split("/")[-1].split("\\")[-1])
            self.stained_lbl.setToolTip(path)
            self._refresh_run_btn()

    def _browse_control(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select control FCS file", "", "FCS files (*.fcs);;All files (*)"
        )
        if path:
            self.control_path = path
            self.control_lbl.setText(path.split("/")[-1].split("\\")[-1])
            self.control_lbl.setToolTip(path)
            self._refresh_run_btn()

    def _refresh_run_btn(self):
        ready = bool(self.stained_path and self.control_path)
        self.run_btn.setEnabled(ready)
        self.modify_btn.setEnabled(ready)
        if ready:
            self.status_lbl.setText("ready — press Run UMAP")
        else:
            missing = []
            if not self.stained_path: missing.append("stained")
            if not self.control_path: missing.append("control")
            self.status_lbl.setText(f"missing: {', '.join(missing)}")

    def set_computing(self, is_computing: bool):
        self.run_btn.setEnabled(not is_computing)
        self.run_btn.setText("⏳  Computing…" if is_computing else "▶  Run UMAP")
        if is_computing:
            self.status_lbl.setText("running UMAP…")

    def set_done(self, title: str):
        self.run_btn.setEnabled(True)
        self.run_btn.setText("▶  Run UMAP")
        self.status_lbl.setText(f"✓ {title}")

    def set_error(self, msg: str):
        self.run_btn.setEnabled(True)
        self.run_btn.setText("▶  Run UMAP")
        self.status_lbl.setText(f"✗ {msg}")

    @property
    def sample_name(self) -> str:
        if self.stained_path:
            name = self.stained_path.replace("\\", "/").split("/")[-1]
            return name.replace(".fcs", "")
        return f"Panel {self.index + 1}"


# ── Main window ──────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):

    N_PANELS = 4

    def __init__(self):
        super().__init__()
        self.setWindowTitle("DiaNA — UMAP Analyzer")
        self.setGeometry(100, 100, 1500, 860)

        self.service = UMAPService(cache_dir="data/embedding_cache")
        self._workers: list[UMAPWorker | None] = [None] * self.N_PANELS

        self._build_ui()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(6)

        sidebar = self._build_sidebar()
        splitter.addWidget(sidebar)

        plot_area = self._build_plot_area()
        splitter.addWidget(plot_area)

        # Domyślne proporcje: sidebar ~200px, reszta dla wykresów
        splitter.setSizes([200, 1300])
        # Wykresy mogą się kurczyć, sidebar ma minimum
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        root_layout.addWidget(splitter)

    def _build_sidebar(self) -> QWidget:
        container = QWidget()
        container.setMinimumWidth(160)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # App title
        title = QLabel("DiaNA")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("UMAP Analyzer")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: gray; font-size: 11px; margin-bottom: 8px;")
        layout.addWidget(subtitle)

        # Panel controls
        self._panel_controls: list[PanelControl] = []
        for i in range(self.N_PANELS):
            pc = PanelControl(i)
            pc.run_requested.connect(self._on_run)
            self._panel_controls.append(pc)
            layout.addWidget(pc)

        layout.addStretch()
        scroll.setWidget(inner)

        outer = QVBoxLayout(container)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)
        return container

    def _build_plot_area(self) -> QWidget:
        container = QWidget()
        grid = QVBoxLayout(container)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(0)

        self._plot_widgets: list[PlotWidget] = []

        # Row 0: panels 0 & 1
        row0 = QHBoxLayout()
        row0.setSpacing(0)
        for i in range(2):
            pw = PlotWidget(panel_index=i)
            self._plot_widgets.append(pw)
            row0.addWidget(pw)
            if i == 0:
                sep = QFrame()
                sep.setFrameShape(QFrame.VLine)
                sep.setFrameShadow(QFrame.Plain)
                sep.setStyleSheet("color: palette(mid);")
                row0.addWidget(sep)

        # Row 1: panels 2 & 3
        row1 = QHBoxLayout()
        row1.setSpacing(0)
        for i in range(2, 4):
            pw = PlotWidget(panel_index=i)
            self._plot_widgets.append(pw)
            row1.addWidget(pw)
            if i == 2:
                sep = QFrame()
                sep.setFrameShape(QFrame.VLine)
                sep.setFrameShadow(QFrame.Plain)
                sep.setStyleSheet("color: palette(mid);")
                row1.addWidget(sep)

        h_sep = QFrame()
        h_sep.setFrameShape(QFrame.HLine)
        h_sep.setFrameShadow(QFrame.Plain)
        h_sep.setStyleSheet("color: palette(mid);")

        grid.addLayout(row0, stretch=1)
        grid.addWidget(h_sep)
        grid.addLayout(row1, stretch=1)

        return container

    # ── Event handlers ────────────────────────────────────────────────────────

    def _on_run(self, panel_index: int):
        pc = self._panel_controls[panel_index]

        if not pc.stained_path or not pc.control_path:
            return

        pc.set_computing(True)
        self._plot_widgets[panel_index].show_loading()

        worker = UMAPWorker(
            service       = self.service,
            stained_path  = pc.stained_path,
            control_path  = pc.control_path,
            sample_name   = pc.sample_name,
            n_neighbors   = pc.umap_params["n_neighbors"],
            min_dist      = pc.umap_params["min_dist"],
            n_components  = pc.umap_params["n_components"],
            cofactor      = pc.umap_params["cofactor"],
        )
        worker.finished.connect(lambda emb, ttl, idx=panel_index: self._on_done(idx, emb, ttl))
        worker.error.connect(lambda msg, idx=panel_index: self._on_error(idx, msg))

        self._workers[panel_index] = worker
        worker.start()

    def _on_done(self, panel_index: int, embedding, title: str):
        self._panel_controls[panel_index].set_done(title)
        self._plot_widgets[panel_index].update_plot(embedding, title)

    def _on_error(self, panel_index: int, msg: str):
        self._panel_controls[panel_index].set_error(msg)
        self._plot_widgets[panel_index].show_error(msg)