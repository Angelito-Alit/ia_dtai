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
                    "response": "Parece que no escribiste nada. ¿En qué te puedo ayudar?",
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
                response = f"No pude generar la consulta para tu pregunta. Intenta reformularla."
                self.update_context(user_id, message, 'consulta_fallida', response)
                
                return {
                    "success": False,
                    "response": response,
                    "intent": "consulta_fallida",
                    "has_data": False
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
            error_response = "Lo siento, tuve un problema procesando tu mensaje. ¿Puedes intentar de nuevo?"
            
            return {
                "success": False,
                "response": error_response,
                "intent": "error_sistema",
                "error": str(e),
                "has_data": False
            }
    
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
            'afirmacion', 'negacion', 'conversacion_general'
        ]
        return intent in conversational_intents
    
    def get_available_commands(self, role: str) -> Dict[str, List[str]]:
        commands = {
            'alumno': [
                "¿Cuáles son mis calificaciones?",
                "¿Cuál es mi horario?",
                "¿Cómo van mis materias?",
                "¿Cuál es mi promedio?",
                "Hola, ¿cómo estás?"
            ],
            'profesor': [
                "¿Qué alumnos están en riesgo?",
                "¿Cuáles son las estadísticas generales?",
                "¿Qué grupos hay activos?",
                "¿Cuáles son las materias más reprobadas?",
                "¿Cuántas solicitudes de ayuda hay?"
            ],
            'directivo': [
                "¿Cuáles son las estadísticas generales?",
                "¿Qué alumnos están en riesgo?",
                "¿Cómo va el rendimiento por carreras?",
                "¿Qué materias tienen más reprobación?",
                "¿Cuántos grupos hay activos?",
                "¿Cuántas solicitudes pendientes hay?"
            ]
        }
        
        return {
            "commands": commands.get(role, commands['alumno']),
            "role": role,
            "total_commands": len(commands.get(role, []))
        }
    
    def analyze_query_complexity(self, message: str) -> Dict[str, Any]:
        complexity_indicators = {
            'simple': ['que', 'cual', 'cuanto', 'quien'],
            'medium': ['como', 'donde', 'cuando', 'por que'],
            'complex': ['analizar', 'comparar', 'evaluar', 'generar reporte']
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
                'complex': '3-10 segundos'
            }.get(complexity, '< 1 segundo')
        }
    
    def validate_user_permissions(self, role: str, intent: str) -> Tuple[bool, str]:
        role_permissions = {
            'alumno': [
                'calificaciones', 'horarios', 'conversacion_general',
                'saludo', 'despedida', 'agradecimiento'
            ],
            'profesor': [
                'alumnos_riesgo', 'grupos', 'estadisticas_generales',
                'materias_reprobadas', 'calificaciones', 'horarios'
            ],
            'directivo': [
                'estadisticas_generales', 'alumnos_riesgo', 'promedio_carreras',
                'materias_reprobadas', 'solicitudes_ayuda', 'grupos'
            ]
        }
        
        allowed_intents = role_permissions.get(role, role_permissions['alumno'])
        
        if intent in allowed_intents or intent.startswith('conversacion') or intent.startswith('emocional'):
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
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "system_status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }