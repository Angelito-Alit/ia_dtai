from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

from utils.intent_classifier import IntentClassifier
from models.query_generator import QueryGenerator
from models.response_formatter import ResponseFormatter
from database.connection import DatabaseConnection

logger = logging.getLogger(__name__)

class ConversationAI:
    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.query_generator = QueryGenerator()
        self.response_formatter = ResponseFormatter()
        self.db = DatabaseConnection()
        self.conversation_contexts = {}
    
    def process_message(self, message: str, user_id: int = 1, role: str = 'alumno') -> Dict[str, Any]:
        try:
            if not message or not message.strip():
                return {
                    "success": True,
                    "response": "Parece que no escribiste nada. ¿En qué te puedo ayudar? Puedo darte información sobre estadísticas del sistema, alumnos, carreras, grupos, calificaciones y mucho más.",
                    "intent": "mensaje_vacio",
                    "has_data": False
                }
            
            context = self.get_conversation_context(user_id)
            intent = self.intent_classifier.classify_intent(message, context)
            
            logger.info(f"Usuario {user_id} ({role}): {message[:50]}... -> Intent: {intent}")
            
            if self._is_conversational_intent(intent):
                response = self.response_formatter.format_response(intent, None, message, role)
                self.update_context(user_id, message, intent, response)
                
                return {
                    "success": True,
                    "response": response,
                    "intent": intent,
                    "has_data": False,
                    "conversational": True
                }
            
            query, params = self.query_generator.generate_query(message, intent, user_id, role)
            
            if not query:
                suggested_response = self._generate_helpful_suggestion(message, intent, role)
                self.update_context(user_id, message, 'consulta_sugerencia', suggested_response)
                
                return {
                    "success": True,
                    "response": suggested_response,
                    "intent": "consulta_sugerencia",
                    "has_data": False,
                    "helpful_suggestion": True
                }
            
            data = self.db.execute_query(query, params)
            response = self.response_formatter.format_response(intent, data, message, role)
            response = self.response_formatter.add_suggestions(response, intent, role)
            
            self.update_context(user_id, message, intent, response)
            
            return {
                "success": True,
                "response": response,
                "intent": intent,
                "has_data": bool(data),
                "data_count": len(data) if data else 0,
                "query_executed": True
            }
            
        except Exception as e:
            logger.error(f"Error procesando mensaje: {e}")
            error_response = "Lo siento, tuve un problema procesando tu mensaje. ¿Puedes intentar reformulándolo? Por ejemplo: '¿Cuántos alumnos hay?', '¿Qué carreras están disponibles?', o '¿Cuáles son las estadísticas generales?'"
            
            return {
                "success": False,
                "response": error_response,
                "intent": "error_sistema",
                "error": str(e),
                "has_data": False
            }
    
    def _generate_helpful_suggestion(self, message: str, intent: str, role: str) -> str:
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['hola', 'hi', 'hello', 'buenas']):
            return "¡Buenos días! Soy su asistente administrativo de DTAI. Tengo acceso completo al sistema para proporcionarle información sobre: alumnos en riesgo, matrículas específicas, ubicación de grupos, horarios, cargas de profesores, materias problemáticas, solicitudes urgentes y estadísticas completas. ¿Qué información necesita para la gestión académica?"
        
        if any(word in message_lower for word in ['ayuda', 'help', 'que puedes hacer']):
            return """Como directivo, tiene acceso completo a:

🚨 **Gestión de Riesgo** - "¿Qué alumnos están en riesgo crítico?"
📊 **Análisis Académico** - "¿Cuáles son las materias más reprobadas?"
📍 **Ubicaciones** - "¿Dónde está el grupo de Ing. Software 3er cuatri?"
📅 **Horarios** - "¿A qué hora tiene clases el grupo ISW-301?"
👥 **Capacidad** - "¿Qué grupos están llenos?"
👨‍🏫 **Profesores** - "¿Qué profesores están sobrecargados?"
🎓 **Carreras** - "¿Cómo va el rendimiento por carreras?"
🔍 **Estudiantes** - "Información de matrícula 202412345"
📋 **Solicitudes** - "¿Qué solicitudes urgentes hay?"

Pregúnteme cualquier cosa para la toma de decisiones administrativas."""
        
        directivo_suggestions = {
            'alumnos': "Como directivo, puede consultar: '¿Qué alumnos tienen las calificaciones más bajas?', '¿Cuáles son las matrículas en riesgo?', o buscar por matrícula específica.",
            'profesores': "Información disponible: '¿Qué profesores tienen más carga?', '¿Quiénes están sobrecargados?', '¿Cómo está distribuida la carga académica?'",
            'grupos': "Consultas de grupos: '¿Dónde está ubicado el grupo X?', '¿Qué grupos están llenos?', '¿Cuáles son los horarios de los grupos?'",
            'materias': "Análisis de materias: '¿Cuáles son las materias más reprobadas?', '¿Qué asignaturas son problemáticas?', '¿Dónde necesitamos refuerzo académico?'",
            'carreras': "Rendimiento por carreras: '¿Cómo va cada carrera?', '¿Cuál tiene mejor rendimiento?', '¿Dónde hay más problemas académicos?'",
            'estadisticas': "Estadísticas completas: '¿Cuántos alumnos, profesores y grupos hay?', '¿Cuáles son los números generales?', '¿Qué datos críticos hay?'",
            'riesgo': "Gestión de riesgo: '¿Qué alumnos están en situación crítica?', '¿Cuántos reportes de riesgo hay?', '¿Qué casos requieren atención inmediata?'",
            'solicitudes': "Solicitudes administrativas: '¿Qué solicitudes están pendientes?', '¿Cuáles son urgentes?', '¿Qué casos necesitan atención?'"
        }
        
        for keyword, suggestion in directivo_suggestions.items():
            if keyword in message_lower:
                return suggestion
        
        if len(message.split()) == 1:
            word = message_lower.strip()
            quick_responses = {
                'estadisticas': "Para estadísticas: '¿Cuáles son las estadísticas generales del sistema?'",
                'grupos': "Para grupos: '¿Qué grupos hay?' o '¿Dónde está el grupo [nombre]?'",
                'riesgo': "Para riesgo: '¿Qué alumnos están en riesgo?' o '¿Cuáles son los casos críticos?'",
                'materias': "Para materias: '¿Cuáles son las materias más reprobadas?'",
                'profesores': "Para profesores: '¿Cómo está la carga de profesores?'",
                'alumnos': "Para alumnos: '¿Quiénes tienen bajo rendimiento?' o busque por matrícula"
            }
            if word in quick_responses:
                return quick_responses[word]
        
        return f"""No identifiqué qué información específica necesita con "{message}".

Como directivo, puede consultar:
• **Ubicaciones**: "¿Dónde está el grupo [nombre]?"
• **Horarios**: "¿A qué hora tiene clases el grupo [nombre]?"
• **Rendimiento**: "¿Qué alumnos tienen bajo rendimiento?"
• **Riesgo**: "¿Qué estudiantes están en situación crítica?"
• **Materias**: "¿Cuáles son las materias más problemáticas?"
• **Profesores**: "¿Quiénes están sobrecargados?"
• **Matrícula específica**: "Información de matrícula [número]"

¿Podría ser más específico con su consulta administrativa?"""
    
    def get_conversation_context(self, user_id: int) -> Dict[str, Any]:
        if user_id not in self.conversation_contexts:
            self.conversation_contexts[user_id] = {
                'messages': [],
                'last_intent': None,
                'session_start': datetime.now()
            }
        return self.conversation_contexts[user_id]
    
    def update_context(self, user_id: int, message: str, intent: str, response: str):
        context = self.get_conversation_context(user_id)
        
        context['messages'].append({
            'user_message': message[:100],
            'bot_response': response[:100],
            'intent': intent,
            'timestamp': datetime.now()
        })
        
        context['last_intent'] = intent
        
        if len(context['messages']) > 5:
            context['messages'] = context['messages'][-5:]
    
    def clear_context(self, user_id: int) -> bool:
        if user_id in self.conversation_contexts:
            del self.conversation_contexts[user_id]
            return True
        return False
    
    def get_context_summary(self, user_id: int) -> Dict[str, Any]:
        context = self.get_conversation_context(user_id)
        
        return {
            "user_id": user_id,
            "messages_count": len(context['messages']),
            "last_intent": context['last_intent'],
            "session_duration_minutes": (datetime.now() - context['session_start']).total_seconds() / 60,
            "recent_intents": [msg['intent'] for msg in context['messages'][-3:]]
        }
    
    def _is_conversational_intent(self, intent: str) -> bool:
        conversational_intents = [
            'saludo', 'despedida', 'agradecimiento', 'pregunta_estado', 
            'pregunta_identidad', 'emocional_negativo', 'emocional_positivo',
            'afirmacion', 'negacion'
        ]
        return intent in conversational_intents
    
    def get_available_commands(self, role: str = 'directivo') -> Dict[str, Any]:
        directivo_commands = [
            "¿Cuáles son las estadísticas generales?",
            "¿Qué alumnos tienen las calificaciones más bajas?",
            "¿Qué alumnos están en riesgo crítico?",
            "¿Dónde está ubicado el grupo [nombre]?",
            "¿A qué hora tiene clases el grupo [nombre]?",
            "¿Qué grupos están llenos o cerca del límite?",
            "¿Cómo va el rendimiento por carreras?",
            "¿Qué profesores están sobrecargados?",
            "¿Cuáles son las materias más reprobadas?",
            "¿Qué solicitudes de ayuda están urgentes?",
            "Información de matrícula [número]",
            "¿Cuántos alumnos, profesores y grupos hay?"
        ]
        
        return {
            "commands": directivo_commands,
            "role": "directivo",
            "total_commands": len(directivo_commands)
        }
    
    def analyze_query_complexity(self, message: str) -> Dict[str, Any]:
        complexity_indicators = {
            'simple': ['que', 'cual', 'cuanto', 'quien', 'hola', 'gracias'],
            'medium': ['como', 'donde', 'cuando', 'por que', 'estadisticas', 'informacion'],
            'complex': ['analizar', 'comparar', 'evaluar', 'generar reporte', 'detallado', 'completo']
        }
        
        message_lower = message.lower()
        complexity = 'simple'
        indicators_found = []
        
        for level, indicators in complexity_indicators.items():
            found = [ind for ind in indicators if ind in message_lower]
            if found:
                complexity = level
                indicators_found.extend(found)
        
        return {
            "complexity": complexity,
            "indicators": indicators_found,
            "estimated_processing_time": {
                'simple': '< 1 segundo',
                'medium': '1-3 segundos', 
                'complex': '3-5 segundos'
            }.get(complexity, '< 1 segundo')
        }
    
    def validate_user_permissions(self, role: str, intent: str) -> Tuple[bool, str]:
        role_permissions = {
            'alumno': [
                'calificaciones', 'horarios', 'estadisticas_generales', 'carreras', 'grupos',
                'saludo', 'despedida', 'agradecimiento', 'pregunta_estado', 'pregunta_identidad'
            ],
            'profesor': [
                'alumnos_riesgo', 'grupos', 'estadisticas_generales', 'materias_reprobadas',
                'calificaciones', 'horarios', 'carreras', 'profesores', 'solicitudes_ayuda'
            ],
            'directivo': [
                'estadisticas_generales', 'alumnos_riesgo', 'carreras', 'materias_reprobadas', 
                'solicitudes_ayuda', 'grupos', 'profesores', 'alumnos'
            ]
        }
        
        allowed_intents = role_permissions.get(role, role_permissions['alumno'])
        
        if intent in allowed_intents or intent.startswith('conversacion') or intent.startswith('emocional') or intent == 'consulta_sugerencia':
            return True, "Acceso permitido"
        
        return False, f"No tienes permisos para realizar consultas de tipo '{intent}'"
    
    def get_system_status(self) -> Dict[str, Any]:
        try:
            db_status = self.db.test_connection()
            active_contexts = len(self.conversation_contexts)
            
            return {
                "system_status": "online",
                "database_connection": "connected" if db_status else "disconnected",
                "active_conversations": active_contexts,
                "ai_components": {
                    "intent_classifier": "ready",
                    "query_generator": "ready", 
                    "response_formatter": "ready"
                },
                "capabilities": [
                    "Conversación natural",
                    "Consultas SQL dinámicas",
                    "Múltiples roles de usuario",
                    "Contexto conversacional",
                    "Respuestas formateadas"
                ],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error en get_system_status: {e}")
            return {
                "system_status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }