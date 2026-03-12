# scripts/precompute_all.py
from src.services.umap_service import UMAPService

CONTROL_PATH = r"C:\Users\katar\Desktop\umap\Flow cytometry data\Nowy folder\Helthy female\K7\Control NB NK CELLS BLOOD K7 mama 15-10-2020_STAINED FCS from LymphocytesGate.fcs"

SAMPLES = [
    {
        'name': 'CD3+ Gate',
        'stained': r"C:\Users\katar\Desktop\umap\Flow cytometry data\Nowy folder\Helthy female\K7\NK CELLS BLOOD K7 15-10-2020_STAINED FCS from CD3+Gate.fcs",
        'control': CONTROL_PATH
    },
    {
        'name': 'Lymphocyte Gate',
        'stained': r"C:\Users\katar\Desktop\umap\Flow cytometry data\Nowy folder\Helthy female\K7\NK CELLS BLOOD K7 15-10-2020_STAINED FCS from LymphocytesGate.fcs",
        'control': CONTROL_PATH
    },
    {
        'name': 'Not CD3+ Gate',
        'stained': r"C:\Users\katar\Desktop\umap\Flow cytometry data\Nowy folder\Helthy female\K7\NK CELLS BLOOD K7 15-10-2020_STAINED FCS from_NOT(CD3+)Gate.fcs",
        'control': CONTROL_PATH
    },
    {
        'name': 'NK Gate',
        'stained': r"C:\Users\katar\Desktop\umap\Flow cytometry data\Nowy folder\Helthy female\K7\NK CELLS BLOOD K7 15-10-2020_STAINED FCS from NK cellsGate.fcs",
        'control': CONTROL_PATH
    },
    {
        'name': 'All events Gate',
        'stained': r"C:\Users\katar\Desktop\umap\Flow cytometry data\Nowy folder\Helthy female\K7\NK CELLS BLOOD K7 15-10-2020_STAINED FCS from ALL evts Gate.fcs",
        'control': r"C:\Users\katar\Desktop\umap\Flow cytometry data\Nowy folder\Helthy female\K7\Control NB NK CELLS BLOOD K7 mama 15-10-2020_STAINED FCS from All evtsGate.fcs"
    },
]

N_NEIGHBORS_OPTIONS = [10, 15, 20]

# Stałe parametry
MIN_DIST = 0.1
N_COMPONENTS = 3
COFACTOR = 150.0


def main():
    service = UMAPService()
    total = len(SAMPLES) * len(N_NEIGHBORS_OPTIONS)
    current = 0

    for sample in SAMPLES:
        for n_neighbors in N_NEIGHBORS_OPTIONS:
            current += 1
            print(f"[{current}/{total}] {sample['name']} | n_neighbors={n_neighbors}")

            service.process_sample(
                stained_path=sample['stained'],
                control_path=sample['control'],
                sample_name=sample['name'],
                n_neighbors=n_neighbors,
                min_dist=MIN_DIST,
                n_components=N_COMPONENTS,
                cofactor=COFACTOR,
                use_cache=True
            )

    print(f"\nGotowe! Obliczono {total} embeddingów.")


if __name__ == "__main__":
    main()