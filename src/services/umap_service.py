# src/services/umap_service.py
from src.modules.preprocessor.preprocess import FlowCytometryPreprocessor
from src.modules.embedding.umap_embedder import UMAPEmbedder
from src.modules.preprocessor.cache import EmbeddingCache


class UMAPService:
    def __init__(self, cache_dir="data/embedding_cache"):
        self.cache = EmbeddingCache(cache_dir)

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

        # Klucz cache uwzględnia wszystkie parametry
        cache_key = (
            f"{sample_name}"
            f"_nn{n_neighbors}"
            f"_md{min_dist}"
            f"_nc{n_components}"
            f"_cf{cofactor}"
        )

        if use_cache:
            cached = self.cache.load(cache_key)
            if cached is not None:
                print(f"Loaded from cache: {cache_key}")
                return cached

        print(f"Computing: {sample_name}")

        # Preprocessing
        stained_data, control_median = FlowCytometryPreprocessor.load_sample_pair(
            stained_path,
            control_path,
            skip_first_n=2
        )

        print("Preprocessing data...")
        preprocessed_data = FlowCytometryPreprocessor.preprocess_data(
            stained_data,
            control_median,
            cofactor=cofactor
        )

        # Embedding
        embedder = UMAPEmbedder(
            n_neighbors=n_neighbors,
            min_dist=min_dist,
            n_components=n_components
        )
        embedding = embedder.fit_transform(preprocessed_data)

        if use_cache:
            print("Saving to cache...")
            self.cache.save(
                cache_key,
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