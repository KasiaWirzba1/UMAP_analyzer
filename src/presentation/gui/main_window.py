""" Main GUI window for UMAP analyzer """

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QLabel, QCheckBox,
    QGroupBox
)
from PySide6.QtCore import Qt
from src.services.umap_service import UMAPService
from .plot_widget import PlotWidget


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("DiaNA - UMAP Analyzer")
        self.setGeometry(100, 100, 1400, 800)

        # Initialize service
        self.service = UMAPService(cache_dir="data/embeddings")

        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        """Setup user interface"""

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout (horizontal: controls | plots)
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)


        controls_widget = self.create_controls()
        main_layout.addWidget(controls_widget, stretch=1)


        plots_layout = QHBoxLayout()

        # Left plot
        self.plot_left = PlotWidget()
        plots_layout.addWidget(self.plot_left)

        # Right plot
        self.plot_right = PlotWidget()
        plots_layout.addWidget(self.plot_right)

        main_layout.addLayout(plots_layout, stretch=3)

    def create_controls(self) -> QWidget:
        """Create controls panel"""

        controls = QWidget()
        layout = QVBoxLayout()
        controls.setLayout(layout)


        sample_group = QGroupBox("Sample Selection")
        sample_layout = QVBoxLayout()
        sample_group.setLayout(sample_layout)

        # Sample dropdown
        sample_layout.addWidget(QLabel("Sample:"))
        self.sample_selector = QComboBox()
        self.sample_selector.addItems([
            "CD3+ Gate",
            "Lymphocyte Gate",
            "NK Gate",
            "Not CD3+ Gate",
            "All events Gate"
        ])
        sample_layout.addWidget(self.sample_selector)

        layout.addWidget(sample_group)


        params_group = QGroupBox("UMAP Parameters")
        params_layout = QVBoxLayout()
        params_group.setLayout(params_layout)

        # n_neighbors
        # daj to:
        params_layout.addWidget(QLabel("n_neighbors:"))
        self.neighbors_combo = QComboBox()
        self.neighbors_combo.addItems(["10", "15", "20"])
        self.neighbors_combo.setCurrentText("15")
        params_layout.addWidget(self.neighbors_combo)
        layout.addWidget(params_group)

        self.use_cache_checkbox = QCheckBox("Use cache")
        self.use_cache_checkbox.setChecked(True)
        layout.addWidget(self.use_cache_checkbox)

        self.load_left_btn = QPushButton("Load to LEFT plot")
        self.load_left_btn.clicked.connect(self.load_to_left)
        layout.addWidget(self.load_left_btn)

        self.load_right_btn = QPushButton("Load to RIGHT plot")
        self.load_right_btn.clicked.connect(self.load_to_right)
        layout.addWidget(self.load_right_btn)

        self.status_label = QLabel("Ready")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        # Spacer
        layout.addStretch()

        return controls


    def load_to_left(self):
        """Load sample to left plot"""
        self.load_sample(self.plot_left, "LEFT")

    def load_to_right(self):
        """Load sample to right plot"""
        self.load_sample(self.plot_right, "RIGHT")

    def load_sample(self, plot_widget: PlotWidget, side: str):
        """
        Load sample and display in plot

        Args:
            plot_widget: PlotWidget to update
            side: "LEFT" or "RIGHT"
        """

        # Get parameters
        sample_name = self.sample_selector.currentText()
        n_neighbors = int(self.neighbors_combo.currentText())
        min_dist = 0.1
        n_components = 3
        cofactor = 150.0
        use_cache = self.use_cache_checkbox.isChecked()

        # Update status
        self.status_label.setText(f"Loading {sample_name} to {side}...")

        # TODO: Replace with your actual file paths!
        # This is just an example structure
        control_path = "data/raw/Control_NB_NK_CELLS.fcs"

        stained_paths = {
            "CD3+ Gate": "data/raw/NK_CELLS_CD3+Gate.fcs",
            "Lymphocyte Gate": "data/raw/NK_CELLS_LymphocyteGate.fcs",
            "NK Gate": "data/raw/NK_CELLS_NKGate.fcs",
            "Not CD3+ Gate": "data/raw/NK_CELLS_NotCD3+Gate.fcs",
            "All events Gate": "data/raw/NK_CELLS_AllEventsGate.fcs"
        }

        stained_path = stained_paths.get(sample_name)

        if not stained_path:
            self.status_label.setText(f"Unknown sample: {sample_name}")
            return

        try:
            # Process sample
            embedding = self.service.process_sample(
                stained_path=stained_path,
                control_path=control_path,
                sample_name=sample_name,
                n_neighbors=n_neighbors,
                min_dist=min_dist,
                n_components=n_components,
                cofactor=cofactor,
                use_cache=use_cache
            )

            # Update plot
            plot_widget.update_plot(embedding, title=sample_name)

            # Update status
            self.status_label.setText(
                f"Loaded {sample_name} to {side}\n"
                f"Shape: {embedding.shape}\n"
                f"n={n_neighbors}, dist={min_dist}, cof={cofactor}"
            )

        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")