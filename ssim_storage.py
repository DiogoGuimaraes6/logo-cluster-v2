import json
import os
from pathlib import Path
from typing import Dict, Tuple, List
import numpy as np

class SSIMStorage:
    def __init__(self, storage_dir: str = "ssim_data"):
        """Initialize SSIM storage with a directory to store the data."""
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
    def save_ssim_scores(self, ssim_scores: Dict[Tuple[str, str], float], 
                        metadata: dict = None, name: str = "ssim_scores"):
        """
        Save SSIM scores to a JSON file.
        
        Args:
            ssim_scores: Dictionary mapping (file1, file2) tuples to SSIM scores
            metadata: Optional dictionary containing metadata about the scores
            name: Name for the saved file (without extension)
        """
        # Convert tuple keys to strings for JSON serialization
        serializable_scores = {
            f"{f1}|{f2}": float(score)  # Convert numpy float to Python float
            for (f1, f2), score in ssim_scores.items()
        }
        
        data = {
            "scores": serializable_scores,
            "metadata": metadata or {}
        }
        
        output_file = self.storage_dir / f"{name}.json"
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
            
        return output_file
    
    def load_ssim_scores(self, name: str = "ssim_scores") -> Tuple[Dict[Tuple[str, str], float], dict]:
        """
        Load SSIM scores from a JSON file.
        
        Args:
            name: Name of the file to load (without extension)
            
        Returns:
            Tuple of (ssim_scores dictionary, metadata dictionary)
        """
        input_file = self.storage_dir / f"{name}.json"
        if not input_file.exists():
            raise FileNotFoundError(f"No SSIM scores found at {input_file}")
            
        with open(input_file, 'r') as f:
            data = json.load(f)
            
        # Convert string keys back to tuples
        ssim_scores = {
            tuple(k.split('|')): float(v)
            for k, v in data["scores"].items()
        }
        
        return ssim_scores, data["metadata"]
    
    def save_clusters(self, clusters: List[set], metadata: dict = None, name: str = "clusters"):
        """
        Save clusters to a JSON file.
        
        Args:
            clusters: List of sets containing file paths
            metadata: Optional dictionary containing metadata about the clusters
            name: Name for the saved file (without extension)
        """
        # Convert sets to lists for JSON serialization
        serializable_clusters = [list(cluster) for cluster in clusters]
        
        data = {
            "clusters": serializable_clusters,
            "metadata": metadata or {}
        }
        
        output_file = self.storage_dir / f"{name}.json"
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
            
        return output_file
    
    def load_clusters(self, name: str = "clusters") -> Tuple[List[set], dict]:
        """
        Load clusters from a JSON file.
        
        Args:
            name: Name of the file to load (without extension)
            
        Returns:
            Tuple of (list of clusters as sets, metadata dictionary)
        """
        input_file = self.storage_dir / f"{name}.json"
        if not input_file.exists():
            raise FileNotFoundError(f"No clusters found at {input_file}")
            
        with open(input_file, 'r') as f:
            data = json.load(f)
            
        # Convert lists back to sets
        clusters = [set(cluster) for cluster in data["clusters"]]
        
        return clusters, data["metadata"]
    
    def load_block4_similarities(self, path: str = "block4_similarities.json") -> Dict[Tuple[str, str], float]:
        """
        Load block4_conv3 cosine similarities from the specified JSON file in the project root.
        Returns a dict mapping (file1, file2) to float.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"No block4 similarities found at {path}")
        with open(path, 'r') as f:
            data = json.load(f)
        # The file is a flat dict: {"logo1.png|logo2.png": score, ...}
        similarities = {tuple(k.split('|')): float(v) for k, v in data.items()}
        return similarities
    
    def load_block4_similarities_for_set(self, set_type: str) -> dict:
        """
        Load block4_conv3 cosine similarities for a specific set (A, B, ...).
        Returns a dict mapping (file1, file2) to float.
        """
        filename = f"block4_similarities_pngs_{set_type}_inkscape_512.json"
        if not os.path.exists(filename):
            raise FileNotFoundError(f"No block4 similarities found at {filename}")
        with open(filename, 'r') as f:
            data = json.load(f)
        # The file is a dict: {"scores": {"logo1.png|logo2.png": score, ...}}
        similarities = {tuple(k.split('|')): float(v) for k, v in data["scores"].items()}
        return similarities 