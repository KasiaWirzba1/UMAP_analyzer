# src/config.py
"""
Centralna konfiguracja projektu DiaNA.
Edytuj ścieżki tutaj — zmiany propagują się automatycznie wszędzie.
"""

from pathlib import Path

# --- ID ---
SAMPLE_ID = "K1"

# --- Katalog bazowy z danymi FCS ---
DATA_ROOT = Path(r"F:\dane\UMAP datasets\UMAP datasets\K1  21-01-2020 MALE")

# --- Plik kontrolny ---
CONTROL_PATH = DATA_ROOT / "Control_NB_BLOOD NK CELLS K1  21-01-2020 from LymphocytesGate.fcs"
CONTROL_PATH_ALL_EVTS = DATA_ROOT / "Control_NB_BLOOD NK CELLS K1  21-01-2020 from ALLevtsGate.fcs"

# --- Definicja próbek ---
SAMPLES = [
    {
        'name': f'{SAMPLE_ID} CD3+ Gate',
        'stained': DATA_ROOT / "NK CELLS BLOOD K1  21-01-2020_STAINED_FCS from CD3+Gate.fcs",
        'control': CONTROL_PATH,
    },
    {
        'name': f'{SAMPLE_ID} Lymphocyte Gate',
        'stained': DATA_ROOT / "NK CELLS BLOOD K1  21-01-2020_STAINED_FCS from LymphocytesGate.fcs",
        'control': CONTROL_PATH,
    },
    {
        'name': f'{SAMPLE_ID} Not CD3+ Gate',
        'stained': DATA_ROOT / "NK CELLS BLOOD K1  21-01-2020_STAINED_FCS from_NOT(CD3+)Gate.fcs",
        'control': CONTROL_PATH,
    },
    {
        'name': f'{SAMPLE_ID} NK Gate',
        'stained': DATA_ROOT / "NK CELLS BLOOD K1  21-01-2020_STAINED_FCS from NK cellsGate.fcs",
        'control': CONTROL_PATH,
    },
    {
        'name': f'{SAMPLE_ID} All events Gate',
        'stained': DATA_ROOT / "NK CELLS BLOOD K1  21-01-2020_STAINED_FCS from AllevtsGate.fcs",
        'control': CONTROL_PATH_ALL_EVTS,
    },
]

# --- Parametry UMAP ---
N_NEIGHBORS_OPTIONS = [10, 15, 20]
MIN_DIST = 0.1
N_COMPONENTS = 3
COFACTOR = 150.0