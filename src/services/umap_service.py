# src/services/umap_service.py
from src.modules.preprocessor.preprocess import FlowCytometryPreprocessor
from src.modules.embedding.umap_embedder import UMAPEmbedder
from src.modules.preprocessor.cache import EmbeddingCache


class UMAPService:
    def __init__(self, cache_dir="data/embedding_cache"):
        self.cache = EmbeddingCache(cache_dir)

    def get_available_combinations(self) -> dict[str, list[int]]:
        """
        Czyta cache i zwraca słownik:
            { nazwa_próbki: [n_neighbors_1, n_neighbors_2, ...] }
        Tylko te kombinacje, które faktycznie są w cache.
        """
        result: dict[str, list[int]] = {}

        for key, meta in self.cache.list_all().items():
            params = meta.get('params', {})
            sample_name = params.get('sample_name')
            n_neighbors = params.get('n_neighbors')

            if sample_name is None or n_neighbors is None:
                continue

            result.setdefault(sample_name, [])
            if n_neighbors not in result[sample_name]:
                result[sample_name].append(n_neighbors)

        # Posortuj n_neighbors dla każdej próbki
        for name in result:
            result[name].sort()

        return result

    def load_from_cache(self, sample_name: str, n_neighbors: int,
                        min_dist: float = 0.1, n_components: int = 3,
                        cofactor: float = 150.0):
        """
        Ładuje embedding wyłącznie z cache.
        Rzuca ValueError jeśli kombinacja nie istnieje.
        """
        cache_key = self._make_key(sample_name, n_neighbors, min_dist, n_components, cofactor)
        embedding = self.cache.load(cache_key)

        if embedding is None:
            raise ValueError(
                f"Brak embeddingu w cache: {cache_key}\n"
                f"Uruchom scripts/precompute_all.py aby go wygenerować."
            )

        return embedding

    def process_sample(self, stained_path: str, control_path: str, sample_name: str,
                       n_neighbors: int = 15, min_dist: float = 0.1,
                       n_components: int = 3, cofactor: float = 150.0,
                       use_cache: bool = True):
        """
        Pełny pipeline: preprocessing → UMAP → zapis do cache.
        Używany tylko przez precompute_all.py.
        """
        cache_key = self._make_key(sample_name, n_neighbors, min_dist, n_components, cofactor)

        if use_cache:
            cached = self.cache.load(cache_key)
            if cached is not None:
                return cached

        print(f"Computing: {sample_name}")

        stained_data, control_median = FlowCytometryPreprocessor.load_sample_pair(
            stained_path, control_path, skip_first_n=2
        )

        print("Preprocessing data...")
        preprocessed_data = FlowCytometryPreprocessor.preprocess_data(
            stained_data, control_median, cofactor=cofactor
        )

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
                    'sample_name': sample_name,
                    'n_neighbors': n_neighbors,
                    'min_dist': min_dist,
                    'n_components': n_components,
                    'cofactor': cofactor
                }
            )

        return embedding

    @staticmethod
    def _make_key(sample_name: str, n_neighbors: int, min_dist: float,
                  n_components: int, cofactor: float) -> str:
        return (
            f"{sample_name}"
            f"_nn{n_neighbors}"
            f"_md{min_dist}"
            f"_nc{n_components}"
            f"_cf{cofactor}"
        )