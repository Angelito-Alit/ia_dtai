import re

class EnhancedIntentClassifier:
    def __init__(self):
        self.query_patterns = {
            'promedio_alumno': {
                'keywords': ['promedio', 'general', 'alumno', 'estudiante'],
                'requires': ['nombre_alumno'],
                'query_type': 'specific_student'
            },
            'alumnos_cuatrimestre': {
                'keywords': ['alumnos', 'cuatrimestre', 'semestre'],
                'requires': ['numero_cuatrimestre'],
                'query_type': 'cuatrimestre_filter'
            },
            'alumnos_por_carrera': {
                'keywords': ['cuantos', 'alumnos', 'carrera', 'estudiantes'],
                'requires': [],
                'query_type': 'count_by_career'
            },
            'alumnos_bajas': {
                'keywords': ['alumnos', 'baja', 'temporal', 'definitiva', 'estado'],
                'requires': [],
                'query_type': 'student_status'
            },
            'grupo_aula_alumno': {
                'keywords': ['grupo', 'aula', 'asignado', 'alumno'],
                'requires': ['nombre_alumno'],
                'query_type': 'student_group'
            },
            'contacto_alumno': {
                'keywords': ['contacto', 'tutor', 'datos', 'alumno'],
                'requires': ['nombre_alumno'],
                'query_type': 'student_contact'
            },
            'evolucion_promedio': {
                'keywords': ['evolucion', 'promedio', 'historial', 'alumno'],
                'requires': ['nombre_alumno'],
                'query_type': 'grade_evolution'
            },
            'asignaturas_alumno': {
                'keywords': ['asignaturas', 'cursado', 'materias', 'alumno', 'calificaciones'],
                'requires': ['nombre_alumno'],
                'query_type': 'student_subjects'
            },
            'reportes_riesgo_alumno': {
                'keywords': ['reportes', 'riesgo', 'recibido', 'alumno'],
                'requires': ['nombre_alumno'],
                'query_type': 'student_risk_reports'
            },
            'solicitudes_ayuda_alumno': {
                'keywords': ['solicitudes', 'ayuda', 'hecho', 'alumno'],
                'requires': ['nombre_alumno'],
                'query_type': 'student_help_requests'
            },
            'encuestas_alumno': {
                'keywords': ['encuestas', 'contestado', 'respondido', 'alumno'],
                'requires': ['nombre_alumno'],
                'query_type': 'student_surveys'
            },
            'participacion_foro_alumno': {
                'keywords': ['participacion', 'foro', 'posts', 'alumno'],
                'requires': ['nombre_alumno'],
                'query_type': 'student_forum'
            },
            'interacciones_alumno': {
                'keywords': ['interacciones', 'likes', 'bookmarks', 'alumno'],
                'requires': ['nombre_alumno'],
                'query_type': 'student_interactions'
            },
            'asignaturas_profesor': {
                'keywords': ['asignaturas', 'imparte', 'profesor', 'materias'],
                'requires': ['nombre_profesor'],
                'query_type': 'teacher_subjects'
            },
            'grupos_profesor': {
                'keywords': ['grupos', 'asignados', 'profesor', 'cuatrimestre'],
                'requires': ['nombre_profesor'],
                'query_type': 'teacher_groups'
            },
            'horarios_profesor': {
                'keywords': ['horarios', 'profesor', 'clases'],
                'requires': ['nombre_profesor'],
                'query_type': 'teacher_schedule'
            },
            'alumnos_grupo_profesor': {
                'keywords': ['alumnos', 'grupo', 'profesor', 'impartido'],
                'requires': ['nombre_profesor', 'nombre_grupo'],
                'query_type': 'group_students'
            },
            'reportes_emitidos_profesor': {
                'keywords': ['reportes', 'riesgo', 'emitido', 'profesor'],
                'requires': ['nombre_profesor'],
                'query_type': 'teacher_reports'
            },
            'calificaciones_profesor': {
                'keywords': ['calificaciones', 'capturado', 'profesor', 'evaluaciones'],
                'requires': ['nombre_profesor'],
                'query_type': 'teacher_grades'
            },
            'experiencia_profesor': {
                'keywords': ['experiencia', 'especialidad', 'profesor'],
                'requires': ['nombre_profesor'],
                'query_type': 'teacher_experience'
            },
            'tutor_academico': {
                'keywords': ['tutor', 'academico', 'profesor'],
                'requires': ['nombre_profesor'],
                'query_type': 'academic_tutor'
            },
            'noticias_directivo': {
                'keywords': ['noticias', 'publicado', 'directivo'],
                'requires': ['nombre_directivo'],
                'query_type': 'director_news'
            },
            'categorias_foro_directivo': {
                'keywords': ['categorias', 'foro', 'encuestas', 'creado', 'directivo'],
                'requires': ['nombre_directivo'],
                'query_type': 'director_categories'
            },
            'solicitudes_directivo': {
                'keywords': ['solicitudes', 'ayuda', 'asignadas', 'directivo'],
                'requires': ['nombre_directivo'],
                'query_type': 'director_requests'
            },
            'conversaciones_directivo': {
                'keywords': ['conversaciones', 'chatbot', 'iniciado', 'directivo'],
                'requires': ['nombre_directivo'],
                'query_type': 'director_chats'
            },
            'asignaturas_carrera': {
                'keywords': ['asignaturas', 'carrera', 'corresponden'],
                'requires': ['nombre_carrera'],
                'query_type': 'career_subjects'
            },
            'asignaturas_cuatrimestre_carrera': {
                'keywords': ['asignaturas', 'cuatrimestre', 'carrera', 'imparten'],
                'requires': ['numero_cuatrimestre', 'nombre_carrera'],
                'query_type': 'career_term_subjects'
            },
            'asignaturas_complejidad': {
                'keywords': ['asignaturas', 'mayor', 'complejidad', 'nivel'],
                'requires': [],
                'query_type': 'subject_complexity'
            },
            'carreras_activas': {
                'keywords': ['carreras', 'activas', 'actualmente'],
                'requires': [],
                'query_type': 'active_careers'
            },
            'horas_asignatura': {
                'keywords': ['horas', 'teoricas', 'practicas', 'asignatura'],
                'requires': ['nombre_asignatura'],
                'query_type': 'subject_hours'
            },
            'grupos_activos': {
                'keywords': ['grupos', 'activos', 'ciclo', 'escolar'],
                'requires': [],
                'query_type': 'active_groups'
            },
            'tutor_grupo': {
                'keywords': ['profesor', 'tutor', 'grupo'],
                'requires': ['nombre_grupo'],
                'query_type': 'group_tutor'
            },
            'aula_grupo': {
                'keywords': ['aula', 'asignada', 'grupo'],
                'requires': ['nombre_grupo'],
                'query_type': 'group_classroom'
            },
            'capacidad_grupo': {
                'keywords': ['capacidad', 'maxima', 'grupo'],
                'requires': ['nombre_grupo'],
                'query_type': 'group_capacity'
            },
            'horarios_grupo_dia': {
                'keywords': ['horarios', 'grupo', 'lunes', 'martes', 'miercoles', 'jueves', 'viernes'],
                'requires': ['nombre_grupo', 'dia_semana'],
                'query_type': 'group_day_schedule'
            },
            'grupos_asignatura': {
                'keywords': ['grupos', 'imparte', 'asignatura', 'cuatrimestre'],
                'requires': ['nombre_asignatura'],
                'query_type': 'subject_groups'
            },
            'alumnos_reprobados': {
                'keywords': ['alumnos', 'reprobaron', 'asignatura', 'materia'],
                'requires': ['nombre_asignatura'],
                'query_type': 'failed_students'
            },
            'aprobados_ordinario_extraordinario': {
                'keywords': ['alumnos', 'aprobaron', 'ordinario', 'extraordinario'],
                'requires': [],
                'query_type': 'pass_type_stats'
            },
            'calificacion_final_alumno_asignatura': {
                'keywords': ['calificacion', 'final', 'alumno', 'asignatura'],
                'requires': ['nombre_alumno', 'nombre_asignatura'],
                'query_type': 'student_subject_grade'
            },
            'materias_cursando': {
                'keywords': ['materias', 'estatus', 'cursando', 'alumno'],
                'requires': ['nombre_alumno'],
                'query_type': 'current_subjects'
            },
            'profesor_calificacion': {
                'keywords': ['profesor', 'asigno', 'calificacion', 'alumno'],
                'requires': ['nombre_alumno'],
                'query_type': 'grade_teacher'
            },
            'reportes_tipo_nivel': {
                'keywords': ['reportes', 'riesgo', 'tipo', 'nivel', 'cuantos'],
                'requires': [],
                'query_type': 'risk_report_stats'
            },
            'reportes_abiertos': {
                'keywords': ['alumnos', 'reportes', 'abiertos', 'proceso'],
                'requires': [],
                'query_type': 'open_reports'
            },
            'acciones_recomendadas': {
                'keywords': ['acciones', 'recomendadas', 'alumno'],
                'requires': ['nombre_alumno'],
                'query_type': 'recommended_actions'
            },
            'profesores_mas_reportes': {
                'keywords': ['profesores', 'emitido', 'mas', 'reportes'],
                'requires': [],
                'query_type': 'teachers_most_reports'
            },
            'seguimiento_reporte': {
                'keywords': ['seguimiento', 'reporte', 'especifico'],
                'requires': ['id_reporte'],
                'query_type': 'report_follow_up'
            },
            'tipos_problemas_alumnos': {
                'keywords': ['tipo', 'problemas', 'reportan', 'alumnos'],
                'requires': [],
                'query_type': 'problem_types'
            },
            'solicitudes_pendientes': {
                'keywords': ['solicitudes', 'pendientes', 'atencion'],
                'requires': [],
                'query_type': 'pending_requests'
            },
            'urgencia_comun': {
                'keywords': ['nivel', 'urgencia', 'comun', 'solicitudes'],
                'requires': [],
                'query_type': 'urgency_stats'
            },
            'solicitudes_atendidas_directivo': {
                'keywords': ['solicitudes', 'atendido', 'directivo'],
                'requires': ['nombre_directivo'],
                'query_type': 'director_handled_requests'
            },
            'contacto_preferido': {
                'keywords': ['tipo', 'contacto', 'prefieren', 'alumnos'],
                'requires': [],
                'query_type': 'contact_preferences'
            },
            'mensajes_solicitud': {
                'keywords': ['mensajes', 'enviado', 'solicitud', 'especifica'],
                'requires': ['id_solicitud'],
                'query_type': 'request_messages'
            },
            'mensajes_alumno_directivo': {
                'keywords': ['mensajes', 'intercambiado', 'alumno', 'directivo'],
                'requires': ['nombre_alumno', 'nombre_directivo'],
                'query_type': 'student_director_messages'
            },
            'ultimo_mensaje': {
                'keywords': ['fecha', 'ultimo', 'mensaje', 'solicitud'],
                'requires': ['id_solicitud'],
                'query_type': 'last_message_date'
            },
            'noticias_activas': {
                'keywords': ['noticias', 'activas', 'destacadas'],
                'requires': [],
                'query_type': 'active_news'
            },
            'categoria_mas_noticias': {
                'keywords': ['categoria', 'mas', 'noticias'],
                'requires': [],
                'query_type': 'news_category_stats'
            },
            'vistas_noticia': {
                'keywords': ['vistas', 'tenido', 'noticia'],
                'requires': ['titulo_noticia'],
                'query_type': 'news_views'
            },
            'autor_noticia': {
                'keywords': ['quien', 'publico', 'noticia'],
                'requires': ['titulo_noticia'],
                'query_type': 'news_author'
            },
            'categorias_foro': {
                'keywords': ['categorias', 'foro', 'existen', 'publicaciones'],
                'requires': [],
                'query_type': 'forum_categories'
            },
            'posts_mas_vistos': {
                'keywords': ['posts', 'mas', 'vistos', 'comentados'],
                'requires': [],
                'query_type': 'popular_posts'
            },
            'comentarios_usuario': {
                'keywords': ['comentarios', 'hecho', 'usuario', 'foro'],
                'requires': ['nombre_usuario'],
                'query_type': 'user_comments'
            },
            'publicaciones_cerradas': {
                'keywords': ['publicaciones', 'cerradas', 'fijadas'],
                'requires': [],
                'query_type': 'closed_posts'
            },
            'reacciones_post': {
                'keywords': ['comento', 'reacciono', 'post', 'especifico'],
                'requires': ['id_post'],
                'query_type': 'post_reactions'
            },
            'encuestas_profesor': {
                'keywords': ['encuestas', 'creado', 'profesor'],
                'requires': ['nombre_profesor'],
                'query_type': 'teacher_surveys'
            },
            'respuestas_encuesta': {
                'keywords': ['alumnos', 'respondido', 'encuesta'],
                'requires': ['titulo_encuesta'],
                'query_type': 'survey_responses'
            },
            'respuestas_alumno_encuesta': {
                'keywords': ['respuestas', 'dio', 'alumno', 'encuesta'],
                'requires': ['nombre_alumno', 'titulo_encuesta'],
                'query_type': 'student_survey_answers'
            },
            'preguntas_encuesta': {
                'keywords': ['preguntas', 'contiene', 'encuesta', 'vulnerabilidad'],
                'requires': ['titulo_encuesta'],
                'query_type': 'survey_questions'
            }
        }
    
    def classify_and_extract(self, message):
        msg_lower = message.lower()
        best_match = None
        best_score = 0
        
        for intent, pattern in self.query_patterns.items():
            score = 0
            for keyword in pattern['keywords']:
                if keyword in msg_lower:
                    score += 1
            
            if score > best_score and score >= 2:
                best_score = score
                best_match = intent
        
        if best_match:
            pattern = self.query_patterns[best_match]
            missing_data = self._extract_missing_data(message, pattern['requires'])
            
            return {
                'intent': best_match,
                'query_type': pattern['query_type'],
                'requires': pattern['requires'],
                'missing_data': missing_data,
                'confidence': best_score / len(pattern['keywords'])
            }
        
        return None
    
    def _extract_missing_data(self, message, required_fields):
        missing = []
        extracted_data = {}
        
        name_patterns = {
            'nombre_alumno': r'(?:alumno|estudiante)\s+([A-Za-zÁÉÍÓÚáéíóúñÑ\s]+)',
            'nombre_profesor': r'(?:profesor|maestro)\s+([A-Za-zÁÉÍÓÚáéíóúñÑ\s]+)',
            'nombre_directivo': r'(?:directivo|director)\s+([A-Za-zÁÉÍÓÚáéíóúñÑ\s]+)',
            'nombre_carrera': r'(?:carrera|programa)\s+([A-Za-zÁÉÍÓÚáéíóúñÑ\s]+)',
            'nombre_asignatura': r'(?:asignatura|materia)\s+([A-Za-zÁÉÍÓÚáéíóúñÑ\s]+)',
            'nombre_grupo': r'(?:grupo)\s+([A-Za-z0-9\-]+)',
            'numero_cuatrimestre': r'(?:cuatrimestre|semestre)\s+(\d+)',
            'dia_semana': r'(?:lunes|martes|miercoles|jueves|viernes|sabado|domingo)',
            'id_reporte': r'(?:reporte)\s+(\d+)',
            'id_solicitud': r'(?:solicitud)\s+(\d+)',
            'titulo_noticia': r'(?:noticia)\s+"([^"]+)"',
            'titulo_encuesta': r'(?:encuesta)\s+"([^"]+)"',
            'id_post': r'(?:post)\s+(\d+)',
            'nombre_usuario': r'(?:usuario)\s+([A-Za-zÁÉÍÓÚáéíóúñÑ\s]+)'
        }
        
        for field in required_fields:
            if field in name_patterns:
                match = re.search(name_patterns[field], message, re.IGNORECASE)
                if match:
                    extracted_data[field] = match.group(1).strip()
                else:
                    missing.append(field)
            else:
                missing.append(field)
        
        return {
            'missing_fields': missing,
            'extracted_data': extracted_data
        }
    
    def get_question_prompt(self, missing_field):
        prompts = {
            'nombre_alumno': 'Por favor, proporciona el nombre del alumno',
            'nombre_profesor': 'Por favor, proporciona el nombre del profesor',
            'nombre_directivo': 'Por favor, proporciona el nombre del directivo',
            'nombre_carrera': 'Por favor, especifica el nombre de la carrera',
            'nombre_asignatura': 'Por favor, indica el nombre de la asignatura o materia',
            'nombre_grupo': 'Por favor, especifica el nombre o codigo del grupo',
            'numero_cuatrimestre': 'Por favor, indica el numero del cuatrimestre',
            'dia_semana': 'Por favor, especifica el dia de la semana',
            'id_reporte': 'Por favor, proporciona el ID del reporte',
            'id_solicitud': 'Por favor, proporciona el ID de la solicitud',
            'titulo_noticia': 'Por favor, indica el titulo de la noticia',
            'titulo_encuesta': 'Por favor, especifica el titulo de la encuesta',
            'id_post': 'Por favor, proporciona el ID del post',
            'nombre_usuario': 'Por favor, indica el nombre del usuario'
        }
        
        return prompts.get(missing_field, f'Por favor, proporciona: {missing_field}')