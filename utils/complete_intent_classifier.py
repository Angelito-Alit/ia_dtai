import re

class CompleteIntentClassifier:
    def __init__(self):
        self.query_patterns = {
            'grupos_generales': {
                'keywords': ['que', 'grupos', 'hay', 'cuales', 'grupos'],
                'requires': [],
                'query_type': 'all_groups'
            },
            'total_alumnos_sistema': {
                'keywords': ['cuantos', 'alumnos', 'hay', 'total', 'sistema'],
                'requires': [],
                'query_type': 'student_count'
            },
            'profesores_activos_count': {
                'keywords': ['cuantos', 'profesores', 'activos', 'hay'],
                'requires': [],
                'query_type': 'active_teachers_count'
            },
            'directivos_nivel_count': {
                'keywords': ['cuantos', 'directivos', 'nivel', 'acceso'],
                'requires': [],
                'query_type': 'directors_by_level'
            },
            'usuarios_rol_count': {
                'keywords': ['cuantos', 'usuarios', 'rol'],
                'requires': [],
                'query_type': 'users_by_role'
            },
            'grupos_carrera_count': {
                'keywords': ['cuantos', 'grupos', 'creado', 'carrera'],
                'requires': [],
                'query_type': 'groups_by_career'
            },
            'bajas_definitivas_count': {
                'keywords': ['cuantos', 'alumnos', 'baja', 'definitivamente'],
                'requires': [],
                'query_type': 'permanent_dropouts'
            },
            'proporcion_tutores': {
                'keywords': ['proporcion', 'profesores', 'tutores', 'vs'],
                'requires': [],
                'query_type': 'tutor_ratio'
            },
            'asignaturas_activas_count': {
                'keywords': ['cuantas', 'asignaturas', 'activas', 'total'],
                'requires': [],
                'query_type': 'active_subjects'
            },
            'reportes_abiertos_count': {
                'keywords': ['cuantos', 'reportes', 'riesgo', 'abiertos'],
                'requires': [],
                'query_type': 'open_reports_count'
            },
            'solicitudes_sin_atender': {
                'keywords': ['cuantas', 'solicitudes', 'sin', 'atender', 'pendientes'],
                'requires': [],
                'query_type': 'pending_requests_count'
            },
            'grupos_año_2024': {
                'keywords': ['cuantos', 'grupos', 'crearon', '2024'],
                'requires': ['año'],
                'query_type': 'groups_by_year'
            },
            'alumnos_periodo_sep_dic': {
                'keywords': ['cuantos', 'alumnos', 'inscribieron', 'sep', 'dic', '2023'],
                'requires': ['periodo'],
                'query_type': 'students_by_period'
            },
            'solicitudes_año_2023': {
                'keywords': ['cuantas', 'solicitudes', 'ayuda', '2023'],
                'requires': ['año'],
                'query_type': 'requests_by_year'
            },
            'calificaciones_ciclo_ene_abr': {
                'keywords': ['cuantas', 'calificaciones', 'registraron', 'ene', 'abr', '2025'],
                'requires': ['ciclo_escolar'],
                'query_type': 'grades_by_cycle'
            },
            'carrera_mas_alumnos_nuevos_may_ago': {
                'keywords': ['carrera', 'mas', 'alumnos', 'nuevos', 'may', 'ago', '2025'],
                'requires': ['ciclo_escolar'],
                'query_type': 'career_most_new_students'
            },
            'carrera_mayor_asignaturas': {
                'keywords': ['carrera', 'mayor', 'cantidad', 'asignaturas', 'registradas'],
                'requires': [],
                'query_type': 'career_most_subjects'
            },
            'asignatura_mayor_horas_practicas': {
                'keywords': ['asignatura', 'mayor', 'cantidad', 'horas', 'practicas'],
                'requires': [],
                'query_type': 'subject_most_practical_hours'
            },
            'asignaturas_mayor_complejidad_5': {
                'keywords': ['5', 'asignaturas', 'mayor', 'complejidad'],
                'requires': [],
                'query_type': 'highest_complexity_subjects'
            },
            'carrera_mas_profesores_asignados': {
                'keywords': ['carrera', 'mas', 'profesores', 'asignados'],
                'requires': [],
                'query_type': 'career_most_teachers'
            },
            'alumnos_cuatrimestre_carrera': {
                'keywords': ['cuantos', 'alumnos', 'cuatrimestre', 'carrera'],
                'requires': ['nombre_carrera'],
                'query_type': 'students_per_term_career'
            },
            'profesor_mas_asignaturas_asignadas': {
                'keywords': ['profesor', 'mas', 'asignaturas', 'asignadas'],
                'requires': [],
                'query_type': 'teacher_most_subjects'
            },
            'profesores_mas_grupo': {
                'keywords': ['profesores', 'imparten', 'mas', 'grupo'],
                'requires': [],
                'query_type': 'teachers_multiple_groups'
            },
            'profesores_inactivos_actualmente': {
                'keywords': ['profesores', 'inactivos', 'actualmente'],
                'requires': [],
                'query_type': 'inactive_teachers'
            },
            'profesores_carrera_count': {
                'keywords': ['cuantos', 'profesores', 'carrera'],
                'requires': [],
                'query_type': 'teachers_per_career'
            },
            'profesores_mas_reportes_riesgo': {
                'keywords': ['profesores', 'emitido', 'mas', 'reportes', 'riesgo'],
                'requires': [],
                'query_type': 'teachers_most_reports'
            },
            'alumno_promedio_mas_alto_sistema': {
                'keywords': ['alumno', 'promedio', 'mas', 'alto', 'sistema'],
                'requires': [],
                'query_type': 'highest_gpa_student'
            },
            'alumnos_promedio_menor_60': {
                'keywords': ['alumnos', 'promedio', 'general', 'menor', '6'],
                'requires': [],
                'query_type': 'low_gpa_students'
            },
            'alumnos_ultimo_cuatrimestre_count': {
                'keywords': ['cuantos', 'alumnos', 'ultimo', 'cuatrimestre'],
                'requires': [],
                'query_type': 'final_term_students'
            },
            'alumnos_grupo_asignado_count': {
                'keywords': ['cuantos', 'alumnos', 'asignado', 'grupo', 'actualmente'],
                'requires': [],
                'query_type': 'students_with_group'
            },
            'alumnos_mas_reporte_riesgo': {
                'keywords': ['cuantos', 'alumnos', 'mas', 'reporte', 'riesgo'],
                'requires': [],
                'query_type': 'students_multiple_reports'
            },
            'aprobados_ordinario_sep_dic_2024': {
                'keywords': ['cuantos', 'alumnos', 'aprobaron', 'ordinario', 'sep', 'dic', '2024'],
                'requires': ['ciclo_escolar'],
                'query_type': 'passed_ordinary_cycle'
            },
            'asignaturas_mas_extraordinaria': {
                'keywords': ['asignaturas', 'mas', 'casos', 'calificacion', 'extraordinaria'],
                'requires': [],
                'query_type': 'subjects_most_extraordinary'
            },
            'promedio_general_asignatura': {
                'keywords': ['promedio', 'general', 'asignatura'],
                'requires': [],
                'query_type': 'average_per_subject'
            },
            'profesor_mas_reprobatorias': {
                'keywords': ['profesor', 'asigno', 'mas', 'calificaciones', 'reprobatorias'],
                'requires': [],
                'query_type': 'teacher_most_failing_grades'
            },
            'calificacion_promedio_grupo': {
                'keywords': ['calificacion', 'promedio', 'grupo'],
                'requires': [],
                'query_type': 'average_grade_per_group'
            },
            'aula_mas_usada_semana': {
                'keywords': ['aula', 'usa', 'mas', 'veces', 'semana'],
                'requires': [],
                'query_type': 'most_used_classroom'
            },
            'grupo_mas_alumnos_inscritos': {
                'keywords': ['grupo', 'mas', 'alumnos', 'inscritos'],
                'requires': [],
                'query_type': 'largest_group'
            },
            'grupos_capacidad_mayor_35': {
                'keywords': ['cuantos', 'grupos', 'capacidad', 'mayor', '35'],
                'requires': ['numero_capacidad'],
                'query_type': 'groups_capacity_over'
            },
            'grupos_mismo_aula_horario': {
                'keywords': ['grupos', 'asignados', 'mismo', 'aula', 'horario'],
                'requires': [],
                'query_type': 'groups_same_classroom_schedule'
            },
            'clases_sabados_count': {
                'keywords': ['cuantas', 'clases', 'imparten', 'sabados'],
                'requires': [],
                'query_type': 'saturday_classes'
            },
            'reportes_tipo_riesgo_count': {
                'keywords': ['cuantos', 'reportes', 'tipo', 'riesgo'],
                'requires': [],
                'query_type': 'reports_by_type'
            },
            'alumnos_mas_reporte_critico': {
                'keywords': ['alumnos', 'mas', 'reporte', 'critico'],
                'requires': [],
                'query_type': 'students_multiple_critical_reports'
            },
            'reportes_resueltos_total': {
                'keywords': ['cuantos', 'reportes', 'resuelto', 'total'],
                'requires': [],
                'query_type': 'resolved_reports'
            },
            'reportes_sin_seguimiento_count': {
                'keywords': ['cuantos', 'reportes', 'sin', 'seguimiento'],
                'requires': [],
                'query_type': 'reports_no_follow_up'
            },
            'profesores_mas_5_reportes': {
                'keywords': ['profesores', 'generado', 'mas', '5', 'reportes'],
                'requires': [],
                'query_type': 'teachers_over_5_reports'
            },
            'promedio_alumno_especifico': {
                'keywords': ['promedio', 'general', 'alumno'],
                'requires': ['nombre_alumno'],
                'query_type': 'promedio_alumno'
            },
            'alumnos_cuatrimestre_x': {
                'keywords': ['alumnos', 'cuatrimestre'],
                'requires': ['numero_cuatrimestre'],
                'query_type': 'alumnos_cuatrimestre'
            },
            'alumnos_carrera_count': {
                'keywords': ['cuantos', 'alumnos', 'carrera'],
                'requires': [],
                'query_type': 'alumnos_por_carrera'
            },
            'asignaturas_cursado_alumno': {
                'keywords': ['asignaturas', 'cursado', 'alumno', 'calificaciones'],
                'requires': ['nombre_alumno'],
                'query_type': 'asignaturas_alumno'
            },
            'reportes_riesgo_recibido_alumno': {
                'keywords': ['reportes', 'riesgo', 'recibido', 'alumno'],
                'requires': ['nombre_alumno'],
                'query_type': 'reportes_riesgo_alumno'
            },
            'grupos_asignados_profesor': {
                'keywords': ['grupos', 'asignados', 'profesor', 'cuatrimestre'],
                'requires': ['nombre_profesor'],
                'query_type': 'grupos_profesor'
            },
            'horarios_profesor': {
                'keywords': ['horarios', 'profesor'],
                'requires': ['nombre_profesor'],
                'query_type': 'horarios_profesor'
            }
        }
    
    def classify_and_extract(self, message):
        msg_lower = message.lower().strip()
        best_match = None
        best_score = 0
        
        for intent, pattern in self.query_patterns.items():
            score = 0
            total_keywords = len(pattern['keywords'])
            
            for keyword in pattern['keywords']:
                if keyword in msg_lower:
                    score += 1
            
            confidence = score / total_keywords if total_keywords > 0 else 0
            
            if score >= 2 and confidence > best_score:
                best_score = confidence
                best_match = intent
        
        if best_match:
            pattern = self.query_patterns[best_match]
            missing_data = self._extract_missing_data(message, pattern['requires'])
            
            return {
                'intent': best_match,
                'query_type': pattern['query_type'],
                'requires': pattern['requires'],
                'missing_data': missing_data,
                'confidence': best_score
            }
        
        return None
    
    def _extract_missing_data(self, message, required_fields):
        missing = []
        extracted_data = {}
        
        name_patterns = {
            'nombre_alumno': r'(?:alumno|estudiante)\s+([A-Za-zÁÉÍÓÚáéíóúñÑ\s]+?)(?:\s|$)',
            'nombre_profesor': r'(?:profesor|maestro)\s+([A-Za-zÁÉÍÓÚáéíóúñÑ\s]+?)(?:\s|$)',
            'nombre_carrera': r'(?:carrera|programa)\s+([A-Za-zÁÉÍÓÚáéíóúñÑ\s]+?)(?:\s|$)',
            'numero_cuatrimestre': r'(?:cuatrimestre|semestre)\s+(\d+)',
            'numero_capacidad': r'(?:mayor|mas)?\s*(?:a)?\s*(\d+)',
            'año': r'(\d{4})',
            'periodo': r'((?:SEP|ENE|MAY)-(?:DIC|ABR|AGO)\s+\d{4})',
            'ciclo_escolar': r'((?:SEP|ENE|MAY)-(?:DIC|ABR|AGO)\s+\d{4})'
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
            'nombre_carrera': 'Por favor, especifica el nombre de la carrera',
            'numero_cuatrimestre': 'Por favor, indica el numero del cuatrimestre (1, 2, 3, etc.)',
            'numero_capacidad': 'Por favor, especifica el numero de capacidad',
            'año': 'Por favor, indica el año (ejemplo: 2024)',
            'periodo': 'Por favor, especifica el periodo (ejemplo: SEP-DIC 2023)',
            'ciclo_escolar': 'Por favor, indica el ciclo escolar (ejemplo: ENE-ABR 2025)'
        }
        
        return prompts.get(missing_field, f'Por favor, proporciona: {missing_field}')