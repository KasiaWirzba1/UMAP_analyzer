# scripts/process_samples.py
from src.config import SAMPLES
from src.services.umap_service import UMAPService
from src.modules.graph_visualization.scatter_plot import UMAPScatterPlot


def main():
    service = UMAPService()

    embeddings = []
    for sample in SAMPLES:
        emb = service.process_sample(
            stained_path=str(sample['stained']),
            control_path=str(sample['control']),
            sample_name=sample['name'],
            use_cache=True
        )
        embeddings.append((sample['name'], emb))

    for name, embedding in embeddings:
        UMAPScatterPlot.plot_2d_with_3rd_color(embedding, title=name)


if __name__ == "__main__":
    main()