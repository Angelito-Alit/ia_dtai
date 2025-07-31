import logging
import pickle
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Tuple
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
from training_data import TRAINING_DATA, get_all_training_data, validate_training_data
from utils.text_processor import TextProcessor

logger = logging.getLogger(__name__)

class AIModelTrainer:
    def __init__(self, model_path: str = "models/"):
        self.model_path = model_path
        self.text_processor = TextProcessor()
        self.models = {
            'naive_bayes': MultinomialNB(),
            'svm': SVC(kernel='linear', probability=True),
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42)
        }
        self.intent_classifier = None
        self.vectorizer = None
        self.label_encoder = None
        self.trained_models = {}
        self.training_metrics = {}
        self.config = {
            'test_size': 0.2,
            'random_state': 42,
            'cv_folds': 5,
            'min_samples_per_intent': 3
        }
        os.makedirs(model_path, exist_ok=True)
    
    def prepare_training_data(self) -> Tuple[List[str], List[str]]:
        logger.info("Preparando datos de entrenamiento...")
        validation_issues = validate_training_data()
        if validation_issues:
            logger.warning(f"Problemas en datos de entrenamiento: {validation_issues}")
        training_data = get_all_training_data()
        
        texts = []
        labels = []
        
        for item in training_data:
            processed_text = self.text_processor.process(item['text'])
            texts.append(processed_text)
            labels.append(item['intent'])
        intent_counts = pd.Series(labels).value_counts()
        logger.info(f"Distribución de intenciones:\n{intent_counts}")
        min_samples = self.config['min_samples_per_intent']
        valid_intents = intent_counts[intent_counts >= min_samples].index
        
        filtered_texts = []
        filtered_labels = []
        
        for text, label in zip(texts, labels):
            if label in valid_intents:
                filtered_texts.append(text)
                filtered_labels.append(label)
        
        logger.info(f"Datos preparados: {len(filtered_texts)} ejemplos, {len(valid_intents)} intenciones")
        
        return filtered_texts, filtered_labels
    
    def train_intent_classifier(self, model_type: str = 'naive_bayes') -> Dict[str, Any]:
        logger.info(f"Entrenando clasificador de intenciones con {model_type}...")
        texts, labels = self.prepare_training_data()
        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels, 
            test_size=self.config['test_size'],
            random_state=self.config['random_state'],
            stratify=labels
        )
        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=5000,
                ngram_range=(1, 2),
                stop_words=None,  
                lowercase=True,
                min_df=2,
                max_df=0.8
            )),
            ('classifier', self.models[model_type])
        ])
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        cv_scores = cross_val_score(pipeline, texts, labels, cv=self.config['cv_folds'])
        metrics = {
            'model_type': model_type,
            'accuracy': accuracy,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'unique_intents': len(set(labels)),
            'classification_report': classification_report(y_test, y_pred, output_dict=True),
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
            'feature_count': pipeline.named_steps['tfidf'].get_feature_names_out().shape[0],
            'timestamp': datetime.now().isoformat()
        }
        self.intent_classifier = pipeline
        self.training_metrics[model_type] = metrics
        
        logger.info(f"Modelo entrenado - Accuracy: {accuracy:.3f}, CV: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
        
        return metrics
    
    def train_all_models(self) -> Dict[str, Dict[str, Any]]:
        logger.info("Entrenando todos los modelos...")
        
        all_metrics = {}
        
        for model_name in self.models.keys():
            try:
                metrics = self.train_intent_classifier(model_name)
                all_metrics[model_name] = metrics
                if not self.intent_classifier or metrics['accuracy'] > max(
                    m.get('accuracy', 0) for m in all_metrics.values() if m != metrics
                ):
                    self.intent_classifier = self.trained_models.get(model_name)
                
                self.trained_models[model_name] = self.intent_classifier
                
            except Exception as e:
                logger.error(f"Error entrenando modelo {model_name}: {e}")
                all_metrics[model_name] = {'error': str(e)}
        best_model = max(all_metrics.keys(), key=lambda k: all_metrics[k].get('accuracy', 0))
        logger.info(f"Mejor modelo: {best_model} con accuracy {all_metrics[best_model]['accuracy']:.3f}")
        
        return all_metrics
    
    def augment_training_data(self, texts: List[str], labels: List[str]) -> Tuple[List[str], List[str]]:
        logger.info("Aumentando datos de entrenamiento...")
        
        augmented_texts = texts.copy()
        augmented_labels = labels.copy()
        augmentation_techniques = [
            self._add_noise,
            self._synonym_replacement,
            self._sentence_shuffle,
            self._add_punctuation_variation
        ]
        
        for i, (text, label) in enumerate(zip(texts, labels)):
            for technique in augmentation_techniques:
                if np.random.random() < 0.3:  
                    try:
                        augmented_text = technique(text)
                        if augmented_text and augmented_text != text:
                            augmented_texts.append(augmented_text)
                            augmented_labels.append(label)
                    except Exception as e:
                        logger.debug(f"Error en aumento de datos: {e}")
        
        logger.info(f"Datos aumentados: {len(texts)} → {len(augmented_texts)} ejemplos")
        
        return augmented_texts, augmented_labels
    
    def _add_noise(self, text: str) -> str:
        words = text.split()
        if len(words) > 3 and np.random.random() < 0.1:
            i, j = np.random.choice(len(words), 2, replace=False)
            words[i], words[j] = words[j], words[i]
        
        return ' '.join(words)
    
    def _synonym_replacement(self, text: str) -> str:
        synonyms = {
            'calificaciones': ['notas', 'puntuaciones', 'resultados'],
            'alumnos': ['estudiantes', 'muchachos'],
            'materias': ['asignaturas', 'clases'],
            'profesor': ['maestro', 'docente'],
            'ver': ['mostrar', 'consultar', 'revisar'],
            'como': ['de que manera', 'de que forma'],
            'problema': ['dificultad', 'inconveniente'],
            'ayuda': ['apoyo', 'asistencia']
        }
        
        words = text.split()
        for i, word in enumerate(words):
            if word.lower() in synonyms and np.random.random() < 0.2:  
                words[i] = np.random.choice(synonyms[word.lower()])
        
        return ' '.join(words)
    
    def _sentence_shuffle(self, text: str) -> str:
        sentences = text.split('.')
        if len(sentences) > 2:
            np.random.shuffle(sentences[:-1])  
            return '.'.join(sentences)
        return text
    
    def _add_punctuation_variation(self, text: str) -> str:
        variations = [
            text.replace('?', ''),
            text.replace('.', ''),
            text + '?',
            text.replace(' ', '  ')  
        ]
        
        return np.random.choice(variations)
    
    def evaluate_model_performance(self, model_name: str = None) -> Dict[str, Any]:
        if model_name and model_name in self.trained_models:
            model = self.trained_models[model_name]
        else:
            model = self.intent_classifier
        
        if not model:
            raise ValueError("No hay modelo entrenado para evaluar")
        texts, labels = self.prepare_training_data()
        predictions = model.predict(texts)
        probabilities = model.predict_proba(texts)
        intent_analysis = {}
        unique_labels = sorted(set(labels))
        
        for intent in unique_labels:
            intent_mask = np.array(labels) == intent
            intent_predictions = np.array(predictions)[intent_mask]
            intent_accuracy = (intent_predictions == intent).mean()
            intent_indices = [i for i, label in enumerate(labels) if label == intent]
            intent_confidences = [probabilities[i].max() for i in intent_indices]
            
            intent_analysis[intent] = {
                'accuracy': intent_accuracy,
                'samples': int(intent_mask.sum()),
                'avg_confidence': np.mean(intent_confidences),
                'min_confidence': np.min(intent_confidences),
                'max_confidence': np.max(intent_confidences)
            }
        error_analysis = []
        for i, (true_label, pred_label) in enumerate(zip(labels, predictions)):
            if true_label != pred_label:
                error_analysis.append({
                    'text': texts[i],
                    'true_intent': true_label,
                    'predicted_intent': pred_label,
                    'confidence': probabilities[i].max()
                })
        
        return {
            'overall_accuracy': accuracy_score(labels, predictions),
            'intent_analysis': intent_analysis,
            'error_analysis': error_analysis[:10], 
            'total_errors': len(error_analysis),
            'model_info': {
                'type': type(model).__name__,
                'features': getattr(model.named_steps.get('tfidf'), 'vocabulary_', {}).keys().__len__() if hasattr(model, 'named_steps') else 'unknown'
            }
        }
    
    def save_models(self, filename_prefix: str = "ai_model") -> Dict[str, str]:
        logger.info("Guardando modelos entrenados...")
        
        saved_files = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            if self.intent_classifier:
                model_file = f"{self.model_path}/{filename_prefix}_{timestamp}.pkl"
                with open(model_file, 'wb') as f:
                    pickle.dump(self.intent_classifier, f)
                saved_files['intent_classifier'] = model_file
                logger.info(f"Modelo principal guardado en: {model_file}")
            if self.training_metrics:
                metrics_file = f"{self.model_path}/{filename_prefix}_metrics_{timestamp}.json"
                with open(metrics_file, 'w', encoding='utf-8') as f:
                    json.dump(self.training_metrics, f, indent=2, ensure_ascii=False)
                saved_files['metrics'] = metrics_file
                logger.info(f"Métricas guardadas en: {metrics_file}")
            config_file = f"{self.model_path}/{filename_prefix}_config_{timestamp}.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'config': self.config,
                    'timestamp': timestamp,
                    'training_data_size': len(get_all_training_data()),
                    'intent_count': len(TRAINING_DATA)
                }, f, indent=2, ensure_ascii=False)
            saved_files['config'] = config_file
            metadata_file = f"{self.model_path}/latest_model.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'latest_model': saved_files.get('intent_classifier'),
                    'created': timestamp,
                    'metrics': self.training_metrics,
                    'files': saved_files
                }, f, indent=2, ensure_ascii=False)
            saved_files['metadata'] = metadata_file
            
        except Exception as e:
            logger.error(f"Error guardando modelos: {e}")
            raise
        
        return saved_files
    
    def load_model(self, model_file: str = None) -> bool:
        try:
            if not model_file:
                metadata_file = f"{self.model_path}/latest_model.json"
                if os.path.exists(metadata_file):
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                        model_file = metadata.get('latest_model')
                else:
                    pkl_files = [f for f in os.listdir(self.model_path) if f.endswith('.pkl')]
                    if pkl_files:
                        model_file = f"{self.model_path}/{sorted(pkl_files)[-1]}"
            
            if not model_file or not os.path.exists(model_file):
                logger.warning("No se encontró modelo para cargar")
                return False
            
            with open(model_file, 'rb') as f:
                self.intent_classifier = pickle.load(f)
            
            logger.info(f"Modelo cargado desde: {model_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error cargando modelo: {e}")
            return False
    
    def test_model_real_time(self, test_phrases: List[str] = None) -> Dict[str, Any]:
        if not self.intent_classifier:
            raise ValueError("No hay modelo cargado")
        
        if not test_phrases:
            test_phrases = [
                "¿Cuáles son mis calificaciones?",
                "¿Qué alumnos están en riesgo?",
                "Mostrar promedio por carrera",
                "¿Cuándo tengo clases?",
                "Necesito ayuda académica",
                "¿Cómo van las materias reprobadas?"
            ]
        
        results = []
        
        for phrase in test_phrases:
            processed = self.text_processor.process(phrase)
            prediction = self.intent_classifier.predict([processed])[0]
            probabilities = self.intent_classifier.predict_proba([processed])[0]
            top_indices = np.argsort(probabilities)[-3:][::-1]
            classes = self.intent_classifier.classes_
            
            top_predictions = [
                {
                    'intent': classes[i],
                    'confidence': float(probabilities[i])
                }
                for i in top_indices
            ]
            
            results.append({
                'original_text': phrase,
                'processed_text': processed,
                'predicted_intent': prediction,
                'confidence': float(probabilities.max()),
                'top_predictions': top_predictions
            })
        
        return {
            'test_results': results,
            'model_info': {
                'type': type(self.intent_classifier).__name__,
                'classes': list(self.intent_classifier.classes_),
                'feature_count': len(self.intent_classifier.named_steps['tfidf'].vocabulary_) if hasattr(self.intent_classifier, 'named_steps') else 'unknown'
            }
        }
    
    def generate_training_report(self) -> str:
        if not self.training_metrics:
            return "No hay métricas de entrenamiento disponibles"
        
        report = "# Reporte de Entrenamiento - IA Conversacional\n\n"
        report += f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        best_model = max(self.training_metrics.keys(), 
                        key=lambda k: self.training_metrics[k].get('accuracy', 0))
        best_accuracy = self.training_metrics[best_model]['accuracy']
        
        report += f"## Resumen General\n"
        report += f"- **Mejor modelo:** {best_model}\n"
        report += f"- **Mejor accuracy:** {best_accuracy:.3f}\n"
        report += f"- **Intenciones entrenadas:** {self.training_metrics[best_model]['unique_intents']}\n"
        report += f"- **Muestras de entrenamiento:** {self.training_metrics[best_model]['training_samples']}\n\n"
        report += "## Detalles por Modelo\n\n"
        for model_name, metrics in self.training_metrics.items():
            if 'error' in metrics:
                report += f"### {model_name} ❌\n"
                report += f"**Error:** {metrics['error']}\n\n"
                continue
            
            report += f"### {model_name}\n"
            report += f"- **Accuracy:** {metrics['accuracy']:.3f}\n"
            report += f"- **CV Score:** {metrics['cv_mean']:.3f} ± {metrics['cv_std']:.3f}\n"
            report += f"- **Features:** {metrics['feature_count']}\n"
            if 'classification_report' in metrics:
                class_report = metrics['classification_report']
                intent_scores = [(intent, scores['f1-score']) 
                               for intent, scores in class_report.items() 
                               if isinstance(scores, dict)]
                intent_scores.sort(key=lambda x: x[1], reverse=True)
                
                report += f"- **Mejores intenciones (F1-score):**\n"
                for intent, f1 in intent_scores[:5]:
                    report += f"  - {intent}: {f1:.3f}\n"
            
            report += "\n"
        report += "## Recomendaciones\n\n"
        if best_accuracy < 0.85:
            report += "- ⚠️ **Accuracy baja:** Considerar agregar más datos de entrenamiento\n"
        if best_accuracy > 0.95:
            report += "- ✅ **Excelente accuracy:** Modelo listo para producción\n"
        
        total_samples = sum(len(examples) for examples in TRAINING_DATA.values())
        if total_samples < 100:
            report += "- 📊 **Pocos datos:** Recopilar más ejemplos de conversación\n"
        
        report += "- 🔄 **Monitoreo:** Revisar rendimiento regularmente en producción\n"
        report += "- 📈 **Mejora continua:** Agregar nuevos ejemplos basados en uso real\n"
        
        return report
    
    def compare_models(self) -> pd.DataFrame:
        if not self.training_metrics:
            return pd.DataFrame()
        
        comparison_data = []
        
        for model_name, metrics in self.training_metrics.items():
            if 'error' not in metrics:
                comparison_data.append({
                    'Modelo': model_name,
                    'Accuracy': metrics['accuracy'],
                    'CV Mean': metrics['cv_mean'],
                    'CV Std': metrics['cv_std'],
                    'Features': metrics['feature_count'],
                    'Training Samples': metrics['training_samples'],
                    'Test Samples': metrics['test_samples']
                })
        
        df = pd.DataFrame(comparison_data)
        return df.sort_values('Accuracy', ascending=False)
    
    def get_feature_importance(self, top_n: int = 20) -> Dict[str, float]:
        if not self.intent_classifier or not hasattr(self.intent_classifier, 'named_steps'):
            return {}
        
        try:
            if hasattr(self.intent_classifier.named_steps['classifier'], 'coef_'):
                feature_names = self.intent_classifier.named_steps['tfidf'].get_feature_names_out()
                coef = self.intent_classifier.named_steps['classifier'].coef_
                importance = np.mean(np.abs(coef), axis=0)
                top_indices = np.argsort(importance)[-top_n:][::-1]
                
                return {
                    feature_names[i]: float(importance[i])
                    for i in top_indices
                }
            elif hasattr(self.intent_classifier.named_steps['classifier'], 'feature_importances_'):
                feature_names = self.intent_classifier.named_steps['tfidf'].get_feature_names_out()
                importance = self.intent_classifier.named_steps['classifier'].feature_importances_
                
                top_indices = np.argsort(importance)[-top_n:][::-1]
                
                return {
                    feature_names[i]: float(importance[i])
                    for i in top_indices
                }
        
        except Exception as e:
            logger.warning(f"No se pudo obtener importancia de características: {e}")
        
        return {}
def main():
    logger.info("Iniciando entrenamiento de modelos de IA...")
    trainer = AIModelTrainer()
    metrics = trainer.train_all_models()
    evaluation = trainer.evaluate_model_performance()
    real_time_test = trainer.test_model_real_time()
    saved_files = trainer.save_models()
    report = trainer.generate_training_report()
    print("\n" + "="*50)
    print("ENTRENAMIENTO COMPLETADO")
    print("="*50)
    print(f"Archivos guardados: {list(saved_files.keys())}")
    print(f"Mejor accuracy: {max(m.get('accuracy', 0) for m in metrics.values()):.3f}")
    print(f"Errores totales: {evaluation['total_errors']}")
    print("\n" + report)
    
    return trainer

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    trained_model = main()