"""
N-gram Model for Thirukkural Word Prediction
This module implements a bigram/trigram model to predict missing words in Thirukkural lines.
"""

from collections import defaultdict
from app import db
import time


class NGramModel:
    """
    N-gram model for predicting missing words in Thirukkural lines.
    Uses bigram (n=2) for word prediction based on context.
    """
    
    def __init__(self, n=2):
        """
        Initialize the N-gram model.
        
        Args:
            n: Order of n-gram (default: 2 for bigram)
        """
        self.n = n
        self.ngram_counts = defaultdict(lambda: defaultdict(int))
        self.vocab = set()
        self.model_trained = False
        self.total_tokens = 0
        
    def tokenize(self, text):
        """
        Tokenize Tamil text into words.
        
        Args:
            text: Input text string
            
        Returns:
            List of tokens (words)
        """
        # Split by whitespace and filter empty strings
        tokens = [word.strip() for word in text.split() if word.strip()]
        return tokens
    
    def train_from_mongodb(self):
        """
        Train the n-gram model using all kural lines from MongoDB.
        Fetches all kural data and builds n-gram counts.
        """
        if self.model_trained:
            return  # Already trained
            
        print("Training N-gram model from MongoDB...")
        start_time = time.time()
        
        # Access kural_data collection
        kural_data = db['kural_data']
        
        # Fetch all kurals
        all_kurals = kural_data.find({})
        
        # Process each kural
        for kural_doc in all_kurals:
            if 'kural' in kural_doc and len(kural_doc['kural']) >= 2:
                line1 = kural_doc['kural'][0][0] if len(kural_doc['kural'][0]) > 0 else ""
                line2 = kural_doc['kural'][1][0] if len(kural_doc['kural'][1]) > 0 else ""
                
                # Train on both lines
                if line1:
                    self._train_on_text(line1)
                if line2:
                    self._train_on_text(line2)
        
        # Mark as trained
        self.model_trained = True
        elapsed_time = time.time() - start_time
        print(f"N-gram model trained in {elapsed_time:.2f} seconds")
        print(f"Total vocabulary size: {len(self.vocab)}")
        print(f"Total tokens processed: {self.total_tokens}")
    
    def _train_on_text(self, text):
        """
        Train the model on a single text line.
        
        Args:
            text: Input text string
        """
        tokens = self.tokenize(text)
        if len(tokens) < 2:
            return  # Need at least 2 tokens for bigram
        
        # Add tokens to vocabulary
        self.vocab.update(tokens)
        self.total_tokens += len(tokens)
        
        # Build n-gram counts (bigram)
        for i in range(len(tokens) - 1):
            context = tokens[i]
            next_word = tokens[i + 1]
            self.ngram_counts[context][next_word] += 1
    
    def predict(self, context_words, masked_index):
        """
        Predict the missing word given context words and position.
        
        Args:
            context_words: List of words with one masked as None or empty
            masked_index: Index of the masked word in the list
            
        Returns:
            Predicted word (string) or None if no prediction possible
        """
        if not self.model_trained:
            self.train_from_mongodb()
        
        if not context_words or masked_index < 0 or masked_index >= len(context_words):
            return None
        
        # Get context: use previous word for bigram prediction
        if masked_index > 0:
            # Use the word before the masked position
            context = context_words[masked_index - 1]
            if context is None:
                return None
        else:
            # If first word is masked, try to use next word as context (reverse prediction)
            if masked_index < len(context_words) - 1:
                # Use next word's context (predict backwards)
                context = context_words[masked_index + 1]
                if context is None:
                    return None
                # Reverse prediction: find what word comes before context
                reverse_predictions = defaultdict(int)
                for prev_word, next_words in self.ngram_counts.items():
                    if context in next_words:
                        reverse_predictions[prev_word] = next_words[context]
                if reverse_predictions:
                    return max(reverse_predictions.items(), key=lambda x: x[1])[0]
            return None
        
        # Get predictions for this context
        if context not in self.ngram_counts:
            return None
        
        next_word_counts = self.ngram_counts[context]
        if not next_word_counts:
            return None
        
        # Return the most frequent next word
        predicted_word = max(next_word_counts.items(), key=lambda x: x[1])[0]
        return predicted_word
    
    def predict_from_line(self, line, masked_word_index):
        """
        Predict missing word(s) from a line of text with one or more masked words.
        Supports passing a single masked index (int) or a list of indices.

        Args:
            line: Text line with a masked word (represented as "_____")
            masked_word_index: Index of the masked word (0-based) or list of indices

        Returns:
            If single index passed: predicted word (string) or None
            If list passed: list of predicted words (string or None)
        """
        words = self.tokenize(line)

        # If list of indices provided, return list of predictions
        if isinstance(masked_word_index, (list, tuple)):
            predictions = []
            for idx in masked_word_index:
                if idx >= 0 and idx < len(words):
                    proc = words.copy()
                    proc[idx] = None
                    predictions.append(self.predict(proc, idx))
                else:
                    predictions.append(None)
            return predictions

        # Single index case
        if isinstance(masked_word_index, int) and masked_word_index >= 0 and masked_word_index < len(words):
            processed_words = words.copy()
            processed_words[masked_word_index] = None
            return self.predict(processed_words, masked_word_index)

        return None


# Global model instance (lazy-loaded singleton)
_model_instance = None


def get_model():
    """
    Get or create the global N-gram model instance.
    Uses singleton pattern to ensure only one model is trained.
    
    Returns:
        NGramModel instance
    """
    global _model_instance
    if _model_instance is None:
        _model_instance = NGramModel(n=2)
        _model_instance.train_from_mongodb()
    return _model_instance

