# scripts/precompute_all.py
from src.config import SAMPLES, N_NEIGHBORS_OPTIONS, MIN_DIST, N_COMPONENTS, COFACTOR
from src.services.umap_service import UMAPService


def main():
    service = UMAPService()
    total = len(SAMPLES) * len(N_NEIGHBORS_OPTIONS)
    current = 0

    for sample in SAMPLES:
        for n_neighbors in N_NEIGHBORS_OPTIONS:
            current += 1
            print(f"[{current}/{total}] {sample['name']} | n_neighbors={n_neighbors}")

            service.process_sample(
                stained_path=str(sample['stained']),
                control_path=str(sample['control']),
                sample_name=sample['name'],
                n_neighbors=n_neighbors,
                min_dist=MIN_DIST,
                n_components=N_COMPONENTS,
                cofactor=COFACTOR,
                use_cache=True,
            )
            # sample_name jest przekazywany → zostanie zapisany w params cache
            # dzięki temu GUI może odczytać dostępne kombinacje

    print(f"\nGotowe! Obliczono {total} embeddingów.")


if __name__ == "__main__":
    main()