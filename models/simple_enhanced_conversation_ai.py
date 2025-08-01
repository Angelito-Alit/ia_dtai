from datetime import datetime
import random
from database.connection import DatabaseConnection
from utils.enhanced_intent_classifier import EnhancedIntentClassifier
from models.fixed_query_generator import FixedQueryGenerator
from models.response_formatter import ResponseFormatter

class SimpleEnhancedConversationAI:
    def __init__(self):
        self.db = DatabaseConnection()
        self.classifier = EnhancedIntentClassifier()
        self.query_gen = FixedQueryGenerator()
        self.formatter = ResponseFormatter()
        self.contexts = {}
    
    def get_user_context(self, user_id):
        if user_id not in self.contexts:
            self.contexts[user_id] = {
                'messages': [],
                'last_intent': None,
                'pending_data': None,
                'conversation_state': 'ready'
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
        
        if context['conversation_state'] == 'waiting_data':
            return self._handle_pending_data(message, context, role, user_id)
        
        classification = self.classifier.classify_and_extract(message)
        
        if not classification:
            return self._handle_simple_conversation(message, context, role, user_id)
        
        if classification['missing_data']['missing_fields']:
            return self._request_missing_data(classification, context, user_id)
        
        return self._execute_complex_query(classification, context, role, user_id)
    
    def _handle_pending_data(self, message, context, role, user_id):
        pending = context['pending_data']
        missing_fields = pending['missing_fields']
        
        if missing_fields:
            field = missing_fields[0]
            pending['extracted_data'][field] = message.strip()
            missing_fields.pop(0)
            
            if missing_fields:
                next_field = missing_fields[0]
                prompt = self.classifier.get_question_prompt(next_field)
                return {
                    'response': prompt,
                    'intent': 'data_collection',
                    'conversational': True,
                    'context_messages': len(context['messages']),
                    'role': role
                }
            else:
                context['conversation_state'] = 'ready'
                classification = {
                    'intent': pending['intent'],
                    'query_type': pending['query_type'],
                    'requires': pending['requires'],
                    'missing_data': {
                        'missing_fields': [],
                        'extracted_data': pending['extracted_data']
                    }
                }
                return self._execute_complex_query(classification, context, role, user_id)
        
        return self._handle_simple_conversation(message, context, role, user_id)
    
    def _request_missing_data(self, classification, context, user_id):
        missing_fields = classification['missing_data']['missing_fields'][:]
        first_field = missing_fields[0]
        
        context['pending_data'] = {
            'intent': classification['intent'],
            'query_type': classification['query_type'],
            'requires': classification['requires'],
            'missing_fields': missing_fields,
            'extracted_data': classification['missing_data']['extracted_data']
        }
        context['conversation_state'] = 'waiting_data'
        
        prompt = self.classifier.get_question_prompt(first_field)
        
        return {
            'response': prompt,
            'intent': 'data_collection',
            'conversational': True,
            'context_messages': len(context['messages']),
            'waiting_for': first_field
        }
    
    def _execute_complex_query(self, classification, context, role, user_id):
        extracted_data = classification['missing_data']['extracted_data']
        
        params = self.query_gen.format_parameters(extracted_data, classification['missing_data'])
        query, formatted_params = self.query_gen.generate_query(classification['query_type'], params)
        
        if not query:
            return {
                'response': 'No pude generar la consulta para tu pregunta. Intenta reformularla.',
                'intent': classification['intent'],
                'error': 'query_generation_failed'
            }
        
        try:
            data = self.db.execute_query(query, formatted_params)
            
            if data:
                response = self._format_response(data, classification['intent'], extracted_data)
            else:
                response = f'No se encontraron resultados para tu consulta sobre {classification["intent"].replace("_", " ")}.'
            
            self.update_context(user_id, f"Consulta sobre {classification['intent']}", classification['intent'], response)
            
            return {
                'response': response,
                'intent': classification['intent'],
                'query_type': classification['query_type'],
                'results_count': len(data) if data else 0,
                'conversational': True,
                'context_messages': len(context['messages']),
                'role': role
            }
            
        except Exception as e:
            return {
                'response': 'Hubo un error al procesar tu consulta. Por favor intenta de nuevo.',
                'intent': classification['intent'],
                'error': str(e)
            }
    
    def _format_response(self, data, intent, extracted_data):
        if not data:
            return "No se encontraron resultados para tu consulta."
        
        # Respuestas simples para conteos
        if len(data) == 1 and len(data[0]) == 1:
            result = data[0]
            key = list(result.keys())[0]
            value = result[key]
            return f"**Resultado:** {value}"
        
        # Respuestas para consultas específicas conocidas
        if intent == 'grupos_generales':
            response = "**Grupos Activos:**\n\n"
            for i, group in enumerate(data[:15], 1):
                response += f"{i}. {group.get('grupo', 'N/A')} - {group.get('asignatura', 'N/A')}\n"
                if group.get('total_alumnos'):
                    response += f"   Alumnos: {group['total_alumnos']}\n"
                response += "\n"
            if len(data) > 15:
                response += f"... y {len(data) - 15} mas.\n"
            return response
        
        # Formato genérico para otras consultas
        response = f"**Resultados ({len(data)}):**\n\n"
        for i, row in enumerate(data[:10], 1):
            response += f"{i}. "
            values = []
            for key, value in row.items():
                if value is not None:
                    if isinstance(value, (int, float)) and key != 'id':
                        values.append(f"{key}: {value}")
                    elif isinstance(value, str) and len(value) < 50:
                        values.append(f"{value}")
            
            response += " | ".join(values[:3])
            response += "\n"
        
        if len(data) > 10:
            response += f"\n... y {len(data) - 10} resultados mas."
        
        return response
    
    def _handle_simple_conversation(self, message, context, role, user_id):
        from utils.intent_classifier import IntentClassifier
        simple_classifier = IntentClassifier()
        intent = simple_classifier.classify(message, context)
        
        if intent in ['saludo', 'despedida', 'agradecimiento', 'pregunta_estado', 'pregunta_identidad']:
            response = self._get_simple_response(intent, message)
        else:
            response = f"Entiendo que me preguntas sobre '{message}'. Puedo ayudarte con consultas especificas. Ejemplos: 'que grupos hay', 'cuantos alumnos hay', 'cual es el promedio del alumno Juan Perez'."
        
        self.update_context(user_id, message, intent, response)
        
        return {
            'response': response,
            'intent': intent,
            'conversational': True,
            'context_messages': len(context['messages']),
            'role': role
        }
    
    def _get_simple_response(self, intent, message):
        responses = {
            'saludo': [
                "Hola! Soy tu asistente academico inteligente. Puedo ayudarte con consultas especificas.",
                "Buenos dias! En que consulta especifica puedo ayudarte hoy?",
                "Hola! Estoy aqui para ayudarte con informacion del sistema academico.",
            ],
            'pregunta_estado': [
                "Estoy funcionando perfectamente! Puedo procesar consultas complejas.",
                "Muy bien, gracias! Listo para ayudarte con cualquier consulta.",
            ],
            'pregunta_identidad': [
                "Soy un asistente de IA especializado en consultas academicas. Puedo responder preguntas sobre alumnos, profesores, calificaciones, reportes y mas.",
                "Soy tu asistente academico inteligente. Puedo procesar consultas complejas del sistema educativo.",
            ],
            'agradecimiento': [
                "De nada! Estoy aqui para ayudarte con cualquier consulta academica.",
                "Un placer ayudarte! Si tienes mas preguntas, no dudes en preguntarme.",
            ],
            'despedida': [
                "Hasta luego! Recuerda que puedo ayudarte con consultas academicas cuando regreses.",
                "Nos vemos! Siempre estare aqui para tus consultas.",
            ]
        }
        
        return random.choice(responses.get(intent, ["Entiendo. En que mas puedo ayudarte?"]))