import re
import unicodedata

class TextProcessor:
    def __init__(self):
        self.stopwords = {
            'es': ['el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 
                   'le', 'da', 'su', 'por', 'son', 'con', 'para', 'como', 'las', 'del', 'los',
                   'una', 'al', 'me', 'mi', 'tu', 'yo', 'he', 'ha', 'si', 'muy', 'mas', 'ya']
        }
    
    def clean_text(self, text):
        if not text:
            return ""
        
        text = text.lower().strip()
        text = self.remove_accents(text)
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def remove_accents(self, text):
        return ''.join(c for c in unicodedata.normalize('NFD', text)
                      if unicodedata.category(c) != 'Mn')
    
    def tokenize(self, text):
        clean = self.clean_text(text)
        tokens = clean.split()
        return [token for token in tokens if len(token) > 2 and token not in self.stopwords['es']]
    
    def extract_keywords(self, text, max_keywords=10):
        tokens = self.tokenize(text)
        word_freq = {}
        
        for token in tokens:
            word_freq[token] = word_freq.get(token, 0) + 1
        
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:max_keywords]]
    
    def similarity_score(self, text1, text2):
        tokens1 = set(self.tokenize(text1))
        tokens2 = set(self.tokenize(text2))
        
        if not tokens1 or not tokens2:
            return 0.0
        
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        
        return len(intersection) / len(union) if union else 0.0