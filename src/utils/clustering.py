import numpy as np
from scipy.cluster.vq import kmeans2, whiten
from typing import List, Tuple

def cluster_into_domains(embeddings: List[List[float]], module_count: int) -> List[int]:
    """
    Groups modules into functional domains using K-means clustering on embeddings.
    Returns a list of cluster indices corresponding to the input embeddings.
    """
    if not embeddings or module_count < 4:
        # Skip clustering for very small repositories
        return [0] * len(embeddings)

    # Dynamic k calculation: k = min(8, max(2, module_count // 3))
    k = min(8, max(2, module_count // 3))
    
    # K-means requires a numpy array
    data = np.array(embeddings)
    
    # Safety: k cannot be greater than number of points
    k = min(k, len(data))
    
    if k < 2:
        # Fallback if too few distinct clusters possible
        return [0] * len(embeddings)
    
    try:
        # Whiten data to normalize variance across dimensions
        whitened_data = whiten(data)
        
        # Perform K-means with k clusters
        # iter=10 for stability; we use a fixed seed for numpy to encourage determinism
        np.random.seed(42)
        centroids, labels = kmeans2(whitened_data, k, iter=20, minit='points')
        
        return labels.tolist()
    except Exception:
        # Fallback if clustering fails (e.g., singular matrix)
        return [0] * len(embeddings)
