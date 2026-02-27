# src/services/umap_service.py
from src.modules.preprocessor.preprocess import FlowCytometryPreprocessor
from src.modules.embedding.umap_embedder import UMAPEmbedder
from src.modules.preprocessor.cache import EmbeddingCache


class UMAPService:
    def __init__(self, cache_dir="data/embedding_cache"):
        self.cache = EmbeddingCache()

    def process_sample(
            self,
            stained_path: str,
            control_path: str,
            sample_name: str,
            n_neighbors: int = 15,
            min_dist: float = 0.1,
            n_components: int = 3,
            cofactor: float = 150.0,
            use_cache: bool = True):

        # cache
        if use_cache:
            cached = self.cache.load(sample_name)
            if cached is not None:
                print(f"Loaded from cache: {sample_name}")
                return cached

        print(f"Computing: {sample_name}")

        #Preprocessing
        stained_data, control_median = FlowCytometryPreprocessor.load_sample_pair(
            stained_path,
            control_path,
            skip_first_n=2
        )

        print("Preprocessing data")
        preprocessed_data = FlowCytometryPreprocessor.preprocess_data(
            stained_data,
            control_median,
            cofactor=cofactor
        )
        umap_data = self.preprocessor.full_pipeline(stained_path, control_path, cofactor=150.0)

        embedder = UMAPEmbedder(n_neighbors=15, min_dist=0.1, n_components=3)
        embedding = embedder.fit_transform(umap_data)

        if use_cache:
            print("Saving to cache")
            self.cache.save(
                sample_name,
                embedding,
                method='umap',
                params={
                    'n_neighbors': n_neighbors,
                    'min_dist': min_dist,
                    'n_components': n_components,
                    'cofactor': cofactor
                }
            )

        return embedding