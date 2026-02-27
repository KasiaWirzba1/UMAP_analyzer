# src/modules/embedding/umap_embedder.py
import umap
import numpy as np


class UMAPEmbedder:


    def __init__(self, n_neighbors: int = 15, min_dist: float = 0.1, n_components: int = 3):
        self.n_neighbors = n_neighbors
        self.min_dist = min_dist
        self.n_components = n_components

    def fit_transform(self, data: np.ndarray) -> np.ndarray:

        reducer = umap.UMAP(
            n_neighbors=self.n_neighbors,
            min_dist=self.min_dist,
            n_components=self.n_components
        )
        embedding = reducer.fit_transform(data)

        return embedding