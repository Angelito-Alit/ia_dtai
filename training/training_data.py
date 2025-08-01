TRAINING_DATA = {
    'saludo': [
        'hola',
        'buenos dias',
        'buenas tardes',
        'buenas noches',
        'hello',
        'hi',
        'que tal',
        'como estas',
        'saludos'
    ],
    'despedida': [
        'adios',
        'hasta luego',
        'nos vemos',
        'bye',
        'chau',
        'hasta pronto',
        'me voy',
        'hasta la vista'
    ],
    'agradecimiento': [
        'gracias',
        'muchas gracias',
        'te lo agradezco',
        'thank you',
        'thanks',
        'muy amable',
        'excelente ayuda'
    ],
    'calificaciones': [
        'mis calificaciones',
        'mis notas',
        'como van mis materias',
        'que calificaciones tengo',
        'ver mis puntuaciones',
        'resultados academicos',
        'como voy en el semestre',
        'mis evaluaciones',
        'notas del cuatrimestre',
        'rendimiento academico'
    ],
    'riesgo': [
        'alumnos en riesgo',
        'estudiantes con problemas',
        'quien necesita ayuda',
        'reportes de riesgo',
        'alumnos problema',
        'estudiantes en dificultades',
        'casos criticos',
        'alumnos que necesitan atencion'
    ],
    'promedio': [
        'promedio por carrera',
        'rendimiento por carrera',
        'como van las carreras',
        'estadisticas por programa',
        'promedios generales',
        'rendimiento academico por area'
    ],
    'estadisticas': [
        'estadisticas generales',
        'numeros del sistema',
        'resumen general',
        'datos globales',
        'metricas del sistema',
        'indicadores generales',
        'panorama general'
    ],
    'emocional_positivo': [
        'me siento bien',
        'estoy feliz',
        'todo va excelente',
        'muy contento',
        'todo perfecto',
        'estoy motivado',
        'genial'
    ],
    'emocional_negativo': [
        'me siento mal',
        'estoy triste',
        'tengo problemas',
        'estoy preocupado',
        'me siento deprimido',
        'todo va mal',
        'tengo miedo'
    ],
    'pregunta_identidad': [
        'quien eres',
        'que eres',
        'que puedes hacer',
        'como me puedes ayudar',
        'para que sirves',
        'que funciones tienes'
    ],
    'pregunta_estado': [
        'como estas',
        'que tal estas',
        'como te va',
        'todo bien',
        'how are you'
    ]
}

DOMAIN_ENTITIES = {
    'materias': [
        'matematicas', 'fisica', 'quimica', 'biologia', 'historia',
        'geografia', 'literatura', 'ingles', 'programacion', 'base de datos',
        'redes', 'sistemas operativos', 'algoritmos', 'calculo', 'algebra'
    ],
    'carreras': [
        'ingenieria en sistemas', 'ingenieria industrial', 'administracion',
        'contaduria', 'derecho', 'medicina', 'psicologia', 'arquitectura',
        'diseño grafico', 'mercadotecnia'
    ],
    'niveles_riesgo': [
        'critico', 'alto', 'medio', 'bajo'
    ],
    'tipos_riesgo': [
        'academico', 'economico', 'personal', 'familiar', 'salud'
    ],
    'estados': [
        'activo', 'inactivo', 'graduado', 'baja temporal', 'baja definitiva'
    ]
}

def get_all_training_data():
    all_data = []
    for intent, examples in TRAINING_DATA.items():
        for example in examples:
            all_data.append((example, intent))
    return all_data

def get_training_data_by_intent(intent):
    return TRAINING_DATA.get(intent, [])

def validate_training_data():
    total_examples = sum(len(examples) for examples in TRAINING_DATA.values())
    intent_counts = {intent: len(examples) for intent, examples in TRAINING_DATA.items()}
    
    validation = {
        'total_examples': total_examples,
        'total_intents': len(TRAINING_DATA),
        'intent_distribution': intent_counts,
        'min_examples_per_intent': min(intent_counts.values()),
        'max_examples_per_intent': max(intent_counts.values()),
        'balanced': max(intent_counts.values()) / min(intent_counts.values()) <= 3
    }
    
    return validation

def add_training_example(intent, example):
    if intent not in TRAINING_DATA:
        TRAINING_DATA[intent] = []
    
    if example not in TRAINING_DATA[intent]:
        TRAINING_DATA[intent].append(example)
        return True
    return False

def get_intent_keywords(intent):
    if intent not in TRAINING_DATA:
        return []
    
    all_words = []
    for example in TRAINING_DATA[intent]:
        all_words.extend(example.split())
    
    word_freq = {}
    for word in all_words:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, freq in sorted_words[:10]]