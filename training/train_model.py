import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import logging
from training.training_data import get_all_training_data, validate_training_data
from utils.text_processor import TextProcessor

logger = logging.getLogger(__name__)

class AIModelTrainer:
    def __init__(self):
        self.processor = TextProcessor()
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            stop_words=None,
            lowercase=True
        )
        self.model = MultinomialNB(alpha=1.0)
        self.is_trained = False
    
    def prepare_data(self):
        training_data = get_all_training_data()
        validation_info = validate_training_data()
        
        logger.info(f"Training data validation: {validation_info}")
        
        if validation_info['total_examples'] < 50:
            logger.warning("Insufficient training data. Minimum 50 examples recommended.")
        
        texts = []
        labels = []
        
        for text, label in training_data:
            processed_text = self.processor.clean_text(text)
            texts.append(processed_text)
            labels.append(label)
        
        return texts, labels
    
    def train_model(self, test_size=0.2, validation=True):
        logger.info("Starting model training...")
        
        texts, labels = self.prepare_data()
        
        if len(set(labels)) < 2:
            logger.error("Need at least 2 different intents to train")
            return False
        
        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels, test_size=test_size, random_state=42, stratify=labels
        )
        
        X_train_vectorized = self.vectorizer.fit_transform(X_train)
        X_test_vectorized = self.vectorizer.transform(X_test)
        
        self.model.fit(X_train_vectorized, y_train)
        
        if validation:
            self._validate_model(X_test_vectorized, y_test)
        
        self.is_trained = True
        logger.info("Model training completed successfully")
        return True
    
    def _validate_model(self, X_test, y_test):
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"Model accuracy: {accuracy:.3f}")
        logger.info(f"Classification report:\n{classification_report(y_test, y_pred)}")
        
        return accuracy
    
    def predict_intent(self, text, confidence_threshold=0.6):
        if not self.is_trained:
            logger.warning("Model not trained. Using fallback classification.")
            return 'conversacion_general', 0.5
        
        processed_text = self.processor.clean_text(text)
        vectorized = self.vectorizer.transform([processed_text])
        
        prediction = self.model.predict(vectorized)[0]
        probabilities = self.model.predict_proba(vectorized)[0]
        confidence = max(probabilities)
        
        if confidence < confidence_threshold:
            return 'conversacion_general', confidence
        
        return prediction, confidence
    
    def get_feature_importance(self, intent, top_n=10):
        if not self.is_trained:
            return []
        
        feature_names = self.vectorizer.get_feature_names_out()
        class_idx = list(self.model.classes_).index(intent)
        feature_weights = self.model.feature_log_prob_[class_idx]
        
        top_indices = np.argsort(feature_weights)[-top_n:]
        top_features = [(feature_names[i], feature_weights[i]) for i in top_indices]
        
        return sorted(top_features, key=lambda x: x[1], reverse=True)
    
    def save_model(self, filepath_base='model'):
        if not self.is_trained:
            logger.error("Cannot save untrained model")
            return False
        
        try:
            joblib.dump(self.model, f'{filepath_base}_classifier.pkl')
            joblib.dump(self.vectorizer, f'{filepath_base}_vectorizer.pkl')
            logger.info(f"Model saved to {filepath_base}_*.pkl")
            return True
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            return False
    
    def load_model(self, filepath_base='model'):
        try:
            self.model = joblib.load(f'{filepath_base}_classifier.pkl')
            self.vectorizer = joblib.load(f'{filepath_base}_vectorizer.pkl')
            self.is_trained = True
            logger.info(f"Model loaded from {filepath_base}_*.pkl")
            return True
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    def cross_validate(self, cv_folds=5):
        texts, labels = self.prepare_data()
        X_vectorized = self.vectorizer.fit_transform(texts)
        
        scores = cross_val_score(self.model, X_vectorized, labels, cv=cv_folds)
        
        logger.info(f"Cross-validation scores: {scores}")
        logger.info(f"Average CV score: {scores.mean():.3f} (+/- {scores.std() * 2:.3f})")
        
        return scores.mean(), scores.std()