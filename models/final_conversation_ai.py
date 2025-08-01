from datetime import datetime
import random
from database.connection import DatabaseConnection
from utils.complete_intent_classifier import CompleteIntentClassifier
from models.complete_query_generator import CompleteQueryGenerator

class FinalConversationAI:
    def __init__(self):
        self.db = DatabaseConnection()
        self.classifier = CompleteIntentClassifier()
        self.query_gen = CompleteQueryGenerator()
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
            return self._request_missing_data(classification, context, user_id, role)
        
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
    
    def _request_missing_data(self, classification, context, user_id, role):
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
            'waiting_for': first_field,
            'role': role
        }
    
    def _execute_complex_query(self, classification, context, role, user_id):
        try:
            extracted_data = classification['missing_data']['extracted_data']
            params = self.query_gen.format_parameters(extracted_data, classification['missing_data'])
            query, formatted_params = self.query_gen.generate_query(classification['query_type'], params)
            
            if not query:
                return {
                    'response': f'No tengo configurada una consulta para: {classification["intent"]}. Intenta con otra pregunta.',
                    'intent': classification['intent'],
                    'error': 'query_not_configured'
                }
            
            data = self.db.execute_query(query, formatted_params)
            
            if data:
                response = self._format_response_by_intent(data, classification['intent'], extracted_data)
            else:
                response = f'No se encontraron resultados para tu consulta.'
            
            self.update_context(user_id, f"Consulta: {classification['intent']}", classification['intent'], response)
            
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
                'response': f'Hubo un error al procesar tu consulta: {str(e)}',
                'intent': classification['intent'],
                'error': str(e)
            }
    
    def _format_response_by_intent(self, data, intent, extracted_data):
        if not data:
            return "No se encontraron resultados."
        
        # Respuestas de conteo simple
        if len(data) == 1 and len(data[0]) == 1:
            result = data[0]
            key = list(result.keys())[0]
            value = result[key]
            
            if intent == 'total_alumnos_sistema':
                return f"**Total de alumnos activos en el sistema:** {value:,}"
            elif intent == 'profesores_activos_count':
                return f"**Total de profesores activos:** {value:,}"
            elif intent == 'bajas_definitivas_count':
                return f"**Total de alumnos con baja definitiva:** {value:,}"
            elif intent == 'asignaturas_activas_count':
                return f"**Total de asignaturas activas:** {value:,}"
            elif intent == 'reportes_abiertos_count':
                return f"**Total de reportes de riesgo abiertos:** {value:,}"
            elif intent == 'solicitudes_sin_atender':
                return f"**Total de solicitudes de ayuda pendientes:** {value:,}"
            elif intent == 'alumnos_ultimo_cuatrimestre_count':
                return f"**Alumnos en su ultimo cuatrimestre:** {value:,}"
            elif intent == 'alumnos_grupo_asignado_count':
                return f"**Alumnos con grupo asignado:** {value:,}"
            elif intent == 'alumnos_mas_reporte_riesgo':
                return f"**Alumnos con multiples reportes de riesgo:** {value:,}"
            elif intent == 'clases_sabados_count':
                return f"**Clases que se imparten los sabados:** {value:,}"
            elif intent == 'reportes_resueltos_total':
                return f"**Total de reportes resueltos:** {value:,}"
            elif intent == 'reportes_sin_seguimiento_count':
                return f"**Reportes sin seguimiento:** {value:,}"
            else:
                return f"**Resultado:** {value:,}"
        
        # Respuestas específicas por tipo de consulta
        if intent == 'grupos_generales':
            response = f"**Grupos Activos ({len(data)}):**\n\n"
            for i, group in enumerate(data[:20], 1):
                response += f"{i}. **{group['grupo']}** - {group['asignatura']}\n"
                response += f"   Cuatrimestre: {group['cuatrimestre']}\n"
                response += f"   Alumnos: {group['total_alumnos']}/{group['capacidad_maxima']}\n\n"
            if len(data) > 20:
                response += f"... y {len(data) - 20} grupos mas."
            return response
        
        elif intent == 'directivos_nivel_count':
            response = "**Directivos por Nivel de Acceso:**\n\n"
            for row in data:
                response += f"• **{row['nivel_acceso'].title()}**: {row['total_directivos']} directivos\n"
            return response
        
        elif intent == 'usuarios_rol_count':
            response = "**Usuarios por Rol:**\n\n"
            for row in data:
                response += f"• **{row['rol'].title()}**: {row['total_usuarios']} usuarios\n"
            return response
        
        elif intent == 'grupos_carrera_count':
            response = "**Grupos por Carrera:**\n\n"
            for row in data:
                response += f"• **{row['carrera']}**: {row['total_grupos']} grupos\n"
            return response
        
        elif intent == 'proporcion_tutores':
            result = data[0]
            total = result['total_profesores']
            tutores = result['tutores']
            porcentaje = (tutores / total * 100) if total > 0 else 0
            response = f"**Proporcion de Profesores Tutores:**\n\n"
            response += f"• Total profesores: {total}\n"
            response += f"• Profesores tutores: {tutores}\n"
            response += f"• Porcentaje: {porcentaje:.1f}%"
            return response
        
        elif intent == 'alumnos_carrera_count':
            response = "**Alumnos por Carrera:**\n\n"
            for row in data:
                response += f"• **{row['carrera']}**: {row['total_alumnos']} alumnos\n"
            return response
        
        elif intent == 'promedio_alumno_especifico':
            if data:
                student = data[0]
                return f"**Promedio de {student['nombre']} {student['apellido']}:**\n\nMatricula: {student['matricula']}\nPromedio General: {student['promedio_general']:.2f}"
        
        elif intent == 'alumnos_cuatrimestre_x':
            cuatrimestre = list(extracted_data.values())[0] if extracted_data else 'N/A'
            response = f"**Alumnos en Cuatrimestre {cuatrimestre}:**\n\n"
            for i, student in enumerate(data, 1):
                response += f"{i}. {student['nombre']} {student['apellido']} - {student['matricula']}\n"
            return response
        
        elif intent == 'asignaturas_cursado_alumno':
            alumno_name = list(extracted_data.values())[0] if extracted_data else 'el alumno'
            response = f"**Asignaturas de {alumno_name}:**\n\n"
            for subject in data:
                status = "✅" if subject['estatus'] == 'aprobado' else "📝" if subject['estatus'] == 'cursando' else "❌"
                grade = f"{subject['calificacion_final']:.1f}" if subject['calificacion_final'] else 'Sin calificar'
                response += f"{status} **{subject['asignatura']}**: {grade}\n"
            return response
        
        elif intent == 'reportes_riesgo_recibido_alumno':
            alumno_name = list(extracted_data.values())[0] if extracted_data else 'el alumno'
            response = f"**Reportes de Riesgo de {alumno_name}:**\n\n"
            for report in data:
                emoji = "🔴" if report['nivel_riesgo'] == 'critico' else "🟡" if report['nivel_riesgo'] == 'alto' else "🟠"
                response += f"{emoji} **{report['tipo_riesgo'].title()}** - {report['nivel_riesgo']}\n"
                response += f"   Fecha: {report['fecha_reporte']}\n"
                response += f"   Estado: {report['estado']}\n\n"
            return response
        
        elif intent == 'grupos_asignados_profesor':
            profesor_name = list(extracted_data.values())[0] if extracted_data else 'el profesor'
            response = f"**Grupos de {profesor_name}:**\n\n"
            for group in data:
                response += f"• **{group['grupo']}** - {group['asignatura']}\n"
                response += f"   Cuatrimestre: {group['cuatrimestre']}\n"
                response += f"   Alumnos: {group['total_alumnos']}\n\n"
            return response
        
        elif intent == 'horarios_profesor':
            profesor_name = list(extracted_data.values())[0] if extracted_data else 'el profesor'
            response = f"**Horarios de {profesor_name}:**\n\n"
            current_day = None
            for schedule in data:
                if current_day != schedule['dia_semana']:
                    current_day = schedule['dia_semana']
                    response += f"**{current_day.title()}:**\n"
                response += f"   {schedule['hora_inicio']}-{schedule['hora_fin']} | {schedule['asignatura']} | {schedule['grupo']}\n"
            return response
        
        # Respuestas para consultas de "más" o "mejor"
        elif intent in ['alumno_promedio_mas_alto_sistema', 'carrera_mayor_asignaturas', 'asignatura_mayor_horas_practicas', 
                       'carrera_mas_profesores_asignados', 'profesor_mas_asignaturas_asignadas', 'grupo_mas_alumnos_inscritos',
                       'aula_mas_usada_semana', 'profesor_mas_reprobatorias']:
            result = data[0]
            response = f"**Resultado:**\n\n"
            for key, value in result.items():
                if key not in ['id']:
                    display_key = key.replace('_', ' ').title()
                    response += f"• **{display_key}**: {value}\n"
            return response
        
        elif intent in ['asignaturas_mayor_complejidad_5', 'profesores_mas_grupo', 'profesores_inactivos_actualmente',
                       'profesores_carrera_count', 'profesores_mas_reportes_riesgo', 'alumnos_promedio_menor_60',
                       'asignaturas_mas_extraordinaria', 'promedio_general_asignatura', 'calificacion_promedio_grupo',
                       'reportes_tipo_riesgo_count', 'alumnos_mas_reporte_critico', 'profesores_mas_5_reportes']:
            response = f"**Resultados ({len(data)}):**\n\n"
            for i, row in enumerate(data[:15], 1):
                response += f"{i}. "
                values = []
                for key, value in row.items():
                    if key not in ['id'] and value is not None:
                        if isinstance(value, (int, float)) and key != 'matricula':
                            values.append(f"{value}")
                        elif isinstance(value, str):
                            values.append(f"{value}")
                response += " | ".join(values[:3])
                response += "\n"
            
            if len(data) > 15:
                response += f"\n... y {len(data) - 15} resultados mas."
            return response
        
        # Respuesta genérica
        else:
            response = f"**Resultados ({len(data)}):**\n\n"
            for i, row in enumerate(data[:10], 1):
                response += f"{i}. "
                values = []
                for key, value in row.items():
                    if value is not None and key not in ['id']:
                        if isinstance(value, str) and len(value) < 50:
                            values.append(f"{value}")
                        elif isinstance(value, (int, float)):
                            values.append(f"{key}: {value}")
                
                response += " | ".join(values[:3])
                response += "\n"
            
            if len(data) > 10:
                response += f"\n... y {len(data) - 10} resultados mas."
            
            return response
    
    def _handle_simple_conversation(self, message, context, role, user_id):
        simple_responses = {
            'hola': 'Hola! Soy tu asistente academico. Puedo responder preguntas como "que grupos hay", "cuantos alumnos hay", etc.',
            'gracias': 'De nada! En que mas puedo ayudarte?',
            'adios': 'Hasta luego! Siempre estare aqui para tus consultas academicas.'
        }
        
        msg_lower = message.lower().strip()
        for key, response in simple_responses.items():
            if key in msg_lower:
                self.update_context(user_id, message, key, response)
                return {
                    'response': response,
                    'intent': key,
                    'conversational': True,
                    'context_messages': len(context['messages']),
                    'role': role
                }
        
        response = f'No entendi tu pregunta: "{message}". Prueba con preguntas como: "que grupos hay", "cuantos alumnos hay", "cual es el promedio del alumno Juan Perez".'
        self.update_context(user_id, message, 'no_entendido', response)
        
        return {
            'response': response,
            'intent': 'no_entendido',
            'conversational': True,
            'context_messages': len(context['messages']),
            'role': role
        }