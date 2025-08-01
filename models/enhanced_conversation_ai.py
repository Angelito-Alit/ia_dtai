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
        if not data:
            return "No se encontraron resultados para tu consulta."
        
        # Consultas generales
        if intent == 'grupos_generales':
            response = "**Grupos Activos en el Sistema:**\n\n"
            for group in data[:15]:
                response += f"• **{group['grupo']}** - {group['asignatura']}\n"
                response += f"   Cuatrimestre: {group['cuatrimestre']}\n"
                response += f"   Alumnos: {group['total_alumnos']}/{group['capacidad_maxima']}\n"
                if group['profesor']:
                    response += f"   Profesor: {group['profesor']}\n"
                response += "\n"
            if len(data) > 15:
                response += f"... y {len(data) - 15} grupos mas.\n"
            return response
            
        elif intent in ['student_count', 'active_teachers', 'permanent_dropouts', 'active_subjects', 'open_reports_count', 'pending_requests_count']:
            result = data[0]
            key = list(result.keys())[0]
            value = result[key]
            labels = {
                'total_alumnos': 'alumnos activos',
                'total_profesores': 'profesores activos',
                'total_bajas_definitivas': 'alumnos con baja definitiva',
                'total_asignaturas_activas': 'asignaturas activas',
                'reportes_abiertos': 'reportes de riesgo abiertos',
                'solicitudes_pendientes': 'solicitudes de ayuda pendientes'
            }
            label = labels.get(key, key.replace('_', ' '))
            return f"**Total en el sistema:** {value} {label}"
            
        elif intent == 'directors_by_level':
            response = "**Directivos por Nivel de Acceso:**\n\n"
            for row in data:
                response += f"• **{row['nivel_acceso'].title()}**: {row['total_directivos']} directivos\n"
            return response
            
        elif intent == 'users_by_role':
            response = "**Usuarios por Rol:**\n\n"
            for row in data:
                response += f"• **{row['rol'].title()}**: {row['total_usuarios']} usuarios\n"
            return response
            
        elif intent == 'groups_by_career':
            response = "**Grupos por Carrera:**\n\n"
            for row in data:
                response += f"• **{row['carrera']}**: {row['total_grupos']} grupos\n"
            return response
            
        elif intent == 'tutor_ratio':
            result = data[0]
            response = f"**Proporcion de Profesores Tutores:**\n\n"
            response += f"• Total profesores: {result['total_profesores']}\n"
            response += f"• Profesores tutores: {result['tutores']}\n"
            response += f"• Porcentaje de tutores: {result['porcentaje_tutores']}%\n"
            return response
            
        # Consultas de análisis
        elif intent in ['groups_by_year', 'students_by_period', 'requests_by_year', 'grades_by_cycle']:
            result = data[0]
            key = list(result.keys())[0]
            value = result[key]
            return f"**Resultado:** {value} registros encontrados"
            
        elif intent == 'career_most_new_students':
            result = data[0]
            return f"**Carrera con mas alumnos nuevos:** {result['carrera']} con {result['alumnos_nuevos']} alumnos"
            
        # Consultas de datos específicos
        elif intent in ['career_most_subjects', 'subject_most_practical_hours', 'career_most_teachers', 'teacher_most_subjects', 'largest_group', 'most_used_classroom']:
            result = data[0]
            if intent == 'career_most_subjects':
                return f"**Carrera con mas asignaturas:** {result['carrera']} con {result['total_asignaturas']} asignaturas"
            elif intent == 'subject_most_practical_hours':
                return f"**Asignatura con mas horas practicas:** {result['asignatura']} con {result['horas_practicas']} horas"
            elif intent == 'career_most_teachers':
                return f"**Carrera con mas profesores:** {result['carrera']} con {result['total_profesores']} profesores"
            elif intent == 'teacher_most_subjects':
                return f"**Profesor con mas asignaturas:** {result['profesor']} con {result['total_asignaturas']} asignaturas"
            elif intent == 'largest_group':
                return f"**Grupo con mas alumnos:** {result['grupo']} con {result['total_alumnos_inscritos']} alumnos"
            elif intent == 'most_used_classroom':
                return f"**Aula mas utilizada:** {result['aula']} se usa {result['veces_usada_semana']} veces por semana"
                
        elif intent == 'highest_complexity_subjects':
            response = "**Asignaturas con Mayor Complejidad:**\n\n"
            for i, subject in enumerate(data, 1):
                response += f"{i}. **{subject['asignatura']}** - Nivel {subject['nivel_complejidad']}\n"
                response += f"   Carrera: {subject['carrera']}\n\n"
            return response
            
        elif intent == 'students_per_term_career':
            carrera = list(extracted_data.values())[0] if extracted_data else 'la carrera'
            response = f"**Alumnos por Cuatrimestre en {carrera}:**\n\n"
            for row in data:
                response += f"• **Cuatrimestre {row['cuatrimestre_actual']}**: {row['total_alumnos']} alumnos\n"
            return response
            
        elif intent == 'teachers_multiple_groups':
            response = "**Profesores con Multiples Grupos:**\n\n"
            for teacher in data:
                response += f"• **{teacher['profesor']}**: {teacher['total_grupos']} grupos\n"
            return response
            
        elif intent == 'inactive_teachers':
            response = "**Profesores Inactivos:**\n\n"
            for teacher in data:
                response += f"• **{teacher['profesor']}**\n"
                if teacher['fecha_ultimo_acceso']:
                    response += f"   Ultimo acceso: {teacher['fecha_ultimo_acceso']}\n"
                response += "\n"
            return response
            
        elif intent == 'teachers_per_career':
            response = "**Profesores por Carrera:**\n\n"
            for row in data:
                response += f"• **{row['carrera']}**: {row['total_profesores']} profesores\n"
            return response
            
        elif intent == 'highest_gpa_student':
            result = data[0]
            return f"**Alumno con Mayor Promedio:** {result['alumno']} ({result['matricula']}) - Promedio: {result['promedio_general']:.2f}"
            
        elif intent == 'low_gpa_students':
            response = "**Alumnos con Promedio Menor a 6.0:**\n\n"
            for student in data:
                response += f"• **{student['alumno']}** ({student['matricula']}) - Promedio: {student['promedio_general']:.2f}\n"
            return response
            
        elif intent in ['final_term_students', 'students_with_group', 'students_multiple_reports']:
            result = data[0]
            key = list(result.keys())[0]
            value = result[key]
            labels = {
                'alumnos_ultimo_cuatrimestre': 'alumnos en su ultimo cuatrimestre',
                'alumnos_con_grupo': 'alumnos con grupo asignado',
                'alumnos_multiples_reportes': 'alumnos con multiples reportes de riesgo'
            }
            label = labels.get(key, key.replace('_', ' '))
            return f"**Total:** {value} {label}"
            
        elif intent == 'subjects_most_extraordinary':
            response = "**Asignaturas con Mas Casos Extraordinarios:**\n\n"
            for subject in data:
                response += f"• **{subject['asignatura']}**: {subject['casos_extraordinarios']} casos\n"
            return response
            
        elif intent == 'average_per_subject':
            response = "**Promedio General por Asignatura:**\n\n"
            for subject in data[:15]:
                response += f"• **{subject['asignatura']}**: {subject['promedio_general']}\n"
            if len(data) > 15:
                response += f"... y {len(data) - 15} asignaturas mas.\n"
            return response
            
        elif intent == 'teacher_most_failing_grades':
            result = data[0]
            return f"**Profesor con mas calificaciones reprobatorias:** {result['profesor']} con {result['calificaciones_reprobatorias']} calificaciones reprobatorias"
            
        elif intent == 'average_grade_per_group':
            response = "**Promedio de Calificaciones por Grupo:**\n\n"
            for group in data[:15]:
                response += f"• **{group['grupo']}**: {group['promedio_grupo']}\n"
            if len(data) > 15:
                response += f"... y {len(data) - 15} grupos mas.\n"
            return response
            
        elif intent in ['groups_capacity_over', 'saturday_classes']:
            result = data[0]
            key = list(result.keys())[0]
            value = result[key]
            if intent == 'groups_capacity_over':
                capacidad = list(extracted_data.values())[0] if extracted_data else 'N/A'
                return f"**Grupos con capacidad mayor a {capacidad}:** {value} grupos"
            else:
                return f"**Clases los sabados:** {value} clases"
                
        elif intent == 'groups_same_classroom_schedule':
            if not data:
                return "**No se encontraron conflictos de horarios en las aulas.**"
            response = "**Grupos con Conflictos de Horario en la Misma Aula:**\n\n"
            for conflict in data:
                response += f"• **Aula {conflict['aula']}** - {conflict['dia_semana']} {conflict['hora_inicio']}-{conflict['hora_fin']}\n"
                response += f"   Grupos en conflicto: {conflict['grupos_conflicto']}\n\n"
            return response
            
        elif intent == 'reports_by_type':
            response = "**Reportes de Riesgo por Tipo:**\n\n"
            for report_type in data:
                response += f"• **{report_type['tipo_riesgo'].title()}**: {report_type['total_reportes']} reportes\n"
            return response
            
        elif intent == 'students_multiple_critical_reports':
            if not data:
                return "**No hay alumnos con multiples reportes criticos.**"
            response = "**Alumnos con Multiples Reportes Criticos:**\n\n"
            for student in data:
                response += f"• **{student['alumno']}** ({student['matricula']}) - {student['reportes_criticos']} reportes criticos\n"
            return response
            
        elif intent in ['resolved_reports', 'reports_no_follow_up']:
            result = data[0]
            key = list(result.keys())[0]
            value = result[key]
            labels = {
                'reportes_resueltos': 'reportes resueltos',
                'reportes_sin_seguimiento': 'reportes sin seguimiento'
            }
            label = labels.get(key, key.replace('_', ' '))
            return f"**Total:** {value} {label}"
            
        elif intent == 'teachers_over_5_reports':
            if not data:
                return "**No hay profesores con mas de 5 reportes emitidos.**"
            response = "**Profesores con Mas de 5 Reportes Emitidos:**\n\n"
            for teacher in data:
                response += f"• **{teacher['profesor']}**: {teacher['total_reportes']} reportes\n"
            return response
            
        # Continuar con el resto de consultas específicas
        elif intent == 'promedio_alumno':
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
        
        elif intent == 'requests_per_director':
            response = "**Solicitudes Respondidas por Directivo:**\n\n"
            for director in data:
                response += f"• **{director['directivo']}**: {director['solicitudes_respondidas']} solicitudes\n"
            return response
            
        elif intent == 'students_most_chat_usage':
            response = "**Alumnos que Mas Usan el Chat de Ayuda:**\n\n"
            for student in data:
                response += f"• **{student['alumno']}** ({student['matricula']}) - {student['veces_usado_chat']} veces\n"
            return response
            
        elif intent in ['in_person_requests', 'bookmark_usage']:
            result = data[0]
            key = list(result.keys())[0]
            value = result[key]
            labels = {
                'solicitudes_presenciales': 'solicitudes atendidas presencialmente',
                'total_bookmarks': 'veces que se uso bookmark'
            }
            label = labels.get(key, key.replace('_', ' '))
            return f"**Total:** {value} {label}"
            
        elif intent == 'average_response_time':
            result = data[0]
            if result['promedio_horas_respuesta']:
                return f"**Tiempo promedio de respuesta:** {result['promedio_horas_respuesta']} horas"
            else:
                return "**No se pudo calcular el tiempo promedio de respuesta.**"
                
        elif intent == 'most_common_problem':
            result = data[0]
            return f"**Problema mas reportado:** {result['tipo_problema']} ({result['veces_reportado']} veces)"
            
        elif intent == 'most_viewed_news':
            response = "**Noticias Mas Vistas:**\n\n"
            for news in data:
                response += f"• **{news['titulo']}** - {news['vistas']} vistas\n"
                response += f"   Autor: {news['autor']}\n\n"
            return response
            
        elif intent == 'posts_per_forum_category':
            response = "**Publicaciones por Categoria del Foro:**\n\n"
            for category in data:
                response += f"• **{category['categoria']}**: {category['total_publicaciones']} publicaciones\n"
            return response
            
        elif intent == 'user_most_posts':
            result = data[0]
            return f"**Usuario con mas posts:** {result['usuario']} con {result['total_posts']} publicaciones"
            
        elif intent == 'most_liked_comments':
            response = "**Comentarios con Mas Likes:**\n\n"
            for comment in data:
                content = comment['contenido'][:100] + "..." if len(comment['contenido']) > 100 else comment['contenido']
                response += f"• **{comment['total_likes']} likes** - {content}\n\n"
            return response
            
        elif intent == 'survey_most_responses':
            result = data[0]
            return f"**Encuesta con mas respuestas:** {result['titulo']} con {result['total_respuestas']} respuestas"
            
        elif intent == 'students_no_survey_response':
            result = data[0]
            return f"**Alumnos que no han respondido encuestas obligatorias:** {result['alumnos_sin_respuesta']} alumnos"
            
        elif intent == 'most_selected_option_vulnerability':
            result = data[0]
            return f"**Opcion mas seleccionada en encuesta de vulnerabilidad:** {result['respuesta']} ({result['veces_seleccionada']} veces)"
            
        elif intent == 'surveys_per_teacher':
            response = "**Encuestas Creadas por Profesor:**\n\n"
            for teacher in data:
                response += f"• **{teacher['profesor']}**: {teacher['encuestas_creadas']} encuestas\n"
            return response
            
        elif intent == 'survey_no_answers_frequency':
            encuesta = list(extracted_data.values())[0] if extracted_data else 'la encuesta'
            response = f"**Preguntas con mas respuestas 'No' en {encuesta}:**\n\n"
            for question in data:
                response += f"• **{question['respuestas_no']} respuestas 'No'** - {question['pregunta'][:80]}...\n\n"
            return response
            
        else:
            # Respuesta genérica para consultas no específicamente formateadas
            if len(data) == 1 and len(data[0]) <= 3:
                result = data[0]
                response = "**Resultado:**\n\n"
                for key, value in result.items():
                    response += f"• **{key.replace('_', ' ').title()}**: {value}\n"
                return response
            else:
                response = f"**Resultados encontrados ({len(data)}):**\n\n"
                for i, row in enumerate(data[:10], 1):
                    response += f"**{i}.** "
                    important_fields = []
                    for key, value in row.items():
                        if value is not None and key not in ['id', 'fecha_creacion', 'fecha_actualizacion']:
                            if 'nombre' in key or 'titulo' in key:
                                important_fields.insert(0, f"{value}")
                            else:
                                important_fields.append(f"{key.replace('_', ' ')}: {value}")
                    
                    response += " | ".join(important_fields[:3])
                    response += "\n"
                
                if len(data) > 10:
                    response += f"\n... y {len(data) - 10} resultados mas."
                
                return responseparcial_3']:
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