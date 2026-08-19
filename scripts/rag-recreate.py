import sys
sys.path.insert(0, "/opt/data/lazy-packages")
from qdrant_client import QdrantClient
qc = QdrantClient(url="http://127.0.0.1:6333")
if qc.collection_exists("nura-docs"):
    info = qc.get_collection("nura-docs")
    print("existing nura-docs points:", info.points_count, "dims:", info.config.params.vectors.size)
    if info.points_count == 0 or info.config.params.vectors.size != 384:
        qc.delete_collection("nura-docs")
        qc.create_collection(collection_name="nura-docs", vectors_config={"size": 384, "distance": "Cosine"})
        print("recreated nura-docs at 384d")
    else:
        print("nura-docs already correct")
else:
    qc.create_collection(collection_name="nura-docs", vectors_config={"size": 384, "distance": "Cosine"})
    print("created nura-docs at 384d")
