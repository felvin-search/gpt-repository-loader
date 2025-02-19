from sentence_transformers import SentenceTransformer
import numpy as np

class ContentFilter:
    def __init__(self):
        # Use a lightweight model for fast inference
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.threshold = 0.3  # Adjustable threshold for relevance

    def compute_relevance(self, content, query):
        """
        Compute the relevance score between content and query using semantic similarity.
        
        Args:
            content (str): The content to evaluate
            query (str): The query or context to compare against
            
        Returns:
            float: Relevance score between 0 and 1
        """
        # Create embeddings
        content_emb = self.model.encode(content, convert_to_tensor=True)
        query_emb = self.model.encode(query, convert_to_tensor=True)
        
        # Compute cosine similarity
        similarity = np.dot(content_emb, query_emb) / (np.linalg.norm(content_emb) * np.linalg.norm(query_emb))
        return float(similarity)

    def is_relevant(self, content, query):
        """
        Determine if content is relevant to the query.
        
        Args:
            content (str): The content to evaluate
            query (str): The query or context to compare against
            
        Returns:
            bool: True if content is relevant, False otherwise
        """
        # For very short content, consider it relevant to avoid filtering out small but important files
        if len(content.strip()) < 100:
            return True
            
        score = self.compute_relevance(content, query)
        return score > self.threshold