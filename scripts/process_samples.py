#głowny skrypt

from src.services.umap_service import UMAPService
from src.modules.graph_visualization.scatter_plot import UMAPScatterPlot


def main():
    control = r"C:\Users\katar\Desktop\umap\Flow cytometry data\Nowy folder\Helthy female\K7\Control NB NK CELLS BLOOD K7 mama 15-10-2020_STAINED FCS from LymphocytesGate.fcs"
    samples = [
        {
            'name': 'CD3+ Gate',
            'stained': r"C:\Users\katar\Desktop\umap\Flow cytometry data\Nowy folder\Helthy female\K7\NK CELLS BLOOD K7 15-10-2020_STAINED FCS from CD3+Gate.fcs",
            'control': control
        },
        {
            'name': 'Lymphocyte Gate',
            'stained': r"C:\Users\katar\Desktop\umap\Flow cytometry data\Nowy folder\Helthy female\K7\NK CELLS BLOOD K7 15-10-2020_STAINED FCS from LymphocytesGate.fcs",
            'control': control
        },
        {
            'name': 'Not CD3+ Gate',
            'stained': r"C:\Users\katar\Desktop\umap\Flow cytometry data\Nowy folder\Helthy female\K7\NK CELLS BLOOD K7 15-10-2020_STAINED FCS from_NOT(CD3+)Gate.fcs",
            'control': control
        },
        {
            'name': 'NK Gate',
            'stained': r"C:\Users\katar\Desktop\umap\Flow cytometry data\Nowy folder\Helthy female\K7\NK CELLS BLOOD K7 15-10-2020_STAINED FCS from NK cellsGate.fcs",
            'control': control
        },
        {
            'name': 'All events Gate',
            'stained': r"C:\Users\katar\Desktop\umap\Flow cytometry data\Nowy folder\Helthy female\K7\NK CELLS BLOOD K7 15-10-2020_STAINED FCS from ALL evts Gate.fcs",
            'control': r"C:\Users\katar\Desktop\umap\Flow cytometry data\Nowy folder\Helthy female\K7\Control NB NK CELLS BLOOD K7 mama 15-10-2020_STAINED FCS from All evtsGate.fcs"
        },
    ]

    service = UMAPService()

    embeddings = []
    for sample in samples:
        emb = service.process_sample(
            sample['stained'],
            sample['control'],
            sample['name'],
            use_cache=True
        )
        embeddings.append((sample['name'], emb))

    for name, embedding in embeddings:
        UMAPScatterPlot.plot_2d_with_3rd_color(embedding, title=name)


if __name__ == "__main__":
    main()