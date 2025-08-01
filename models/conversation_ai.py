from datetime import datetime
import random
from database.connection import DatabaseConnection
from utils.intent_classifier import IntentClassifier
from models.query_generator import QueryGenerator
from models.response_formatter import ResponseFormatter

class ConversationAI:
    def __init__(self):
        self.db = DatabaseConnection()
        self.classifier = IntentClassifier()
        self.query_gen = QueryGenerator()
        self.formatter = ResponseFormatter()
        self.contexts = {}
    
    def get_user_context(self, user_id):
        if user_id not in self.contexts:
            self.contexts[user_id] = {
                'messages': [],
                'last_intent': None
            }
        return self.contexts[user_id]
    
    def update_context(self, user_id, message, intent, response):
        context = self.get_user_context(user_id)
        context['messages'].append({
            'user': message,
            'bot': response[:100],
            'intent': intent,
            'time': datetime.now()
        })
        context['last_intent'] = intent
        
        if len(context['messages']) > 5:
            context['messages'] = context['messages'][-5:]
    
    def clear_user_context(self, user_id):
        if user_id in self.contexts:
            del self.contexts[user_id]
    
    def process_message(self, message, role='alumno', user_id=1):
        context = self.get_user_context(user_id)
        intent = self.classifier.classify(message, context)
        
        if intent in ['saludo', 'despedida', 'agradecimiento', 'pregunta_estado', 'pregunta_identidad', 'emocional_positivo', 'emocional_negativo']:
            response = self._get_conversational_response(intent, message)
        else:
            response = self._get_data_response(intent, message, role, user_id)
        
        self.update_context(user_id, message, intent, response)
        
        return {
            'response': response,
            'intent': intent,
            'conversational': True,
            'context_messages': len(context['messages']),
            'role': role
        }
    
    def _get_conversational_response(self, intent, message):
        responses = {
            'saludo': [
                "Hola! Como estas? Soy tu asistente virtual academico.",
                "Buenos dias! En que te puedo ayudar hoy?",
                "Hola! Me alegra verte por aqui. Que necesitas saber?",
                "Hey! Como van las cosas? En que te puedo asistir?"
            ],
            'pregunta_estado': [
                "Muy bien, gracias por preguntar! Estoy aqui para ayudarte con tus consultas academicas.",
                "Excelente! Funcionando al 100% y listo para ayudarte. Que necesitas?",
                "Perfecto! Siempre contento de poder ayudar a estudiantes como tu. En que te apoyo?"
            ],
            'pregunta_identidad': [
                "Soy tu asistente virtual academico. Puedo ayudarte con calificaciones, reportes de riesgo, estadisticas y mas. Preguntame lo que necesites!",
                "Hola! Soy una IA especializada en educacion. Mi trabajo es ayudarte con tus consultas academicas y darte recomendaciones personalizadas.",
                "Soy tu companero digital para todo lo academico. Consulto la base de datos en tiempo real para darte informacion actualizada."
            ],
            'emocional_negativo': [
                "Lo siento mucho que te sientas asi. Recuerda que los desafios academicos son temporales y siempre hay oportunidades de mejorar. Te gustaria que revisemos tu situacion academica juntos?",
                "Entiendo que puede ser frustrante. Estoy aqui para apoyarte. Hay algo especifico que te preocupa? Podemos buscar soluciones juntos.",
                "Se que a veces puede ser abrumador. Pero recuerda que cada dificultad es una oportunidad de crecimiento. En que area necesitas mas apoyo?"
            ],
            'emocional_positivo': [
                "Me alegra mucho escuchar eso! Sigue asi! Hay algo en lo que pueda ayudarte para mantener ese buen animo?",
                "Que bueno! La actitud positiva es clave para el exito academico. Quieres revisar como van tus materias?",
                "Excelente! Me encanta ver estudiantes motivados. En que mas puedo apoyarte?"
            ],
            'agradecimiento': [
                "De nada! Para eso estoy aqui. Necesitas algo mas?",
                "Un placer ayudarte! Cualquier otra cosa que necesites, solo pregunta.",
                "Siempre es un gusto! Hay algo mas en lo que te pueda asistir?"
            ],
            'despedida': [
                "Hasta luego! Que tengas un excelente dia. Aqui estare cuando me necesites.",
                "Nos vemos! Que te vaya super bien en tus estudios!",
                "Adios! Recuerda que siempre puedes contar conmigo para tus consultas academicas."
            ]
        }
        
        return random.choice(responses.get(intent, ["Entiendo lo que me dices. En que mas puedo ayudarte?"]))
    
    def _get_data_response(self, intent, message, role, user_id):
        if intent == 'calificaciones':
            return self._get_calificaciones_response(user_id)
        elif intent == 'riesgo':
            return self._get_riesgo_response()
        elif intent == 'promedio':
            return self._get_promedio_response()
        elif intent == 'estadisticas':
            return self._get_estadisticas_response()
        else:
            return f"Interesante lo que me dices: '{message}'. Como tu asistente academico, hay algo relacionado con tus estudios en lo que te pueda ayudar?"
    
    def _get_calificaciones_response(self, user_id):
        query = """
        SELECT a.nombre, c.calificacion_final, c.estatus, c.parcial_1, c.parcial_2, c.parcial_3
        FROM calificaciones c
        JOIN asignaturas a ON c.asignatura_id = a.id
        JOIN alumnos al ON c.alumno_id = al.id
        WHERE al.usuario_id = %s
        ORDER BY a.nombre
        LIMIT 10
        """
        data = self.db.execute_query(query, [user_id])
        
        if data:
            return self.formatter.format_calificaciones(data)
        else:
            return "No encontre calificaciones registradas para ti. Es tu primer cuatrimestre? Si crees que es un error, puedes contactar a tu coordinador academico."
    
    def _get_riesgo_response(self):
        query = """
        SELECT u.nombre, u.apellido, al.matricula, rr.nivel_riesgo, rr.tipo_riesgo, rr.descripcion, car.nombre as carrera
        FROM reportes_riesgo rr
        JOIN alumnos al ON rr.alumno_id = al.id
        JOIN usuarios u ON al.usuario_id = u.id
        JOIN carreras car ON al.carrera_id = car.id
        WHERE rr.estado IN ('abierto', 'en_proceso')
        ORDER BY CASE rr.nivel_riesgo 
            WHEN 'critico' THEN 1 
            WHEN 'alto' THEN 2 
            WHEN 'medio' THEN 3 
            ELSE 4 END
        LIMIT 10
        """
        data = self.db.execute_query(query)
        
        if data:
            return self.formatter.format_riesgo(data)
        else:
            return "Excelente noticia! No hay alumnos en situacion de riesgo actualmente. El sistema educativo esta funcionando bien."
    
    def _get_promedio_response(self):
        query = """
        SELECT c.nombre as carrera, 
               COUNT(al.id) as total_alumnos,
               ROUND(AVG(al.promedio_general), 2) as promedio_carrera,
               COUNT(CASE WHEN al.promedio_general < 7.0 THEN 1 END) as alumnos_riesgo
        FROM carreras c
        LEFT JOIN alumnos al ON c.id = al.carrera_id
        WHERE al.estado_alumno = 'activo'
        GROUP BY c.id, c.nombre
        ORDER BY promedio_carrera DESC
        LIMIT 10
        """
        data = self.db.execute_query(query)
        
        if data:
            return self.formatter.format_promedio(data)
        else:
            return "No se encontraron datos de promedios por carrera."
    
    def _get_estadisticas_response(self):
        queries = [
            ("Total Alumnos Activos", "SELECT COUNT(*) as total FROM alumnos WHERE estado_alumno = 'activo'"),
            ("Total Carreras", "SELECT COUNT(*) as total FROM carreras WHERE activa = 1"),
            ("Reportes Abiertos", "SELECT COUNT(*) as total FROM reportes_riesgo WHERE estado IN ('abierto', 'en_proceso')"),
            ("Solicitudes Pendientes", "SELECT COUNT(*) as total FROM solicitudes_ayuda WHERE estado IN ('pendiente', 'en_atencion')")
        ]
        
        return self.formatter.format_estadisticas(queries, self.db)