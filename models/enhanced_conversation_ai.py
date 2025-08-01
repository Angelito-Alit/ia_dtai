from datetime import datetime
import random
from database.connection import DatabaseConnection
from utils.enhanced_intent_classifier import EnhancedIntentClassifier
from models.advanced_query_generator import AdvancedQueryGenerator
from models.response_formatter import ResponseFormatter

class EnhancedConversationAI:
    def __init__(self):
        self.db = DatabaseConnection()
        self.classifier = EnhancedIntentClassifier()
        self.query_gen = AdvancedQueryGenerator()
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
                response = self._format_complex_response(data, classification['intent'], extracted_data)
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
    
    def _format_complex_response(self, data, intent, extracted_data):
        if intent == 'promedio_alumno':
            if data:
                student = data[0]
                return f"**Promedio de {student['nombre']} {student['apellido']}**\n\nMatricula: {student['matricula']}\nPromedio General: {student['promedio_general']:.2f}"
            
        elif intent == 'alumnos_cuatrimestre':
            response = f"**Alumnos en cuatrimestre {extracted_data.get('numero_cuatrimestre', 'N/A')}:**\n\n"
            for student in data[:20]:
                response += f"• {student['nombre']} {student['apellido']} - {student['matricula']}\n"
            if len(data) > 20:
                response += f"\n... y {len(data) - 20} alumnos mas."
            return response
            
        elif intent == 'alumnos_por_carrera':
            response = "**Alumnos por Carrera:**\n\n"
            for row in data:
                response += f"• **{row['carrera']}**: {row['total_alumnos']} alumnos\n"
            return response
            
        elif intent == 'asignaturas_alumno':
            alumno_name = list(extracted_data.values())[0] if extracted_data else 'el alumno'
            response = f"**Asignaturas de {alumno_name}:**\n\n"
            for subject in data:
                status_emoji = "✅" if subject['estatus'] == 'aprobado' else "📝" if subject['estatus'] == 'cursando' else "❌"
                grade = f"{subject['calificacion_final']:.1f}" if subject['calificacion_final'] else 'Sin calificar'
                response += f"{status_emoji} **{subject['asignatura']}**: {grade}\n"
                
                if subject['parcial_1'] or subject['parcial_2'] or subject['parcial_3']:
                    parciales = []
                    if subject['parcial_1']: parciales.append(f"P1: {subject['parcial_1']:.1f}")
                    if subject['parcial_2']: parciales.append(f"P2: {subject['parcial_2']:.1f}")
                    if subject['parcial_3']: parciales.append(f"P3: {subject['parcial_3']:.1f}")
                    response += f"   {' | '.join(parciales)}\n"
                response += "\n"
            return response
            
        elif intent == 'reportes_riesgo_alumno':
            alumno_name = list(extracted_data.values())[0] if extracted_data else 'el alumno'
            if not data:
                return f"**Reportes de Riesgo de {alumno_name}:**\n\nNo se encontraron reportes de riesgo para este alumno."
            
            response = f"**Reportes de Riesgo de {alumno_name}:**\n\n"
            for report in data:
                emoji = "🔴" if report['nivel_riesgo'] == 'critico' else "🟡" if report['nivel_riesgo'] == 'alto' else "🟠"
                response += f"{emoji} **{report['tipo_riesgo'].title()}** - Nivel {report['nivel_riesgo']}\n"
                response += f"   Fecha: {report['fecha_reporte']}\n"
                response += f"   Estado: {report['estado']}\n"
                if report['descripcion']:
                    response += f"   Descripcion: {report['descripcion'][:100]}...\n"
                if report['acciones_recomendadas']:
                    response += f"   Acciones: {report['acciones_recomendadas'][:100]}...\n"
                response += "\n"
            return response
            
        elif intent == 'grupos_profesor':
            profesor_name = list(extracted_data.values())[0] if extracted_data else 'el profesor'
            response = f"**Grupos asignados a {profesor_name}:**\n\n"
            for group in data:
                response += f"• **{group['grupo']}** - {group['asignatura']}\n"
                response += f"   Cuatrimestre: {group['cuatrimestre']}\n"
                response += f"   Alumnos: {group['total_alumnos']}\n"
                response += f"   Ciclo: {group['ciclo_escolar']}\n\n"
            return response
            
        elif intent == 'horarios_profesor':
            profesor_name = list(extracted_data.values())[0] if extracted_data else 'el profesor'
            response = f"**Horarios de {profesor_name}:**\n\n"
            current_day = None
            for schedule in data:
                if current_day != schedule['dia_semana']:
                    current_day = schedule['dia_semana']
                    response += f"**{current_day.title()}:**\n"
                response += f"   {schedule['hora_inicio']}-{schedule['hora_fin']} | {schedule['asignatura']} | {schedule['grupo']}"
                if schedule['aula']:
                    response += f" | Aula: {schedule['aula']}"
                response += "\n"
            return response
            
        elif intent == 'carreras_activas':
            response = "**Carreras Activas:**\n\n"
            for career in data:
                response += f"• **{career['nombre']}**\n"
                response += f"   Duracion: {career['duracion_cuatrimestres']} cuatrimestres\n"
                if career['descripcion']:
                    response += f"   Descripcion: {career['descripcion'][:80]}...\n"
                response += "\n"
            return response
            
        elif intent == 'reportes_abiertos':
            response = "**Alumnos con Reportes Abiertos:**\n\n"
            for report in data:
                emoji = "🔴" if report['nivel_riesgo'] == 'critico' else "🟡" if report['nivel_riesgo'] == 'alto' else "🟠"
                response += f"{emoji} **{report['nombre']} {report['apellido']}** ({report['matricula']})\n"
                response += f"   Riesgo: {report['nivel_riesgo']} - {report['tipo_riesgo']}\n"
                response += f"   Fecha: {report['fecha_reporte']}\n"
                if report['descripcion']:
                    response += f"   Motivo: {report['descripcion'][:60]}...\n"
                response += "\n"
            return response
            
        elif intent == 'solicitudes_pendientes':
            response = "**Solicitudes de Ayuda Pendientes:**\n\n"
            for request in data:
                urgency_emoji = "🚨" if request['nivel_urgencia'] == 'alta' else "⚠️" if request['nivel_urgencia'] == 'media' else "📋"
                response += f"{urgency_emoji} **{request['nombre']} {request['apellido']}** ({request['matricula']})\n"
                response += f"   Problema: {request['tipo_problema']}\n"
                response += f"   Urgencia: {request['nivel_urgencia']}\n"
                response += f"   Fecha: {request['fecha_solicitud']}\n\n"
            return response
            
        elif intent == 'noticias_activas':
            response = "**Noticias Activas:**\n\n"
            for news in data:
                destacada = "📌 " if hasattr(news, 'destacada') and news['destacada'] else ""
                response += f"{destacada}**{news['titulo']}**\n"
                response += f"   Autor: {news['autor_nombre']} {news['autor_apellido']}\n"
                response += f"   Fecha: {news['fecha_publicacion']}\n"
                response += f"   Vistas: {news['vistas']}\n"
                if news['contenido']:
                    response += f"   Contenido: {news['contenido'][:100]}...\n"
                response += "\n"
            return response
            
        elif intent == 'posts_mas_vistos':
            response = "**Posts Mas Vistos del Foro:**\n\n"
            for post in data:
                response += f"• **{post['titulo']}**\n"
                response += f"   Vistas: {post['vistas']}\n"
                response += f"   Comentarios: {post['total_comentarios']}\n\n"
            return response
            
        elif intent == 'encuestas_profesor':
            profesor_name = list(extracted_data.values())[0] if extracted_data else 'el profesor'
            response = f"**Encuestas creadas por {profesor_name}:**\n\n"
            for survey in data:
                status = "✅ Activa" if survey['activa'] else "❌ Inactiva"
                response += f"• **{survey['titulo']}** ({status})\n"
                response += f"   Fecha: {survey['fecha_creacion']}\n"
                if survey['descripcion']:
                    response += f"   Descripcion: {survey['descripcion'][:80]}...\n"
                response += "\n"
            return response
            
        else:
            response = f"**Resultados de la consulta:**\n\n"
            for i, row in enumerate(data[:10]):
                response += f"**Resultado {i+1}:**\n"
                for key, value in row.items():
                    if value is not None:
                        response += f"   {key.replace('_', ' ').title()}: {value}\n"
                response += "\n"
            
            if len(data) > 10:
                response += f"... y {len(data) - 10} resultados mas.\n"
            
            return response
    
    def _handle_simple_conversation(self, message, context, role, user_id):
        from utils.intent_classifier import IntentClassifier
        simple_classifier = IntentClassifier()
        intent = simple_classifier.classify(message, context)
        
        if intent in ['saludo', 'despedida', 'agradecimiento', 'pregunta_estado', 'pregunta_identidad']:
            response = self._get_simple_response(intent, message)
        else:
            response = f"Entiendo que me preguntas sobre '{message}'. Puedo ayudarte con consultas especificas sobre alumnos, profesores, calificaciones, reportes de riesgo y mas. Por ejemplo, puedes preguntar 'cual es el promedio del alumno Juan Perez' o 'que grupos tiene asignados el profesor Maria Lopez'."
        
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
                "Hola! Soy tu asistente academico inteligente. Puedo ayudarte con consultas especificas sobre alumnos, profesores, calificaciones y mas.",
                "Buenos dias! En que consulta especifica puedo ayudarte hoy?",
                "Hola! Estoy aqui para ayudarte con informacion detallada del sistema academico.",
            ],
            'pregunta_estado': [
                "Estoy funcionando perfectamente! Puedo procesar consultas complejas sobre el sistema academico.",
                "Muy bien, gracias! Listo para ayudarte con cualquier consulta especifica que tengas.",
            ],
            'pregunta_identidad': [
                "Soy un asistente de IA especializado en consultas academicas. Puedo responder preguntas especificas sobre alumnos, profesores, calificaciones, reportes de riesgo, solicitudes de ayuda, noticias, foros y encuestas.",
                "Soy tu asistente academico inteligente. Puedo procesar consultas complejas y darte informacion detallada sobre cualquier aspecto del sistema educativo.",
            ],
            'agradecimiento': [
                "De nada! Estoy aqui para ayudarte con cualquier consulta academica que necesites.",
                "Un placer ayudarte! Si tienes mas preguntas especificas, no dudes en preguntarme.",
            ],
            'despedida': [
                "Hasta luego! Recuerda que puedo ayudarte con consultas especificas sobre el sistema academico cuando regreses.",
                "Nos vemos! Siempre estare aqui para tus consultas academicas.",
            ]
        }
        
        return random.choice(responses.get(intent, ["Entiendo. En que mas puedo ayudarte?"]))