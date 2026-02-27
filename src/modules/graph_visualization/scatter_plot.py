import matplotlib.pyplot as plt
import numpy as np


class UMAPScatterPlot:

    @staticmethod
    def plot_2d_with_3rd_color(embedding: np.ndarray, title: str = "UMAP", save_path: str = None):

        sc = plt.scatter(
            *embedding[:, :2].T,
            s=1,
            c=embedding[:, 2],
            cmap='Spectral_r'
        )

        plt.title(title, fontsize=14, fontweight='bold')
        plt.xlabel('UMAP1', fontsize=15)
        plt.ylabel('UMAP2', fontsize=15)
        plt.colorbar(sc, label='UMAP3')

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')

        plt.show()