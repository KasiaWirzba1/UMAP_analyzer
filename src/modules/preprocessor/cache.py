""" Cache system for UMAP embeddings
Saves/loads embeddings to/from disk for instant loading """

import numpy as np
import json
from pathlib import Path
from typing import Optional, Dict, Any


class EmbeddingCache:

    def __init__(self, cache_dir: str = "data/embeddings"):
        """
        Initialize cache

        Args:
            cache_dir: Directory to store cached embeddings
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.metadata_file = self.cache_dir / "metadata.json"
        self.metadata = self._load_metadata()

    def _load_metadata(self) -> Dict:
        """Load metadata from disk"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_metadata(self):
        """Save metadata to disk"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)

    def save(
            self,
            cache_key: str,
            embedding: np.ndarray,
            params: Optional[Dict[str, Any]] = None
    ):

        cache_path = self.cache_dir / f"{cache_key}.npy"

        # Save embedding
        np.save(cache_path, embedding)

        # Update metadata
        self.metadata[cache_key] = {
            'path': str(cache_path),
            'shape': list(embedding.shape),
            'params': params or {},
            'size_mb': round(cache_path.stat().st_size / (1024 * 1024), 3)
        }

        self._save_metadata()

        print(f"💾 Saved to cache: {cache_key}")

    def load(self, cache_key: str) -> Optional[np.ndarray]:

        cache_path = self.cache_dir / f"{cache_key}.npy"

        if cache_path.exists():
            embedding = np.load(cache_path)
            print(f"✅ Loaded from cache: {cache_key}")
            return embedding

        return None

    def exists(self, cache_key: str) -> bool:
        """Check if embedding exists in cache"""
        cache_path = self.cache_dir / f"{cache_key}.npy"
        return cache_path.exists()

    def get_info(self, cache_key: str) -> Optional[Dict]:
        """Get metadata about cached embedding"""
        return self.metadata.get(cache_key)

    def list_all(self) -> Dict:
        """List all cached embeddings"""
        return self.metadata

    def delete(self, cache_key: str) -> bool:

        cache_path = self.cache_dir / f"{cache_key}.npy"

        if cache_path.exists():
            cache_path.unlink()

            if cache_key in self.metadata:
                del self.metadata[cache_key]
                self._save_metadata()

            print(f"🗑️  Deleted from cache: {cache_key}")
            return True

        return False

    def clear_all(self):
        """Delete all cached embeddings"""
        for cache_key in list(self.metadata.keys()):
            self.delete(cache_key)

        print("🗑Cleared all cache")

    def save(
            self,
            cache_key: str,
            embedding: np.ndarray,
            method: str = 'umap',
            params: Optional[Dict[str, Any]] = None
    ):
        cache_path = self.cache_dir / f"{cache_key}.npy"
        np.save(cache_path, embedding)

        self.metadata[cache_key] = {
            'path': str(cache_path),
            'shape': list(embedding.shape),
            'method': method,
            'params': params or {},
            'size_mb': round(cache_path.stat().st_size / (1024 * 1024), 3)
        }

        self._save_metadata()
        print(f"Saved to cache: {cache_key}")