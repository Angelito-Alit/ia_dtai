import re

class EnhancedIntentClassifier:
    def __init__(self):
        self.query_patterns = {
            # Consultas generales sin parámetros específicos
            'grupos_generales': {
                'keywords': ['que', 'grupos', 'hay'],
                'requires': [],
                'query_type': 'all_groups'
            },
            'total_alumnos': {
                'keywords': ['cuantos', 'alumnos', 'total', 'sistema'],
                'requires': [],
                'query_type': 'student_count'
            },
            'profesores_activos': {
                'keywords': ['cuantos', 'profesores', 'activos'],
                'requires': [],
                'query_type': 'active_teachers'
            },
            'directivos_nivel': {
                'keywords': ['cuantos', 'directivos', 'nivel', 'acceso'],
                'requires': [],
                'query_type': 'directors_by_level'
            },
            'usuarios_por_rol': {
                'keywords': ['cuantos', 'usuarios', 'rol'],
                'requires': [],
                'query_type': 'users_by_role'
            },
            'grupos_por_carrera': {
                'keywords': ['cuantos', 'grupos', 'carrera'],
                'requires': [],
                'query_type': 'groups_by_career'
            },
            'bajas_definitivas': {
                'keywords': ['cuantos', 'alumnos', 'baja', 'definitivamente'],
                'requires': [],
                'query_type': 'permanent_dropouts'
            },
            'proporcion_tutores': {
                'keywords': ['proporcion', 'profesores', 'tutores'],
                'requires': [],
                'query_type': 'tutor_ratio'
            },
            'asignaturas_activas': {
                'keywords': ['cuantas', 'asignaturas', 'activas'],
                'requires': [],
                'query_type': 'active_subjects'
            },
            'reportes_abiertos_count': {
                'keywords': ['cuantos', 'reportes', 'riesgo', 'abiertos'],
                'requires': [],
                'query_type': 'open_reports_count'
            },
            'solicitudes_pendientes_count': {
                'keywords': ['cuantas', 'solicitudes', 'ayuda', 'sin', 'atender', 'pendientes'],
                'requires': [],
                'query_type': 'pending_requests_count'
            },
            
            # Análisis por año y periodo
            'grupos_año': {
                'keywords': ['cuantos', 'grupos', 'crearon', 'año'],
                'requires': ['año'],
                'query_type': 'groups_by_year'
            },
            'alumnos_periodo': {
                'keywords': ['cuantos', 'alumnos', 'inscribieron', 'periodo'],
                'requires': ['periodo'],
                'query_type': 'students_by_period'
            },
            'solicitudes_año': {
                'keywords': ['cuantas', 'solicitudes', 'ayuda', 'año'],
                'requires': ['año'],
                'query_type': 'requests_by_year'
            },
            'calificaciones_ciclo': {
                'keywords': ['cuantas', 'calificaciones', 'registraron', 'ciclo'],
                'requires': ['ciclo_escolar'],
                'query_type': 'grades_by_cycle'
            },
            'carrera_mas_alumnos_nuevos': {
                'keywords': ['carrera', 'mas', 'alumnos', 'nuevos', 'ciclo'],
                'requires': ['ciclo_escolar'],
                'query_type': 'career_most_new_students'
            },
            
            # Datos de carrera y asignatura
            'carrera_mas_asignaturas': {
                'keywords': ['carrera', 'mayor', 'cantidad', 'asignaturas'],
                'requires': [],
                'query_type': 'career_most_subjects'
            },
            'asignatura_mas_horas_practicas': {
                'keywords': ['asignatura', 'mayor', 'cantidad', 'horas', 'practicas'],
                'requires': [],
                'query_type': 'subject_most_practical_hours'
            },
            'asignaturas_mayor_complejidad': {
                'keywords': ['asignaturas', 'mayor', 'complejidad'],
                'requires': [],
                'query_type': 'highest_complexity_subjects'
            },
            'carrera_mas_profesores': {
                'keywords': ['carrera', 'mas', 'profesores', 'asignados'],
                'requires': [],
                'query_type': 'career_most_teachers'
            },
            'alumnos_por_cuatrimestre_carrera': {
                'keywords': ['cuantos', 'alumnos', 'cuatrimestre', 'carrera'],
                'requires': ['nombre_carrera'],
                'query_type': 'students_per_term_career'
            },
            
            # Profesores
            'profesor_mas_asignaturas': {
                'keywords': ['profesor', 'mas', 'asignaturas', 'asignadas'],
                'requires': [],
                'query_type': 'teacher_most_subjects'
            },
            'profesores_multiples_grupos': {
                'keywords': ['profesores', 'imparten', 'mas', 'grupo'],
                'requires': [],
                'query_type': 'teachers_multiple_groups'
            },
            'profesores_inactivos': {
                'keywords': ['profesores', 'inactivos'],
                'requires': [],
                'query_type': 'inactive_teachers'
            },
            'profesores_por_carrera_count': {
                'keywords': ['cuantos', 'profesores', 'carrera'],
                'requires': [],
                'query_type': 'teachers_per_career'
            },
            'profesores_mas_reportes': {
                'keywords': ['profesores', 'mas', 'reportes', 'riesgo'],
                'requires': [],
                'query_type': 'teachers_most_reports'
            },
            
            # Alumnos
            'alumno_promedio_mas_alto': {
                'keywords': ['alumno', 'promedio', 'mas', 'alto', 'sistema'],
                'requires': [],
                'query_type': 'highest_gpa_student'
            },
            'alumnos_promedio_bajo': {
                'keywords': ['alumnos', 'promedio', 'menor'],
                'requires': [],
                'query_type': 'low_gpa_students'
            },
            'alumnos_ultimo_cuatrimestre': {
                'keywords': ['cuantos', 'alumnos', 'ultimo', 'cuatrimestre'],
                'requires': [],
                'query_type': 'final_term_students'
            },
            'alumnos_con_grupo': {
                'keywords': ['cuantos', 'alumnos', 'asignado', 'grupo'],
                'requires': [],
                'query_type': 'students_with_group'
            },
            'alumnos_multiples_reportes': {
                'keywords': ['cuantos', 'alumnos', 'mas', 'reporte', 'riesgo'],
                'requires': [],
                'query_type': 'students_multiple_reports'
            },
            
            # Calificaciones
            'aprobados_ordinario_ciclo': {
                'keywords': ['cuantos', 'alumnos', 'aprobaron', 'ordinario', 'ciclo'],
                'requires': ['ciclo_escolar'],
                'query_type': 'passed_ordinary_cycle'
            },
            'asignaturas_extraordinarias': {
                'keywords': ['asignaturas', 'mas', 'casos', 'extraordinaria'],
                'requires': [],
                'query_type': 'subjects_most_extraordinary'
            },
            'promedio_por_asignatura': {
                'keywords': ['promedio', 'general', 'asignatura'],
                'requires': [],
                'query_type': 'average_per_subject'
            },
            'profesor_mas_reprobatorias': {
                'keywords': ['profesor', 'mas', 'calificaciones', 'reprobatorias'],
                'requires': [],
                'query_type': 'teacher_most_failing_grades'
            },
            'calificacion_promedio_grupo': {
                'keywords': ['calificacion', 'promedio', 'grupo'],
                'requires': [],
                'query_type': 'average_grade_per_group'
            },
            
            # Horarios y grupos
            'aula_mas_usada': {
                'keywords': ['aula', 'usa', 'mas', 'veces', 'semana'],
                'requires': [],
                'query_type': 'most_used_classroom'
            },
            'grupo_mas_alumnos': {
                'keywords': ['grupo', 'mas', 'alumnos', 'inscritos'],
                'requires': [],
                'query_type': 'largest_group'
            },
            'grupos_capacidad_mayor': {
                'keywords': ['cuantos', 'grupos', 'capacidad', 'mayor'],
                'requires': ['numero_capacidad'],
                'query_type': 'groups_capacity_over'
            },
            'grupos_misma_aula_horario': {
                'keywords': ['grupos', 'asignados', 'mismo', 'aula', 'horario'],
                'requires': [],
                'query_type': 'groups_same_classroom_schedule'
            },
            'clases_sabados': {
                'keywords': ['cuantas', 'clases', 'imparten', 'sabados'],
                'requires': [],
                'query_type': 'saturday_classes'
            },
            
            # Reportes de riesgo
            'reportes_por_tipo': {
                'keywords': ['cuantos', 'reportes', 'tipo', 'riesgo'],
                'requires': [],
                'query_type': 'reports_by_type'
            },
            'alumnos_reportes_criticos': {
                'keywords': ['alumnos', 'mas', 'reporte', 'critico'],
                'requires': [],
                'query_type': 'students_multiple_critical_reports'
            },
            'reportes_resueltos': {
                'keywords': ['cuantos', 'reportes', 'resuelto'],
                'requires': [],
                'query_type': 'resolved_reports'
            },
            'reportes_sin_seguimiento': {
                'keywords': ['cuantos', 'reportes', 'sin', 'seguimiento'],
                'requires': [],
                'query_type': 'reports_no_follow_up'
            },
            'profesores_mas_5_reportes': {
                'keywords': ['profesores', 'generado', 'mas', '5', 'reportes'],
                'requires': [],
                'query_type': 'teachers_over_5_reports'
            },
            
            # Solicitudes y chat
            'solicitudes_por_directivo': {
                'keywords': ['cuantas', 'solicitudes', 'respondidas', 'directivo'],
                'requires': [],
                'query_type': 'requests_per_director'
            },
            'alumnos_mas_chat': {
                'keywords': ['alumnos', 'usado', 'mas', 'chat', 'ayuda'],
                'requires': [],
                'query_type': 'students_most_chat_usage'
            },
            'solicitudes_presenciales': {
                'keywords': ['cuantas', 'solicitudes', 'atendieron', 'presencialmente'],
                'requires': [],
                'query_type': 'in_person_requests'
            },
            'tiempo_promedio_respuesta': {
                'keywords': ['promedio', 'tiempo', 'solicitud', 'respuesta'],
                'requires': [],
                'query_type': 'average_response_time'
            },
            'problema_mas_repetido': {
                'keywords': ['tipo', 'problema', 'repite', 'mas', 'solicitudes'],
                'requires': [],
                'query_type': 'most_common_problem'
            },
            
            # Noticias y foro
            'noticias_mas_vistas': {
                'keywords': ['noticias', 'mas', 'vistas'],
                'requires': [],
                'query_type': 'most_viewed_news'
            },
            'publicaciones_categoria_foro': {
                'keywords': ['cuantas', 'publicaciones', 'categoria', 'foro'],
                'requires': [],
                'query_type': 'posts_per_forum_category'
            },
            'usuario_mas_posts': {
                'keywords': ['usuario', 'publicado', 'mas', 'posts', 'foro'],
                'requires': [],
                'query_type': 'user_most_posts'
            },
            'bookmarks_posts': {
                'keywords': ['cuantas', 'veces', 'utilizado', 'bookmark', 'posts'],
                'requires': [],
                'query_type': 'bookmark_usage'
            },
            'comentarios_mas_likes': {
                'keywords': ['comentarios', 'mas', 'likes'],
                'requires': [],
                'query_type': 'most_liked_comments'
            },
            
            # Encuestas
            'encuesta_mas_respuestas': {
                'keywords': ['encuesta', 'mas', 'respuestas', 'registradas'],
                'requires': [],
                'query_type': 'survey_most_responses'
            },
            'alumnos_sin_encuesta': {
                'keywords': ['cuantos', 'alumnos', 'no', 'respondido', 'encuesta', 'obligatoria'],
                'requires': [],
                'query_type': 'students_no_survey_response'
            },
            'opcion_mas_seleccionada': {
                'keywords': ['opcion', 'mas', 'seleccionada', 'encuesta', 'vulnerabilidad'],
                'requires': [],
                'query_type': 'most_selected_option_vulnerability'
            },
            'encuestas_por_profesor': {
                'keywords': ['cuantas', 'encuestas', 'creado', 'profesor'],
                'requires': [],
                'query_type': 'surveys_per_teacher'
            },
            'preguntas_respuestas_no': {
                'keywords': ['preguntas', 'encuesta', 'recibieron', 'respuestas', 'no', 'frecuencia'],
                'requires': ['titulo_encuesta'],
                'query_type': 'survey_no_answers_frequency'
            },
            
            # Consultas existentes que ya tenías
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
            'numero_capacidad': r'(?:capacidad|mayor|mas)\s+(\d+)',
            'año': r'(?:año|year)\s+(\d{4})',
            'periodo': r'(?:periodo|ciclo)\s+([A-Z]{3}-[A-Z]{3}\s+\d{4})',
            'ciclo_escolar': r'(?:ciclo)\s+([A-Z]{3}-[A-Z]{3}\s+\d{4})',
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
            'nombre_alumno': 'Por favor, proporciona el nombre completo del alumno',
            'nombre_profesor': 'Por favor, proporciona el nombre completo del profesor',
            'nombre_directivo': 'Por favor, proporciona el nombre completo del directivo',
            'nombre_carrera': 'Por favor, especifica el nombre completo de la carrera',
            'nombre_asignatura': 'Por favor, indica el nombre completo de la asignatura o materia',
            'nombre_grupo': 'Por favor, especifica el nombre o codigo del grupo',
            'numero_cuatrimestre': 'Por favor, indica el numero del cuatrimestre (ejemplo: 1, 2, 3, etc.)',
            'numero_capacidad': 'Por favor, especifica el numero de capacidad (ejemplo: 35, 40, etc.)',
            'año': 'Por favor, indica el año (ejemplo: 2024, 2025)',
            'periodo': 'Por favor, especifica el periodo (ejemplo: SEP-DIC 2024, ENE-ABR 2025)',
            'ciclo_escolar': 'Por favor, indica el ciclo escolar (ejemplo: SEP-DIC 2024, MAY-AGO 2025)',
            'dia_semana': 'Por favor, especifica el dia de la semana (lunes, martes, miercoles, etc.)',
            'id_reporte': 'Por favor, proporciona el ID numerico del reporte',
            'id_solicitud': 'Por favor, proporciona el ID numerico de la solicitud',
            'titulo_noticia': 'Por favor, indica el titulo completo de la noticia entre comillas',
            'titulo_encuesta': 'Por favor, especifica el titulo completo de la encuesta entre comillas',
            'id_post': 'Por favor, proporciona el ID numerico del post',
            'nombre_usuario': 'Por favor, indica el nombre completo del usuario'
        }
        
        return prompts.get(missing_field, f'Por favor, proporciona: {missing_field}')