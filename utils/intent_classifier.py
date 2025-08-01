import re
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class IntentClassifier:
    def __init__(self):
        self.intent_patterns = {
            'saludo': {
                'keywords': ['hola', 'hello', 'hi', 'buenos dias', 'buenas tardes', 'buenas noches', 'que tal'],
                'priority': 10
            },
            'despedida': {
                'keywords': ['adios', 'bye', 'hasta luego', 'nos vemos', 'chao'],
                'priority': 10
            },
            'agradecimiento': {
                'keywords': ['gracias', 'thank you', 'te lo agradezco', 'muchas gracias'],
                'priority': 10
            },
            'pregunta_estado': {
                'keywords': ['como estas', 'que tal', 'como te encuentras', 'how are you'],
                'priority': 9
            },
            'pregunta_identidad': {
                'keywords': ['quien eres', 'que eres', 'who are you', 'que puedes hacer', 'como funcionas'],
                'priority': 9
            },
            'estadisticas_generales': {
                'keywords': ['estadisticas', 'general', 'resumen', 'datos', 'numeros', 'cuantos hay', 'total'],
                'priority': 8
            },
            'alumnos_riesgo': {
                'keywords': ['riesgo', 'problema', 'dificultad', 'critico', 'alto riesgo', 'alumnos problemas'],
                'priority': 8
            },
            'promedio_carreras': {
                'keywords': ['promedio', 'carrera', 'rendimiento', 'promedio carrera', 'carreras'],
                'priority': 8
            },
            'materias_reprobadas': {
                'keywords': ['reprobada', 'reprobadas', 'materias reprobadas', 'asignaturas reprobadas', 'fallas'],
                'priority': 8
            },
            'solicitudes_ayuda': {
                'keywords': ['solicitud', 'ayuda', 'pendiente', 'atencion', 'solicitudes'],
                'priority': 8
            },
            'calificaciones': {
                'keywords': ['calificacion', 'calificaciones', 'notas', 'puntuaciones', 'resultados', 'mis notas'],
                'priority': 7
            },
            'horarios': {
                'keywords': ['horario', 'horarios', 'clase', 'clases', 'aula', 'mi horario'],
                'priority': 7
            },
            'grupos': {
                'keywords': ['grupo', 'grupos', 'que grupos', 'cuales grupos'],
                'priority': 7
            },
            'profesores': {
                'keywords': ['profesor', 'profesores', 'maestro', 'maestros', 'docente'],
                'priority': 6
            },
            'asignaturas': {
                'keywords': ['asignatura', 'asignaturas', 'materia', 'materias', 'curso'],
                'priority': 6
            },
            'emocional_negativo': {
                'keywords': ['triste', 'deprimido', 'mal', 'terrible', 'horrible', 'preocupado', 'ansioso'],
                'priority': 5
            },
            'emocional_positivo': {
                'keywords': ['feliz', 'contento', 'bien', 'genial', 'excelente', 'perfecto'],
                'priority': 5
            },
            'afirmacion': {
                'keywords': ['si', 'claro', 'ok', 'esta bien', 'perfecto', 'correcto'],
                'priority': 4
            },
            'negacion': {
                'keywords': ['no', 'nada', 'mejor no', 'no gracias'],
                'priority': 4
            }
        }
        
        self.context_patterns = {
            'continuation': ['mas', 'otro', 'tambien', 'ademas', 'siguiente'],
            'clarification': ['que significa', 'no entiendo', 'explica', 'como'],
            'specific_request': ['dame', 'muestrame', 'necesito', 'quiero ver']
        }
    
    def classify_intent(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        if not message or not message.strip():
            return 'mensaje_vacio'
        
        message_clean = self._clean_message(message)
        message_lower = message_clean.lower()
        
        if self._is_matricula_query(message):
            return 'consulta_matricula'
        
        best_intent = 'conversacion_general'
        highest_score = 0
        
        for intent, pattern_data in self.intent_patterns.items():
            score = self._calculate_intent_score(message_lower, pattern_data)
            if score > highest_score:
                highest_score = score
                best_intent = intent
        
        if context and context.get('last_intent'):
            context_intent = self._check_context_continuation(message_lower, context)
            if context_intent:
                return context_intent
        
        if highest_score < 0.3:
            return 'conversacion_general'
        
        return best_intent
    
    def _clean_message(self, message: str) -> str:
        message = re.sub(r'[¿¡]', '', message)
        message = re.sub(r'[^\w\s]', ' ', message)
        message = re.sub(r'\s+', ' ', message)
        return message.strip()
    
    def _is_matricula_query(self, message: str) -> bool:
        matricula_pattern = r'\b\d{8,12}\b'
        return bool(re.search(matricula_pattern, message))
    
    def _calculate_intent_score(self, message: str, pattern_data: Dict[str, Any]) -> float:
        keywords = pattern_data['keywords']
        priority = pattern_data.get('priority', 1)
        
        matches = 0
        total_keywords = len(keywords)
        
        for keyword in keywords:
            if keyword in message:
                matches += 1
        
        if matches == 0:
            return 0
        
        keyword_score = matches / total_keywords
        priority_multiplier = priority / 10
        
        length_bonus = 0
        if len([k for k in keywords if k in message]) > 1:
            length_bonus = 0.2
        
        final_score = (keyword_score * priority_multiplier) + length_bonus
        return min(final_score, 1.0)
    
    def _check_context_continuation(self, message: str, context: Dict[str, Any]) -> Optional[str]:
        last_intent = context.get('last_intent')
        
        if any(word in message for word in self.context_patterns['continuation']):
            if last_intent and last_intent != 'conversacion_general':
                return f"mas_{last_intent}"
        
        if any(word in message for word in ['si', 'claro', 'ok']):
            return 'afirmacion'
        
        if any(word in message for word in ['no', 'nada']):
            return 'negacion'
        
        return None
    
    def get_intent_confidence(self, message: str, intent: str) -> float:
        if intent not in self.intent_patterns:
            return 0.0
        
        message_lower = self._clean_message(message).lower()
        pattern_data = self.intent_patterns[intent]
        
        return self._calculate_intent_score(message_lower, pattern_data)
    
    def suggest_intents(self, message: str, top_n: int = 3) -> list:
        message_lower = self._clean_message(message).lower()
        intent_scores = []
        
        for intent, pattern_data in self.intent_patterns.items():
            score = self._calculate_intent_score(message_lower, pattern_data)
            if score > 0:
                intent_scores.append({
                    'intent': intent,
                    'confidence': score,
                    'keywords_matched': [k for k in pattern_data['keywords'] if k in message_lower]
                })
        
        intent_scores.sort(key=lambda x: x['confidence'], reverse=True)
        return intent_scores[:top_n]