
TRAINING_DATA = {
    'ver_calificaciones': [
        "¿Cuáles son mis calificaciones?",
        "Muéstrame mis notas",
        "¿Cómo van mis calificaciones este cuatrimestre?",
        "Quiero ver mis resultados académicos",
        "¿Qué calificaciones tengo?",
        "Revisar mis puntuaciones",
        "¿Cómo estoy en mis materias?",
        "Consultar mis notas actuales",
        "Ver mis evaluaciones",
        "¿Cuál es mi promedio?"
    ],
    
    'alumnos_riesgo': [
        "¿Qué alumnos están en riesgo?",
        "Muéstrame estudiantes con problemas",
        "¿Quiénes necesitan ayuda académica?",
        "Lista de alumnos en situación de riesgo",
        "¿Hay estudiantes en peligro de reprobar?",
        "Alumnos con dificultades académicas",
        "¿Qué muchachos tienen problemas?",
        "Estudiantes que requieren atención",
        "¿Cuántos alumnos están en riesgo crítico?",
        "Mostrar reportes de riesgo activos"
    ],
    
    'promedio_carreras': [
        "¿Cuál es el promedio por carrera?",
        "Análisis de rendimiento por programa",
        "¿Cómo van las carreras académicamente?",
        "Estadísticas de promedios por licenciatura",
        "Comparar rendimiento entre carreras",
        "¿Qué carrera tiene mejor promedio?",
        "Desempeño académico por programa",
        "¿Cuál es la carrera con mejores calificaciones?",
        "Promedios generales por especialidad",
        "Ranking de carreras por rendimiento"
    ],
    
    'materias_reprobadas': [
        "¿Qué materias tienen más reprobados?",
        "Asignaturas con mayor índice de reprobación",
        "¿Cuáles son las materias más difíciles?",
        "Materias problemáticas del cuatrimestre",
        "¿En qué clases reprueban más?",
        "Asignaturas con bajo rendimiento",
        "¿Qué materias necesitan refuerzo?",
        "Análisis de reprobación por materia",
        "Materias con más dificultades",
        "¿Cuáles son las clases más complicadas?"
    ],
    
    'mi_horario': [
        "¿Cuál es mi horario?",
        "Muéstrame mis clases",
        "¿Cuándo tengo clases?",
        "Mi calendario de materias",
        "¿Qué hora tengo matemáticas?",
        "Horario de esta semana",
        "¿Cuándo es mi próxima clase?",
        "Ver mi programa de clases",
        "¿A qué hora empiezan mis clases?",
        "Calendario académico personal"
    ],
    
    'mis_grupos': [
        "¿Cuáles son mis grupos?",
        "Muéstrame las clases que imparto",
        "¿Qué materias tengo asignadas?",
        "Lista de mis grupos actuales",
        "¿Cuántos grupos manejo?",
        "Mis asignaciones académicas",
        "¿Qué clases doy este cuatrimestre?",
        "Grupos bajo mi responsabilidad",
        "¿Cuáles son mis asignaturas?",
        "Materias que imparto"
    ],
    
    'solicitudes_pendientes': [
        "¿Hay solicitudes de ayuda pendientes?",
        "Muéstrame las peticiones sin resolver",
        "¿Qué estudiantes pidieron ayuda?",
        "Solicitudes que requieren atención",
        "¿Cuántas ayudas están pendientes?",
        "Alumnos esperando respuesta",
        "¿Hay casos urgentes por atender?",
        "Peticiones de apoyo sin resolver",
        "¿Qué solicitudes debo revisar?",
        "Casos pendientes de seguimiento"
    ],
    
    'estadisticas_generales': [
        "¿Cómo está el sistema en general?",
        "Dame un resumen del estado actual",
        "Estadísticas generales de la universidad",
        "¿Cuáles son los números principales?",
        "Panorama general del cuatrimestre",
        "Indicadores principales del sistema",
        "¿Cómo van las cosas en general?",
        "Resumen ejecutivo de la situación",
        "Datos generales de la institución",
        "¿Cuál es el estado actual?"
    ],
    
    'buscar_alumno': [
        "Buscar alumno Juan Pérez",
        "¿Dónde está el estudiante con matrícula 12345?",
        "Información del alumno García",
        "Localizar estudiante por nombre",
        "¿Existe el alumno Pedro López?",
        "Datos del estudiante con matrícula 67890",
        "Buscar información de María González",
        "¿En qué grupo está el alumno Rodríguez?",
        "Consultar expediente del estudiante",
        "Encontrar alumno por apellido"
    ],
    
    'solicitar_ayuda': [
        "Necesito ayuda con mi situación académica",
        "Tengo problemas económicos",
        "Requiero apoyo psicológico",
        "No puedo pagar la colegiatura",
        "Tengo dificultades familiares",
        "Necesito orientación académica",
        "Estoy pasando por una crisis personal",
        "Requiero ayuda financiera",
        "Tengo problemas de salud mental",
        "Necesito hablar con alguien"
    ]
}
RESPONSE_PATTERNS = {
    'ver_calificaciones': {
        'no_data': [
            "No encontré calificaciones registradas para ti en este período.",
            "Aún no tienes calificaciones capturadas este cuatrimestre.",
            "No hay notas disponibles en el sistema actualmente."
        ],
        'intro': [
            "Aquí tienes tus calificaciones actuales:",
            "Te muestro tu resumen académico:",
            "Estos son tus resultados hasta ahora:"
        ]
    },
    
    'alumnos_riesgo': {
        'no_data': [
            "¡Excelente! No hay alumnos en situación de riesgo actualmente.",
            "Perfecto, todos los estudiantes están bien encaminados.",
            "No se detectaron alumnos en riesgo en este momento."
        ],
        'intro': [
            "He identificado estos alumnos que requieren atención:",
            "Los siguientes estudiantes están en situación de riesgo:",
            "Estos alumnos necesitan seguimiento especial:"
        ]
    },
    
    'promedio_carreras': {
        'no_data': [
            "No se encontraron datos de carreras con alumnos activos.",
            "No hay información de promedios disponible actualmente.",
            "No se pudieron obtener las estadísticas por carrera."
        ],
        'intro': [
            "Aquí tienes el análisis de rendimiento por carrera:",
            "Te muestro las estadísticas académicas por programa:",
            "Estos son los promedios por carrera:"
        ]
    }
}
CONVERSATION_EXAMPLES = [
    {
        'role': 'alumno',
        'messages': [
            {
                'user': "¿Cómo van mis calificaciones?",
                'intent': 'ver_calificaciones',
                'ai': "Te muestro tu resumen académico actual. Tienes un promedio general de 8.5, con 4 materias aprobadas y 1 en proceso. Tu mejor materia es Programación con 9.2 y necesitas mejorar en Matemáticas donde tienes 7.1."
            },
            {
                'user': "¿Qué puedo hacer para mejorar en matemáticas?",
                'intent': 'solicitar_ayuda',
                'ai': "Te recomiendo: 1) Asistir a las tutorías gratuitas los martes y jueves, 2) Formar un grupo de estudio con compañeros, 3) Practicar ejercicios adicionales, 4) Solicitar asesoría personalizada con el profesor. ¿Te gustaría que te ayude a programar una cita de tutoría?"
            }
        ]
    },
    {
        'role': 'profesor',
        'messages': [
            {
                'user': "¿Qué alumnos de mis grupos están en riesgo?",
                'intent': 'alumnos_riesgo',
                'ai': "En tus grupos hay 3 alumnos que requieren atención: Juan Pérez (ISW-501) con promedio 6.8 y 5 faltas, Ana García (ISW-501) con 2 materias reprobadas, y Carlos López (IMT-301) con reporte de problemas familiares. Te recomiendo programar citas individuales esta semana."
            }
        ]
    },
    {
        'role': 'directivo',
        'messages': [
            {
                'user': "Dame un panorama general del cuatrimestre",
                'intent': 'estadisticas_generales',
                'ai': "Resumen del cuatrimestre actual: 1,247 alumnos activos, promedio general de 8.1, 15% de estudiantes en riesgo académico, 23 solicitudes de ayuda pendientes, y 89% de asistencia promedio. Las carreras con mejor rendimiento son Gastronomía (8.6) e Ingeniería en Sistemas (8.4)."
            }
        ]
    }
]
DOMAIN_ENTITIES = {
    'carreras': [
        'sistemas', 'industrial', 'administracion', 'mecatronica', 'gastronomia',
        'computacion', 'informatica', 'software', 'negocios', 'empresas',
        'manufactura', 'produccion', 'robotica', 'automatizacion', 'culinaria'
    ],
    
    'materias_comunes': [
        'matematicas', 'fisica', 'quimica', 'programacion', 'algoritmos',
        'base de datos', 'redes', 'ingles', 'estadistica', 'calculo',
        'contabilidad', 'marketing', 'finanzas', 'recursos humanos',
        'diseño', 'manufactura', 'calidad', 'logistica'
    ],
    
    'periodos': [
        'ene-abr', 'may-ago', 'sep-dic', 'enero-abril', 'mayo-agosto',
        'septiembre-diciembre', 'primer cuatrimestre', 'segundo cuatrimestre',
        'tercer cuatrimestre'
    ],
    
    'tipos_riesgo': [
        'academico', 'asistencia', 'conducta', 'economico', 'personal',
        'familiar', 'salud mental', 'financiero', 'emocional'
    ],
    
    'niveles_riesgo': [
        'bajo', 'medio', 'alto', 'critico', 'leve', 'moderado', 'severo'
    ],
    
    'estados_alumno': [
        'activo', 'baja temporal', 'egresado', 'baja definitiva',
        'regular', 'irregular', 'condicional'
    ]
}
def get_training_data_by_intent(intent):
    return TRAINING_DATA.get(intent, [])

def get_all_training_data():
    all_data = []
    for intent, examples in TRAINING_DATA.items():
        for example in examples:
            all_data.append({
                'text': example,
                'intent': intent
            })
    return all_data

def get_response_patterns_for_intent(intent):
    return RESPONSE_PATTERNS.get(intent, {})

def get_conversation_examples_by_role(role):
    return [conv for conv in CONVERSATION_EXAMPLES if conv['role'] == role]

def get_domain_entities():
    return DOMAIN_ENTITIES

def validate_training_data():
    issues = []
    for intent in TRAINING_DATA:
        if len(TRAINING_DATA[intent]) < 5:
            issues.append(f"Intención '{intent}' tiene pocos ejemplos ({len(TRAINING_DATA[intent])})")
    all_texts = []
    for examples in TRAINING_DATA.values():
        all_texts.extend(examples)
    
    if len(all_texts) != len(set(all_texts)):
        issues.append("Hay ejemplos duplicados en los datos de entrenamiento")
    
    return issues
def generate_synthetic_data(intent, count=10):
    templates = {
        'ver_calificaciones': [
            "¿Cómo van mis {materia}?",
            "Mostrar mis notas de {periodo}",
            "¿Cuál es mi promedio en {materia}?",
            "Revisar calificaciones del {cuatrimestre} cuatrimestre"
        ],
        'alumnos_riesgo': [
            "¿Qué alumnos de {carrera} están en riesgo?",
            "Estudiantes con riesgo {tipo_riesgo}",
            "¿Hay alumnos en riesgo {nivel_riesgo}?",
            "Mostrar reportes de riesgo de {periodo}"
        ]
    }
    
    return templates.get(intent, [])