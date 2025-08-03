# utils/intent_classifier.py
import re
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class IntentClassifier:
    def __init__(self):
        self.intent_patterns = {
            'estadisticas_generales': {
                'keywords': [
                    'estadisticas', 'estadistica', 'general', 'resumen', 'datos', 'numeros', 
                    'cuantos hay', 'total', 'cantidad', 'informacion general',
                    'cuantos alumnos', 'cuantos profesores', 'cuantos estudiantes',
                    'cuantos grupos', 'resumen del sistema'
                ],
                'priority': 8
            },
            'alumnos_bajo_rendimiento': {
                'keywords': [
                    'alumnos bajo rendimiento', 'peores calificaciones', 'matriculas bajas',
                    'estudiantes con problemas', 'alumnos reprobando', 'bajo promedio',
                    'calificaciones mas bajas', 'estudiantes en riesgo', 'reprobar'
                ],
                'priority': 9
            },
            'alumnos_riesgo': {
                'keywords': [
                    'riesgo', 'problema', 'dificultad', 'critico', 'alto riesgo', 'alumnos problemas',
                    'estudiantes riesgo', 'matriculas riesgo', 'problemas academicos',
                    'reportes riesgo', 'seguimiento'
                ],
                'priority': 8
            },
            'ubicacion_grupos': {
                'keywords': [
                    'donde esta el grupo', 'ubicacion grupo', 'aula del grupo', 'salon',
                    'donde tienen clase', 'que aula', 'ubicacion', 'donde se encuentra'
                ],
                'priority': 8
            },
            'horarios_grupos': {
                'keywords': [
                    'horario del grupo', 'que hora tiene clase', 'cuando tiene clase',
                    'horarios de grupos', 'a que hora', 'schedule grupo', 'clases grupo'
                ],
                'priority': 8
            },
            'grupos_detalle': {
                'keywords': [
                    'grupos', 'que grupos hay', 'lista grupos', 'grupos activos',
                    'informacion grupos', 'detalles grupos', 'cuantos grupos'
                ],
                'priority': 8
            },
            'carreras_rendimiento': {
                'keywords': [
                    'rendimiento por carrera', 'carreras', 'promedio carreras',
                    'cual carrera va mejor', 'carreras problematicas', 'comparar carreras'
                ],
                'priority': 8
            },
            'profesores_carga': {
                'keywords': [
                    'carga profesores', 'que profesor tiene mas grupos', 'profesores sobrecargados',
                    'distribucion profesores', 'profesor con mas clases', 'workload profesores'
                ],
                'priority': 7
            },
            'materias_criticas': {
                'keywords': [
                    'materias mas reprobadas', 'asignaturas problematicas', 'materias dificiles',
                    'mayor reprobacion', 'materias criticas', 'asignaturas con problemas'
                ],
                'priority': 8
            },
            'solicitudes_urgentes': {
                'keywords': [
                    'solicitudes urgentes', 'ayuda pendiente', 'solicitudes criticas',
                    'peticiones sin atender', 'solicitudes de emergencia'
                ],
                'priority': 8
            },
            'capacidad_grupos': {
                'keywords': [
                    'grupos llenos', 'capacidad grupos', 'grupos saturados',
                    'cuantos alumnos por grupo', 'ocupacion grupos'
                ],
                'priority': 7
            },
            'matriculas_especificas': {
                'keywords': [
                    'matricula', 'matriculas', 'alumno especifico', 'estudiante numero',
                    'buscar alumno', 'datos de matricula'
                ],
                'priority': 8
            },
            'analisis_temporal': {
                'keywords': [
                    'tendencia', 'evolucion', 'comparar periodos', 'historico',
                    'mejora', 'empeoramiento', 'progreso'
                ],
                'priority': 7
            },
            'saludo': {
                'keywords': [
                    'hola', 'hello', 'hi', 'buenos dias', 'buenas tardes', 'buenas noches', 
                    'que tal', 'saludos', 'hey'
                ],
                'priority': 10
            },
            'despedida': {
                'keywords': [
                    'adios', 'bye', 'hasta luego', 'nos vemos', 'chao', 'gracias adios'
                ],
                'priority': 10
            },
            'agradecimiento': {
                'keywords': [
                    'gracias', 'thank you', 'te lo agradezco', 'muchas gracias',
                    'gracias por la info', 'perfecto gracias'
                ],
                'priority': 10
            },
            'pregunta_estado': {
                'keywords': [
                    'como estas', 'que tal estas', 'como te encuentras', 'how are you',
                    'como andas', 'todo bien'
                ],
                'priority': 9
            },
            'pregunta_identidad': {
                'keywords': [
                    'quien eres', 'que eres', 'who are you', 'que puedes hacer', 
                    'como funcionas', 'que sabes hacer', 'en que me ayudas'
                ],
                'priority': 9
            },
            'alumnos_por_carrera_cuatrimestre': {
                'keywords': [
                    'cuantos alumnos por carrera', 'alumnos por cuatrimestre', 'distribucion alumnos',
                    'alumnos por carrera y cuatrimestre', 'cantidad alumnos carrera',
                    'estadisticas por carrera', 'conteo alumnos', 'alumnos activos por carrera',
                    'cuantos estudiantes por carrera', 'distribucion estudiantes'
                ],
                'priority': 8
            },
            'alumnos_inactivos': {
                'keywords': [
                    'alumnos inactivos', 'estudiantes inactivos', 'alumnos no activos',
                    'listado inactivos', 'alumnos dados de baja', 'estudiantes dados de baja',
                    'alumnos que no estan activos', 'estado inactivo', 'no activos'
                ],
                'priority': 8
            },
            
            'alumnos_altas_calificaciones': {
                'keywords': [
                    'alumnos SA', 'alumnos DE', 'alumnos AU', 'calificacion 8', 'calificacion 9', 'calificacion 10',
                    'satisfactorio', 'destacado', 'autonomo', 'altas calificaciones', 'mejores calificaciones',
                    'excelentes calificaciones', 'ultimo ciclo', 'calificaciones sobresalientes',
                    'estudiantes destacados', 'rendimiento sobresaliente'
                ],
                'priority': 8
            },
            'alumnos_riesgo_academico': {
                'keywords': [
                    'alumnos riesgo academico', 'estudiantes riesgo academico', 'riesgo academico',
                    'alumnos problemas academicos', 'estudiantes problemas academicos',
                    'reportes riesgo academico', 'riesgo escolar', 'alumnos en riesgo',
                    'estudiantes en riesgo', 'problemas rendimiento', 'bajo rendimiento academico'
                ],
                'priority': 9
            },
            
            
            
            
            
            
            
            
        }
        
        self.directivo_question_indicators = [
            'cuanto', 'cuanta', 'cuantos', 'cuantas',
            'que', 'cual', 'cuales', 'quien', 'quienes',
            'como', 'donde', 'cuando', 'por que', 'porque',
            'dame', 'muestrame', 'necesito', 'quiero',
            'dime', 'explicame', 'cuentame', 'reporta',
            'lista', 'identifica', 'encuentra'
        ]
    
    def classify_intent(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        if not message or not message.strip():
            return 'mensaje_vacio'
        
        message_clean = self._clean_message(message)
        message_lower = message_clean.lower()
        
        if self._is_matricula_query(message):
            return 'matriculas_especificas'
        
        best_intent = None
        highest_score = 0
        
        for intent, pattern_data in self.intent_patterns.items():
            score = self._calculate_intent_score(message_lower, pattern_data)
            if score > highest_score:
                highest_score = score
                best_intent = intent
        
        if highest_score >= 0.3:
            return best_intent
        
        if self._is_directivo_question(message_lower):
            return self._classify_directivo_question_type(message_lower)
        
        if context and context.get('last_intent'):
            context_intent = self._check_context_continuation(message_lower, context)
            if context_intent:
                return context_intent
        
        return 'consulta_general_directivo'
    
    def _is_directivo_question(self, message: str) -> bool:
        return any(indicator in message for indicator in self.directivo_question_indicators)
    
    def _classify_directivo_question_type(self, message: str) -> str:
        directivo_patterns = {
            'estadisticas_generales': ['cuantos alumnos', 'cuantos profesores', 'cuantos grupos', 'cantidad total'],
            'ubicacion_grupos': ['donde esta', 'que aula', 'ubicacion', 'salon'],
            'horarios_grupos': ['que hora', 'cuando tiene', 'horario'],
            'alumnos_bajo_rendimiento': ['peores', 'mas bajas', 'bajo rendimiento', 'reprobando'],
            'materias_criticas': ['mas reprobadas', 'problematicas', 'dificiles'],
            'capacidad_grupos': ['cuantos por grupo', 'llenos', 'capacidad'],
            'carreras_rendimiento': ['rendimiento carrera', 'mejor carrera', 'promedio carrera'],
            'profesores_carga': ['carga profesor', 'mas grupos', 'sobrecargado']
        }
        
        for intent, patterns in directivo_patterns.items():
            if any(pattern in message for pattern in patterns):
                return intent
        
        return 'estadisticas_generales'
    
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
        
        exact_match_bonus = 0
        for keyword in keywords:
            if keyword == message.strip():
                exact_match_bonus = 0.5
                break
        
        final_score = (keyword_score * priority_multiplier) + length_bonus + exact_match_bonus
        return min(final_score, 1.0)
    
    def _check_context_continuation(self, message: str, context: Dict[str, Any]) -> Optional[str]:
        last_intent = context.get('last_intent')
        
        continuation_words = ['mas', 'otro', 'tambien', 'ademas', 'siguiente', 'detalles']
        if any(word in message for word in continuation_words):
            if last_intent and last_intent != 'consulta_general_directivo':
                return f"mas_{last_intent}"
        
        if any(word in message for word in ['si', 'claro', 'ok', 'correcto', 'exacto']):
            return 'afirmacion'
        
        if any(word in message for word in ['no', 'nada', 'mejor no']):
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