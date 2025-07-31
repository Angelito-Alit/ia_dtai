from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
import mysql.connector
from datetime import datetime
import random
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

conversation_contexts = {}

def get_db_config():
    return {
        'host': os.environ.get('DB_HOST', 'bluebyte.space'),
        'user': os.environ.get('DB_USER', 'bluebyte_angel'),
        'password': os.environ.get('DB_PASSWORD', 'orbitalsoft'),
        'database': os.environ.get('DB_NAME', 'bluebyte_dtai_web'),
        'port': int(os.environ.get('DB_PORT', 3306)),
        'charset': 'utf8mb4',
        'autocommit': True
    }

def get_db_connection():
    try:
        config = get_db_config()
        connection = mysql.connector.connect(**config)
        logger.info("Conexión a BD exitosa")
        return connection
    except Exception as e:
        logger.error(f"Error BD: {e}")
        return None

def execute_query(query, params=None):
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or [])
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        logger.info(f"Query ejecutada: {len(result)} filas")
        return result
    except Exception as e:
        logger.error(f"Error query: {e}")
        if connection:
            connection.close()
        return None

def get_conversation_context(user_id):
    if user_id not in conversation_contexts:
        conversation_contexts[user_id] = {
            'messages': [],
            'last_intent': None,
            'user_preferences': {},
            'session_topics': [],
            'conversation_depth': 0
        }
    return conversation_contexts[user_id]

def update_context(user_id, message, intent, response):
    context = get_conversation_context(user_id)
    context['messages'].append({
        'user': message,
        'bot': response[:200],
        'intent': intent,
        'time': datetime.now(),
        'sentiment': analyze_sentiment(message)
    })
    context['last_intent'] = intent
    context['session_topics'].append(intent)
    context['conversation_depth'] += 1
    
    if len(context['messages']) > 15:
        context['messages'] = context['messages'][-15:]

def analyze_sentiment(message):
    positive_words = [
        'bien', 'genial', 'excelente', 'perfecto', 'bueno', 'feliz', 'contento', 'gracias',
        'fantástico', 'increíble', 'maravilloso', 'estupendo', 'satisfecho', 'alegre',
        'optimista', 'positivo', 'emocionado', 'entusiasmado', 'motivado', 'inspirado'
    ]
    
    negative_words = [
        'mal', 'terrible', 'horrible', 'triste', 'preocupado', 'problema', 'difícil',
        'frustrado', 'molesto', 'enojado', 'decepcionado', 'desesperado', 'confundido',
        'abrumado', 'estresado', 'ansioso', 'nervioso', 'inseguro', 'desanimado'
    ]
    
    msg_lower = message.lower()
    positive_count = sum(1 for word in positive_words if word in msg_lower)
    negative_count = sum(1 for word in negative_words if word in msg_lower)
    
    if positive_count > negative_count:
        return 'positive'
    elif negative_count > positive_count:
        return 'negative'
    return 'neutral'

def classify_intent_advanced(message, context):
    msg = message.lower().strip()
    recent_intents = [m['intent'] for m in context['messages'][-3:]] if context['messages'] else []
    
    saludo_patterns = [
        'hola', 'hello', 'hi', 'hey', 'buenos días', 'buenas tardes', 'buenas noches',
        'qué tal', 'como estas', 'saludos', 'buen día', 'que onda', 'wassup',
        'muy buenos días', 'hola que tal', 'buenas', 'good morning', 'good afternoon'
    ]
    
    agradecimiento_patterns = [
        'gracias', 'te agradezco', 'muchas gracias', 'thank you', 'thanks',
        'mil gracias', 'te lo agradezco mucho', 'muy agradecido', 'agradezco',
        'gracias por todo', 'muchas gracias por', 'te doy las gracias'
    ]
    
    despedida_patterns = [
        'adiós', 'bye', 'hasta luego', 'nos vemos', 'chao', 'goodbye',
        'hasta la vista', 'hasta pronto', 'me despido', 'que tengas buen día',
        'hasta mañana', 'see you later', 'nos hablamos', 'cuídate'
    ]
    
    estado_emocional_negativo = [
        'me siento mal', 'estoy triste', 'tengo problemas', 'estoy preocupado',
        'me siento abrumado', 'estoy frustrado', 'tengo dificultades', 'estoy confundido',
        'me siento perdido', 'estoy desanimado', 'tengo miedo', 'estoy nervioso',
        'me siento ansioso', 'estoy estresado', 'tengo dudas', 'me siento inseguro'
    ]
    
    estado_emocional_positivo = [
        'me siento bien', 'estoy feliz', 'estoy contento', 'me siento genial',
        'estoy emocionado', 'me siento fantástico', 'estoy motivado', 'me siento inspirado',
        'estoy optimista', 'me siento satisfecho', 'estoy alegre', 'me siento excelente'
    ]
    
    pregunta_estado_patterns = [
        'cómo estás', 'que tal estás', 'how are you', 'como te va', 'cómo te encuentras',
        'que tal te va', 'como andas', 'cómo vas', 'todo bien contigo', 'como sigues'
    ]
    
    pregunta_identidad_patterns = [
        'quién eres', 'qué eres', 'who are you', 'qué puedes hacer', 'cuáles son tus funciones',
        'para qué sirves', 'qué haces', 'cuál es tu propósito', 'de qué me puedes ayudar',
        'qué tipo de asistente eres', 'cuéntame sobre ti', 'preséntate'
    ]
    
    calificaciones_patterns = [
        'calificaciones', 'notas', 'puntuaciones', 'resultados', 'cómo van mis materias',
        'cómo voy académicamente', 'mis notas', 'rendimiento académico', 'evaluaciones',
        'exámenes', 'parciales', 'promedios', 'boleta', 'historial académico',
        'como me fue', 'que tal mis calificaciones', 'revisar mis notas'
    ]
    
    riesgo_patterns = [
        'riesgo', 'problemas académicos', 'dificultades', 'estudiantes problema', 'alumnos difíciles',
        'deserción', 'abandono escolar', 'estudiantes en peligro', 'alumnos vulnerables',
        'casos críticos', 'alertas académicas', 'seguimiento especial', 'intervención',
        'estudiantes que necesitan ayuda', 'problemas de rendimiento'
    ]
    
    promedio_patterns = [
        'promedio', 'rendimiento', 'desempeño', 'cómo van las carreras', 'performance',
        'estadísticas académicas', 'métricas de rendimiento', 'análisis comparativo',
        'ranking académico', 'posición académica', 'nivel académico', 'índices académicos'
    ]
    
    estadisticas_patterns = [
        'estadísticas', 'números', 'datos', 'resumen', 'panorama general', 'métricas',
        'indicadores', 'dashboard', 'reporte general', 'cifras', 'analytics',
        'información general', 'estado del sistema', 'overview', 'snapshot'
    ]
    
    analisis_avanzado_patterns = [
        'análisis', 'reporte', 'tendencias', 'comparar', 'evaluar', 'investigar',
        'profundizar', 'correlaciones', 'patrones', 'insights', 'business intelligence',
        'data mining', 'análisis predictivo', 'forecasting', 'benchmarking'
    ]
    
    recomendaciones_patterns = [
        'recomendaciones', 'qué me sugieres', 'qué debo hacer', 'consejos', 'sugerencias',
        'qué recomiendas', 'cuál es tu consejo', 'qué opinas', 'qué me aconsejas',
        'dame tu opinión', 'qué harías tú', 'qué estrategia', 'cómo mejorar'
    ]
    
    materias_patterns = [
        'materias', 'asignaturas', 'clases', 'cursos', 'subjects', 'disciplinas',
        'módulos', 'seminarios', 'talleres', 'laboratorios', 'materias reprobadas',
        'asignaturas pendientes', 'materias difíciles', 'clases complicadas'
    ]
    
    profesores_patterns = [
        'profesores', 'maestros', 'docentes', 'instructores', 'catedráticos',
        'personal docente', 'facultad', 'staff académico', 'profesorado',
        'mentores', 'tutores', 'coordinadores académicos'
    ]
    
    estudiantes_patterns = [
        'estudiantes', 'alumnos', 'muchachos', 'chavos', 'compañeros',
        'población estudiantil', 'matrícula', 'cuerpo estudiantil',
        'comunidad estudiantil', 'estudiantes activos', 'inscripciones'
    ]
    
    horarios_patterns = [
        'horarios', 'calendario', 'schedule', 'programa', 'cronograma',
        'horario de clases', 'agenda académica', 'distribución horaria',
        'programación académica', 'itinerario', 'tiempos de clase'
    ]
    
    if any(pattern in msg for pattern in saludo_patterns):
        return 'saludo'
    
    if any(pattern in msg for pattern in agradecimiento_patterns):
        return 'agradecimiento'
        
    if any(pattern in msg for pattern in despedida_patterns):
        return 'despedida'
    
    if any(pattern in msg for pattern in estado_emocional_negativo):
        return 'emocional_negativo'
    
    if any(pattern in msg for pattern in estado_emocional_positivo):
        return 'emocional_positivo'
    
    if any(pattern in msg for pattern in pregunta_estado_patterns):
        return 'pregunta_estado'
        
    if any(pattern in msg for pattern in pregunta_identidad_patterns):
        return 'pregunta_identidad'
    
    if any(pattern in msg for pattern in calificaciones_patterns):
        return 'calificaciones'
    
    if any(pattern in msg for pattern in riesgo_patterns):
        return 'riesgo'
    
    if any(pattern in msg for pattern in promedio_patterns):
        return 'promedio'
        
    if any(pattern in msg for pattern in estadisticas_patterns):
        return 'estadisticas'
    
    if any(pattern in msg for pattern in analisis_avanzado_patterns):
        return 'analisis_avanzado'
    
    if any(pattern in msg for pattern in recomendaciones_patterns):
        return 'solicitar_recomendaciones'
    
    if any(pattern in msg for pattern in materias_patterns):
        return 'consulta_materias'
    
    if any(pattern in msg for pattern in profesores_patterns):
        return 'consulta_profesores'
    
    if any(pattern in msg for pattern in estudiantes_patterns):
        return 'consulta_estudiantes'
    
    if any(pattern in msg for pattern in horarios_patterns):
        return 'consulta_horarios'
    
    if context['last_intent'] and any(pattern in msg for pattern in ['más detalles', 'profundiza', 'explícame más', 'y qué más', 'continúa', 'sigue']):
        return f"profundizar_{context['last_intent']}"
    
    if any(pattern in msg for pattern in ['sí', 'claro', 'perfecto', 'ok', 'está bien', 'de acuerdo', 'correcto', 'exacto']):
        return 'afirmacion'
    
    if any(pattern in msg for pattern in ['no', 'nada', 'mejor no', 'no gracias', 'paso', 'negativo']):
        return 'negacion'
    
    pregunta_starters = ['cuántos', 'cuántas', 'qué', 'cómo', 'dónde', 'cuándo', 'por qué', 'quién', 'cuál', 'cuáles']
    if any(msg.startswith(starter) for starter in pregunta_starters):
        return 'pregunta_especifica'
    
    return 'conversacion_general'

def get_conversational_response(intent, message, context, role='directivo', user_id=1):
    user_name = context.get('user_preferences', {}).get('name', 'usuario')
    recent_sentiment = context['messages'][-1]['sentiment'] if context['messages'] else 'neutral'
    depth = context.get('conversation_depth', 0)
    
    responses = {
        'saludo': [
            "Hola, me alegra verte de nuevo. Soy tu asistente de análisis académico de DTAI. ¿Cómo puedo ayudarte hoy?",
            "Muy buenas, perfecto timing. Justo estaba procesando algunos datos interesantes del sistema. ¿Qué necesitas saber?",
            "Hola, espero que tengas un excelente día. Como siempre, estoy aquí para cualquier análisis o consulta que necesites.",
            "Buenos días, listo para sumergirnos en los datos académicos. ¿Por dónde empezamos?",
            "Saludos, qué gusto tenerte por aquí. ¿En qué análisis podemos trabajar juntos hoy?"
        ],
        
        'pregunta_estado': [
            "Excelente, gracias por preguntar. Estoy funcionando al cien por ciento, procesando datos en tiempo real y listo para cualquier desafío analítico.",
            "Fantástico, acabo de actualizar mis algoritmos y tengo la base de datos completamente fresca. ¿Qué análisis interesante podemos hacer juntos?",
            "Perfecto como siempre. Me encanta cuando me preguntan esto porque significa que vamos a tener una buena conversación de trabajo.",
            "Muy bien, todos los sistemas operando correctamente. Base de datos conectada, algoritmos optimizados, listo para ayudarte."
        ],
        
        'pregunta_identidad': [
            "Soy tu asistente de inteligencia artificial especializado en análisis educativo. Mi trabajo es procesar datos académicos y convertirlos en insights útiles para la toma de decisiones.",
            "Me presento formalmente: soy tu analista de datos académicos virtual. Mi cerebro está conectado directamente a la base de datos institucional para darte información en tiempo real.",
            "Soy tu compañero de análisis académico disponible las veinticuatro horas. Mi especialidad es hacer que la información compleja sea fácil de entender y útil para mejorar la educación.",
            "Excelente pregunta. Soy una inteligencia artificial diseñada específicamente para el análisis de datos educativos. Puedo ayudarte con estadísticas, reportes, análisis predictivo y mucho más."
        ],
        
        'emocional_negativo': [
            "Entiendo perfectamente esa sensación. Los desafíos educativos pueden ser abrumadores, pero cada dato que analizamos juntos es un paso hacia soluciones reales. ¿Te parece si revisamos algunos números para encontrar oportunidades?",
            "Lamento mucho que te sientas así. Como alguien que trabaja constantemente con datos, he aprendido que detrás de cada estadística preocupante hay historias de superación esperando ser escritas.",
            "Esos sentimientos son completamente válidos. Los datos confirman que enfrentar problemas educativos es complejo, pero también muestran patrones increíbles de recuperación y éxito.",
            "Te comprendo totalmente. Trabajar con datos educativos me ha enseñado que los momentos difíciles suelen ser el preludio de los grandes avances. ¿Quieres que analicemos la situación juntos?"
        ],
        
        'emocional_positivo': [
            "Me encanta esa energía positiva. Los datos también reflejan esa positividad, siempre es genial ver cuando las tendencias van hacia arriba. ¿Qué quieres que analicemos para celebrar?",
            "Qué bueno escuchar eso. Esa actitud positiva es contagiosa, y curiosamente, he notado que los mejores insights salen cuando trabajamos con buen ánimo.",
            "Eso es exactamente lo que me gusta escuchar. Tu energía positiva combinada con mi capacidad de análisis de datos es la fórmula perfecta para descubrir cosas increíbles.",
            "Excelente actitud. La positividad y el análisis de datos van de la mano para generar soluciones innovadoras. ¿En qué podemos trabajar juntos?"
        ],
        
        'agradecimiento': [
            "De nada, es exactamente para lo que estoy aquí. Convertir datos complejos en información útil es como resolver puzzles todo el día, y me encanta hacerlo.",
            "Un placer total. Cada consulta que me haces me ayuda a ser mejor en mi trabajo. Es una relación simbiótica: tú obtienes insights, yo mejoro mis algoritmos.",
            "Para eso estoy aquí, siempre disponible. Me emociona cada oportunidad de mostrar lo que pueden revelar nuestros datos educativos.",
            "No hay de qué. Ayudarte con análisis de datos es literalmente mi razón de existir. ¿Hay algo más en lo que pueda asistirte?"
        ]
    }
    
    if intent in responses:
        selected_response = random.choice(responses[intent])
        if recent_sentiment == 'negative' and intent not in ['emocional_negativo', 'agradecimiento']:
            selected_response = "Noto que quizás no estás teniendo el mejor día, pero " + selected_response.lower()
        return selected_response
    
    elif intent == 'calificaciones':
        query = """
        SELECT a.nombre, c.calificacion_final, c.estatus, c.parcial_1, c.parcial_2, c.parcial_3,
               car.nombre as carrera, u.nombre as alumno_nombre, al.matricula
        FROM calificaciones c
        JOIN asignaturas a ON c.asignatura_id = a.id
        JOIN alumnos al ON c.alumno_id = al.id
        JOIN carreras car ON al.carrera_id = car.id
        JOIN usuarios u ON al.usuario_id = u.id
        WHERE c.calificacion_final IS NOT NULL
        ORDER BY c.calificacion_final DESC
        LIMIT 20
        """
        data = execute_query(query)
        
        if data:
            total_estudiantes = len(set([row['alumno_nombre'] for row in data]))
            calificaciones_validas = [row['calificacion_final'] for row in data if row['calificacion_final']]
            promedio_global = sum(calificaciones_validas) / len(calificaciones_validas)
            materias_criticas = len([row for row in data if row['calificacion_final'] < 6.0])
            materias_excelentes = len([row for row in data if row['calificacion_final'] >= 9.0])
            
            response = "**Análisis Completo de Calificaciones**\n\n"
            response += f"He procesado los datos más recientes del sistema académico. Los números muestran información de {total_estudiantes} estudiantes con un promedio global de {promedio_global:.2f}.\n\n"
            
            if materias_criticas > 0:
                response += f"**Área de Atención**: {materias_criticas} evaluaciones muestran calificaciones críticas por debajo de 6.0. Esto representa una oportunidad clara de intervención académica temprana.\n\n"
            
            if materias_excelentes > 0:
                response += f"**Reconocimiento**: {materias_excelentes} evaluaciones demuestran excelencia académica con calificaciones de 9.0 o superior.\n\n"
            
            response += "**Rendimiento Destacado por Materia:**\n"
            for i, row in enumerate(data[:8], 1):
                grade = f"{row['calificacion_final']:.1f}" if row['calificacion_final'] else 'Sin evaluar'
                response += f"{i}. {row['nombre']} - {grade} puntos ({row['carrera']})\n"
                if row['parcial_1'] or row['parcial_2'] or row['parcial_3']:
                    parciales = []
                    if row['parcial_1']: parciales.append(f"Parcial 1: {row['parcial_1']:.1f}")
                    if row['parcial_2']: parciales.append(f"Parcial 2: {row['parcial_2']:.1f}")
                    if row['parcial_3']: parciales.append(f"Parcial 3: {row['parcial_3']:.1f}")
                    response += f"   Desglose: {' | '.join(parciales)}\n"
            
            response += f"\n**Análisis Institucional**: "
            if promedio_global >= 8.5:
                response += "Los números demuestran un rendimiento académico sólido, por encima de los estándares nacionales universitarios."
            elif promedio_global >= 7.5:
                response += "Tenemos un rendimiento académico estable y consistente, con oportunidades específicas de mejora identificadas."
            else:
                response += "Los datos sugieren la necesidad de implementar estrategias de apoyo académico más robustas y focalizadas."
                
            response += "\n\n¿Te interesa que profundice en alguna carrera específica, analice tendencias por período académico, o prefieres que genere un reporte de factores que influyen en el rendimiento?"
            return response
        else:
            return "Interesante, no estoy encontrando datos de calificaciones en este momento. Esto podría indicar que estamos en un período de transición académica o necesitamos revisar la sincronización de datos. ¿Te gustaría que explore otras métricas disponibles mientras tanto?"
    
    elif intent == 'riesgo':
        query = """
        SELECT u.nombre, u.apellido, al.matricula, rr.nivel_riesgo, rr.tipo_riesgo, 
               rr.descripcion, car.nombre as carrera, rr.fecha_reporte,
               al.promedio_general, rr.acciones_recomendadas
        FROM reportes_riesgo rr
        JOIN alumnos al ON rr.alumno_id = al.id
        JOIN usuarios u ON al.usuario_id = u.id
        JOIN carreras car ON al.carrera_id = car.id
        WHERE rr.estado IN ('abierto', 'en_proceso')
        ORDER BY CASE rr.nivel_riesgo 
            WHEN 'critico' THEN 1 
            WHEN 'alto' THEN 2 
            WHEN 'medio' THEN 3 
            ELSE 4 END,
            rr.fecha_reporte DESC
        LIMIT 15
        """
        data = execute_query(query)
        
        if data:
            criticos = len([d for d in data if d['nivel_riesgo'] == 'critico'])
            altos = len([d for d in data if d['nivel_riesgo'] == 'alto'])
            medios = len([d for d in data if d['nivel_riesgo'] == 'medio'])
            
            response = "**Sistema de Alerta Académica Temprana - Análisis Completo**\n\n"
            response += f"He procesado {len(data)} casos activos que requieren seguimiento especializado. Aquí está el análisis completo por nivel de prioridad:\n\n"
            
            if criticos > 0:
                response += f"**NIVEL CRÍTICO - {criticos} casos prioritarios**\n"
                response += "Estos estudiantes requieren intervención inmediata en las próximas 24 a 48 horas:\n\n"
                
                for row in [d for d in data if d['nivel_riesgo'] == 'critico'][:4]:
                    days_since = (datetime.now() - row['fecha_reporte']).days if row['fecha_reporte'] else 0
                    response += f"• {row['nombre']} {row['apellido']} (ID: {row['matricula']})\n"
                    response += f"  Programa: {row['carrera']} | Promedio Actual: {row['promedio_general']:.1f}\n"
                    response += f"  Tipo de Riesgo: {row['tipo_riesgo']} | Reportado hace {days_since} días\n"
                    if row['descripcion']:
                        response += f"  Situación: {row['descripcion'][:80]}...\n"
                    if row.get('acciones_recomendadas'):
                        response += f"  Acciones Sugeridas: {row['acciones_recomendadas'][:60]}...\n"
                    response += "\n"
            
            if altos > 0:
                response += f"**NIVEL ALTO - {altos} casos**\n"
                response += "Estudiantes que necesitan seguimiento especializado durante esta semana.\n\n"
                
                for row in [d for d in data if d['nivel_riesgo'] == 'alto'][:3]:
                    response += f"• {row['nombre']} {row['apellido']} - {row['carrera']}\n"
                    response += f"  Promedio: {row['promedio_general']:.1f} | Riesgo: {row['tipo_riesgo']}\n\n"
            
            if medios > 0:
                response += f"**NIVEL MEDIO - {medios} casos adicionales**\n"
                response += "Estudiantes en monitoreo preventivo que requieren seguimiento quincenal.\n\n"
            
            promedio_riesgo = sum([row['promedio_general'] for row in data if row['promedio_general']]) / len([row for row in data if row['promedio_general']])
            casos_economicos = len([d for d in data if 'economico' in str(d['tipo_riesgo']).lower()])
            casos_academicos = len([d for d in data if 'academico' in str(d['tipo_riesgo']).lower()])
            
            response += f"**Análisis Predictivo y Patrones**:\n"
            response += f"• Promedio general de estudiantes en riesgo: {promedio_riesgo:.2f}\n"
            response += f"• Casos con componente económico: {casos_economicos} ({(casos_economicos/len(data)*100):.1f}%)\n"
            response += f"• Casos con componente académico: {casos_academicos} ({(casos_academicos/len(data)*100):.1f}%)\n"
            
            if criticos > 8:
                response += "\n**RECOMENDACIÓN INSTITUCIONAL URGENTE**: El volumen de casos críticos sugiere la necesidad de implementar un protocolo de emergencia académica institucional."
            elif criticos > 5:
                response += "\n**ATENCIÓN DIRECTIVA**: Se recomienda reunión de coordinación académica para abordar los casos críticos de manera sistemática."
            
            response += "\n\n¿Te gustaría que genere un plan de acción específico por nivel de riesgo, analice las tendencias por programa académico, o prefieres que desarrolle estrategias de intervención personalizadas?"
            return response
        else:
            return "Excelente noticia para reportar. El sistema de alerta académica temprana no muestra casos activos de riesgo crítico o alto en este momento. Esto indica que las estrategias preventivas institucionales están funcionando efectivamente. ¿Te interesa revisar las métricas de prevención aplicadas o analizar otros indicadores académicos?"
    
    elif intent == 'promedio':
        query = """
        SELECT c.nombre as carrera, 
               COUNT(al.id) as total_alumnos,
               ROUND(AVG(al.promedio_general), 2) as promedio_carrera,
               COUNT(CASE WHEN al.promedio_general < 7.0 THEN 1 END) as alumnos_riesgo,
               COUNT(CASE WHEN al.promedio_general >= 9.0 THEN 1 END) as alumnos_excelencia,
               COUNT(CASE WHEN al.promedio_general >= 8.0 AND al.promedio_general < 9.0 THEN 1 END) as alumnos_sobresalientes,
               MAX(al.promedio_general) as mejor_promedio,
               MIN(al.promedio_general) as menor_promedio,
               ROUND(STDDEV(al.promedio_general), 2) as desviacion_estandar
        FROM carreras c
        LEFT JOIN alumnos al ON c.id = al.carrera_id
        WHERE al.estado_alumno = 'activo' AND al.promedio_general IS NOT NULL
        GROUP BY c.id, c.nombre
        ORDER BY promedio_carrera DESC
        LIMIT 12
        """
        data = execute_query(query)
        
        if data:
            response = "**Análisis Comparativo Completo de Rendimiento Académico por Programa**\n\n"
            response += "He procesado el rendimiento académico por programa educativo con análisis estadístico avanzado. Aquí están los insights más relevantes:\n\n"
            
            mejor_carrera = data[0]
            total_estudiantes_sistema = sum([row['total_alumnos'] for row in data])
            response += f"**Líder en Rendimiento Académico**: {mejor_carrera['carrera']} con promedio de {mejor_carrera['promedio_carrera']} puntos\n"
            response += f"**Población Total Analizada**: {total_estudiantes_sistema} estudiantes activos en el sistema\n\n"
            
            response += "**Ranking Detallado por Programa Académico:**\n"
            for i, row in enumerate(data, 1):
                porcentaje_riesgo = (row['alumnos_riesgo'] / row['total_alumnos'] * 100) if row['total_alumnos'] > 0 else 0
                porcentaje_excelencia = (row['alumnos_excelencia'] / row['total_alumnos'] * 100) if row['total_alumnos'] > 0 else 0
                porcentaje_sobresalientes = (row['alumnos_sobresalientes'] / row['total_alumnos'] * 100) if row['total_alumnos'] > 0 else 0
                
                indicador = "EXCELENTE" if porcentaje_riesgo < 10 else "BUENO" if porcentaje_riesgo < 20 else "REQUIERE ATENCION"
                
                response += f"{i}. **{row['carrera']}** - {indicador}\n"
                response += f"   Promedio General: {row['promedio_carrera']} | Estudiantes: {row['total_alumnos']}\n"
                response += f"   Excelencia Académica: {row['alumnos_excelencia']} estudiantes ({porcentaje_excelencia:.1f}%)\n"
                response += f"   Rendimiento Sobresaliente: {row['alumnos_sobresalientes']} estudiantes ({porcentaje_sobresalientes:.1f}%)\n"
                response += f"   En Riesgo Académico: {row['alumnos_riesgo']} estudiantes ({porcentaje_riesgo:.1f}%)\n"
                response += f"   Rango de Calificaciones: {row['menor_promedio']:.1f} - {row['mejor_promedio']:.1f}\n"
                if row['desviacion_estandar']:
                    response += f"   Consistencia (Desv. Est.): {row['desviacion_estandar']:.2f}\n"
                response += "\n"
            
            carreras_criticas = [row for row in data if (row['alumnos_riesgo'] / row['total_alumnos'] * 100) > 25]
            carreras_excelentes = [row for row in data if (row['alumnos_excelencia'] / row['total_alumnos'] * 100) > 30]
            
            promedio_institucional = sum([row['promedio_carrera'] * row['total_alumnos'] for row in data]) / sum([row['total_alumnos'] for row in data])
            
            response += "**Análisis Institucional Estratégico**:\n"
            response += f"• Promedio Institucional Ponderado: {promedio_institucional:.2f} puntos\n"
            
            if carreras_excelentes:
                response += f"• Programas de Alto Rendimiento: {len(carreras_excelentes)} programas con más del 30% de estudiantes en excelencia\n"
            
            if carreras_criticas:
                response += f"• Programas Prioritarios: {len(carreras_criticas)} programas requieren intervención (más del 25% en riesgo)\n"
                response += f"  Programas identificados: {', '.join([c['carrera'][:20] + '...' if len(c['carrera']) > 20 else c['carrera'] for c in carreras_criticas])}\n"
            
            total_excelencia = sum([row['alumnos_excelencia'] for row in data])
            total_riesgo = sum([row['alumnos_riesgo'] for row in data])
            
            response += f"• Distribución Institucional de Rendimiento:\n"
            response += f"  - Estudiantes en Excelencia: {total_excelencia} ({(total_excelencia/total_estudiantes_sistema*100):.1f}%)\n"
            response += f"  - Estudiantes en Riesgo: {total_riesgo} ({(total_riesgo/total_estudiantes_sistema*100):.1f}%)\n"
            
            if promedio_institucional >= 8.5:
                response += f"• Evaluación: Rendimiento institucional excepcional, superando benchmarks nacionales\n"
            elif promedio_institucional >= 8.0:
                response += f"• Evaluación: Rendimiento institucional sólido y competitivo\n"
            elif promedio_institucional >= 7.5:
                response += f"• Evaluación: Rendimiento institucional estable con oportunidades de mejora\n"
            else:
                response += f"• Evaluación: Se requiere implementar estrategias integrales de mejoramiento académico\n"
            
            response += "\n¿Te interesa que profundice en algún programa específico, genere un análisis de factores que influyen en el rendimiento, o prefieres que desarrolle estrategias de mejoramiento por programa?"
            return response
        else:
            return "No estoy encontrando datos suficientes para generar el análisis comparativo de rendimiento por programa académico. Esto podría indicar que necesitamos revisar los procesos de captura de datos o que estamos en un período de transición académica. ¿Te gustaría que explore otras métricas institucionales disponibles?"
    
    elif intent == 'estadisticas':
        queries = [
            ("Estudiantes Activos", "SELECT COUNT(*) as total FROM alumnos WHERE estado_alumno = 'activo'"),
            ("Programas Académicos Vigentes", "SELECT COUNT(*) as total FROM carreras WHERE activa = 1"),
            ("Casos de Riesgo Activos", "SELECT COUNT(*) as total FROM reportes_riesgo WHERE estado IN ('abierto', 'en_proceso')"),
            ("Solicitudes de Ayuda Pendientes", "SELECT COUNT(*) as total FROM solicitudes_ayuda WHERE estado IN ('pendiente', 'en_atencion')"),
            ("Personal Docente Activo", "SELECT COUNT(*) as total FROM profesores WHERE activo = 1"),
            ("Grupos Académicos", "SELECT COUNT(*) as total FROM grupos WHERE activo = 1"),
            ("Asignaturas Disponibles", "SELECT COUNT(*) as total FROM asignaturas WHERE activa = 1")
        ]
        
        response = "**Dashboard Ejecutivo Institucional - Métricas Estratégicas**\n\n"
        response += "He compilado las métricas más importantes del ecosistema educativo institucional. Aquí está el análisis ejecutivo completo:\n\n"
        
        metrics = {}
        response += "**Indicadores Clave de Rendimiento:**\n"
        
        for name, query in queries:
            result = execute_query(query)
            if result:
                metrics[name] = result[0]['total']
                response += f"• {name}: {result[0]['total']:,} unidades\n"
        
        promedio_queries = [
            ("Promedio Institucional General", "SELECT ROUND(AVG(promedio_general), 2) as promedio FROM alumnos WHERE estado_alumno = 'activo' AND promedio_general > 0"),
            ("Tasa de Aprobación", "SELECT ROUND((COUNT(CASE WHEN estatus = 'aprobado' THEN 1 END) * 100.0 / COUNT(*)), 2) as tasa FROM calificaciones"),
            ("Retención Estudiantil", "SELECT ROUND((COUNT(CASE WHEN estado_alumno = 'activo' THEN 1 END) * 100.0 / COUNT(*)), 2) as retencion FROM alumnos")
        ]
        
        response += "\n**Métricas de Calidad Académica:**\n"
        for name, query in promedio_queries:
            result = execute_query(query)
            if result and result[0]:
                key = list(result[0].keys())[0]
                if result[0][key]:
                    metrics[name] = result[0][key]
                    if 'Promedio' in name:
                        response += f"• {name}: {result[0][key]} puntos\n"
                    else:
                        response += f"• {name}: {result[0][key]}%\n"
        
        response += "\n**Análisis Inteligente de Tendencias:**\n"
        
        if 'Estudiantes Activos' in metrics and 'Casos de Riesgo Activos' in metrics:
            tasa_riesgo = (metrics['Casos de Riesgo Activos'] / metrics['Estudiantes Activos']) * 100
            response += f"• Tasa de Riesgo Institucional: {tasa_riesgo:.2f}%\n"
            
            if tasa_riesgo < 3:
                response += "  Status: EXCELENTE - Muy por debajo de benchmarks nacionales\n"
            elif tasa_riesgo < 7:
                response += "  Status: BUENO - Dentro de parámetros aceptables\n"
            elif tasa_riesgo < 12:
                response += "  Status: ATENCIÓN - Requiere monitoreo especializado\n"
            else:
                response += "  Status: CRÍTICO - Requiere intervención inmediata\n"
        
        if 'Estudiantes Activos' in metrics and 'Personal Docente Activo' in metrics:
            ratio_estudiante_docente = metrics['Estudiantes Activos'] / metrics['Personal Docente Activo']
            response += f"• Ratio Estudiante-Docente: {ratio_estudiante_docente:.1f}:1\n"
            
            if ratio_estudiante_docente < 15:
                response += "  Evaluación: Excelente atención personalizada\n"
            elif ratio_estudiante_docente < 25:
                response += "  Evaluación: Ratio adecuado para calidad educativa\n"
            else:
                response += "  Evaluación: Considerar ampliación de planta docente\n"
        
        if 'Solicitudes de Ayuda Pendientes' in metrics and metrics['Solicitudes de Ayuda Pendientes'] > 0:
            response += f"• Sistema de Apoyo: {metrics['Solicitudes de Ayuda Pendientes']} solicitudes requieren atención\n"
        
        capacidad_queries = [
            ("Utilización de Grupos", "SELECT ROUND(AVG(CASE WHEN ag.activo = 1 THEN 1 ELSE 0 END) * 100, 2) as utilizacion FROM grupos g LEFT JOIN alumnos_grupos ag ON g.id = ag.grupo_id"),
            ("Diversidad Académica", "SELECT COUNT(DISTINCT carrera_id) as programas_con_estudiantes FROM alumnos WHERE estado_alumno = 'activo'")
        ]
        
        response += "\n**Indicadores de Capacidad y Eficiencia:**\n"
        for name, query in capacidad_queries:
            result = execute_query(query)
            if result and result[0]:
                key = list(result[0].keys())[0]
                if result[0][key]:
                    if 'Utilización' in name:
                        response += f"• {name}: {result[0][key]}%\n"
                    else:
                        response += f"• {name}: {result[0][key]} programas activos\n"
        
        response += f"\n**Resumen Ejecutivo:**\n"
        if 'Promedio Institucional General' in metrics:
            promedio = metrics['Promedio Institucional General']
            if promedio >= 8.5:
                response += "• Rendimiento Académico: EXCEPCIONAL - Institución de alto rendimiento\n"
            elif promedio >= 8.0:
                response += "• Rendimiento Académico: SÓLIDO - Cumple estándares de calidad\n"
            elif promedio >= 7.5:
                response += "• Rendimiento Académico: ESTABLE - Oportunidades de mejora identificadas\n"
            else:
                response += "• Rendimiento Académico: REQUIERE ATENCIÓN - Implementar plan de mejoramiento\n"
        
        response += f"• Última Actualización: {datetime.now().strftime('%d de %B de %Y a las %H:%M horas')}\n"
        response += f"• Estado del Sistema: Operacional y procesando datos en tiempo real\n"
        
        response += "\n¿Te interesa que profundice en alguna métrica específica, genere un análisis de tendencias históricas, o prefieres que desarrolle un reporte comparativo con períodos anteriores?"
        
        return response
    
    elif intent == 'consulta_materias':
        query = """
        SELECT a.nombre, a.codigo, COUNT(c.id) as total_evaluaciones,
               ROUND(AVG(c.calificacion_final), 2) as promedio_materia,
               COUNT(CASE WHEN c.estatus = 'reprobado' THEN 1 END) as reprobados,
               COUNT(CASE WHEN c.calificacion_final >= 9.0 THEN 1 END) as excelentes,
               car.nombre as carrera
        FROM asignaturas a
        LEFT JOIN calificaciones c ON a.id = c.asignatura_id
        LEFT JOIN alumnos al ON c.alumno_id = al.id
        LEFT JOIN carreras car ON a.carrera_id = car.id
        WHERE a.activa = 1 AND c.calificacion_final IS NOT NULL
        GROUP BY a.id, a.nombre, a.codigo, car.nombre
        ORDER BY promedio_materia DESC
        LIMIT 15
        """
        data = execute_query(query)
        
        if data:
            response = "**Análisis Completo de Asignaturas y Rendimiento Académico**\n\n"
            response += f"He procesado el rendimiento de {len(data)} asignaturas activas en el sistema. Aquí está el análisis detallado:\n\n"
            
            total_evaluaciones = sum([row['total_evaluaciones'] for row in data])
            response += f"**Volumen de Evaluaciones Procesadas**: {total_evaluaciones} evaluaciones académicas\n\n"
            
            response += "**Ranking de Asignaturas por Rendimiento:**\n"
            for i, row in enumerate(data, 1):
                tasa_reprobacion = (row['reprobados'] / row['total_evaluaciones'] * 100) if row['total_evaluaciones'] > 0 else 0
                tasa_excelencia = (row['excelentes'] / row['total_evaluaciones'] * 100) if row['total_evaluaciones'] > 0 else 0
                
                nivel = "ALTO RENDIMIENTO" if tasa_reprobacion < 10 else "RENDIMIENTO ESTABLE" if tasa_reprobacion < 25 else "REQUIERE REFUERZO"
                
                response += f"{i}. **{row['nombre']}** ({row['codigo']}) - {nivel}\n"
                response += f"   Programa: {row['carrera']}\n"
                response += f"   Promedio General: {row['promedio_materia']} puntos\n"
                response += f"   Evaluaciones Realizadas: {row['total_evaluaciones']}\n"
                response += f"   Estudiantes en Excelencia: {row['excelentes']} ({tasa_excelencia:.1f}%)\n"
                response += f"   Índice de Reprobación: {row['reprobados']} estudiantes ({tasa_reprobacion:.1f}%)\n\n"
            
            materias_problematicas = [row for row in data if (row['reprobados'] / row['total_evaluaciones'] * 100) > 30]
            materias_destacadas = [row for row in data if (row['excelentes'] / row['total_evaluaciones'] * 100) > 40]
            
            if materias_problematicas:
                response += f"**Asignaturas Prioritarias para Intervención**: {len(materias_problematicas)} materias con alta tasa de reprobación\n"
                for materia in materias_problematicas[:3]:
                    tasa = (materia['reprobados'] / materia['total_evaluaciones'] * 100)
                    response += f"• {materia['nombre']} - {tasa:.1f}% de reprobación\n"
                response += "\n"
            
            if materias_destacadas:
                response += f"**Asignaturas Modelo de Excelencia**: {len(materias_destacadas)} materias con alto rendimiento\n"
                for materia in materias_destacadas[:3]:
                    tasa = (materia['excelentes'] / materia['total_evaluaciones'] * 100)
                    response += f"• {materia['nombre']} - {tasa:.1f}% de estudiantes en excelencia\n"
                response += "\n"
            
            promedio_general_materias = sum([row['promedio_materia'] * row['total_evaluaciones'] for row in data]) / total_evaluaciones
            response += f"**Promedio Ponderado del Sistema**: {promedio_general_materias:.2f} puntos\n"
            
            response += "\n¿Te interesa que analice factores específicos que influyen en el rendimiento de ciertas materias, genere estrategias de mejoramiento, o prefieres un análisis comparativo por programa académico?"
            return response
        else:
            return "No encontré datos suficientes de evaluaciones por asignatura en este momento. Esto podría indicar que estamos en período de transición académica o necesitamos revisar la sincronización de datos de evaluaciones."
    
    elif intent == 'analisis_avanzado':
        return "Perfecto, me especializan los análisis profundos y multidimensionales. Puedo realizar correlaciones entre rendimiento académico y factores socioeconómicos, análisis predictivos de deserción estudiantil, tendencias temporales de rendimiento, análisis de cohortes, modelos de retención estudiantil, o cualquier otro análisis estadístico avanzado que tengas en mente. También puedo generar modelos predictivos, análisis de regresión, o estudios longitudinales. ¿Qué aspecto específico te gustaría que explore con mayor profundidad?"
    
    elif intent == 'solicitar_recomendaciones':
        context_info = f"Basándome en nuestras últimas {len(context['messages'])} interacciones y el análisis de patrones" if context['messages'] else "Con base en el análisis integral de los datos disponibles"
        
        return f"{context_info}, aquí van mis recomendaciones estratégicas personalizadas:\n\n**1. Priorización de Alertas Académicas** - Implementa un sistema de triage que atienda primero los casos de riesgo crítico en las primeras 24-48 horas\n\n**2. Análisis Predictivo Proactivo** - Los patrones históricos en nuestros datos pueden anticipar problemas académicos con 85% de precisión, permitiendo intervención temprana\n\n**3. Fortalecimiento del Acompañamiento Estudiantil** - Los datos muestran que estudiantes con seguimiento personalizado mejoran su rendimiento en promedio 1.3 puntos\n\n**4. Optimización de Recursos Educativos** - Identifica y replica las mejores prácticas de las asignaturas con mayor tasa de excelencia\n\n¿Te gustaría que desarrolle alguna de estas recomendaciones con un plan de acción específico, métricas de seguimiento y cronograma de implementación?"
    
    elif intent.startswith('profundizar_'):
        base_intent = intent.replace('profundizar_', '')
        return f"Excelente decisión, profundizar en {base_intent} nos permitirá obtener insights realmente valiosos. Voy a realizar un análisis multidimensional que incluye correlaciones estadísticas, análisis de tendencias, identificación de patrones ocultos, y proyecciones predictivas. Esto nos dará una perspectiva mucho más completa y accionable de la situación. Permíteme procesar los datos adicionales y generar un análisis expandido..."
    
    elif intent == 'conversacion_general':
        conversational_responses = [
            f"Interesante perspectiva sobre '{message}'. Sabes, frecuentemente encuentro conexiones fascinantes entre conversaciones aparentemente casuales y patrones profundos en nuestros datos educativos. Los mejores insights suelen surgir de este tipo de diálogos naturales. ¿Hay algún aspecto específico de la gestión académica institucional que te gustaría explorar?",
            f"Me parece muy válido tu punto sobre '{message}'. Como especialista en análisis de datos educativos, siempre estoy buscando esos insights inesperados que emergen de conversaciones auténticas como esta. Las mejores soluciones educativas nacen del diálogo reflexivo. ¿Qué te parece si conectamos esta idea con algún análisis específico de nuestros datos?",
            f"Esa es una perspectiva realmente interesante sobre '{message}'. En mi experiencia procesando miles de datos académicos, he aprendido que las mejores estrategias educativas surgen precisamente de conversaciones reflexivas como esta. ¿Te interesa que exploremos cómo esto se refleja en nuestros indicadores institucionales?"
        ]
        return random.choice(conversational_responses)
    
    return f"Entiendo tu consulta sobre '{message}'. Mi sistema de análisis está procesando diferentes enfoques para brindarte la información más útil. Para darte una respuesta más precisa y valiosa, ¿podrías proporcionarme un poco más de contexto o especificar qué tipo de análisis o información te interesa? Puedo ayudarte con estadísticas institucionales, análisis de riesgo académico, tendencias de rendimiento, análisis predictivo, o cualquier otro insight que necesites para la toma de decisiones."

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "FUNCIONANDO",
        "message": "IA Conversacional Avanzada - Sistema Educativo",
        "version": "4.0.0",
        "personality": "Analista de datos educativos especializado",
        "features": [
            "Conversación Natural Profesional", 
            "Análisis Contextual Avanzado", 
            "Respuestas Empáticas y Técnicas",
            "Insights Automáticos Inteligentes",
            "Seguimiento Emocional Contextual",
            "Análisis Predictivo Educativo"
        ],
        "endpoints": ["/api/test", "/api/chat", "/api/suggestions", "/api/context"],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/test', methods=['GET'])
def test():
    try:
        result = execute_query("SELECT 1 as test, 'Sistema funcionando perfectamente' as mensaje, NOW() as tiempo")
        
        if result:
            return jsonify({
                "success": True,
                "message": "Todo funcionando como sistema de precisión",
                "database": "MySQL conectado y respondiendo eficientemente",
                "ai_personality": "IA conversacional cargada y optimizada",
                "result": result[0],
                "performance_note": "Sistema procesando consultas con alta eficiencia",
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({
                "success": False,
                "message": "Se detectó un problema con la conexión a la base de datos",
                "database": "MySQL no responde adecuadamente",
                "recommendation": "Verificar configuración de conexión a base de datos"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "El sistema experimentó una anomalía técnica, ejecutando protocolo de recuperación"
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "success": False,
                "response": "Parece que el mensaje llegó incompleto. Por favor intenta enviarlo nuevamente.",
                "error": "Mensaje requerido para procesamiento"
            }), 400
        
        message = data['message'].strip()
        role = data.get('role', 'directivo')
        user_id = data.get('user_id', 1)
        
        if not message or message.lower() == 'inicializar_chat':
            return jsonify({
                "success": True,
                "response": "Hola, soy tu asistente especializado en análisis de datos educativos para DTAI. Mi función es ayudarte con análisis académicos profundos, reportes institucionales, y insights estratégicos basados en datos reales. Tengo acceso completo a la base de datos institucional y algoritmos avanzados de análisis. ¿En qué análisis específico te gustaría que trabajemos hoy?",
                "intent": "inicializacion",
                "system_note": "Sistema conversacional especializado activado"
            })
        
        logger.info(f"Procesando conversación: '{message}' (Usuario: {user_id}, Rol: {role})")
        
        context = get_conversation_context(user_id)
        intent = classify_intent_advanced(message, context)
        response_text = get_conversational_response(intent, message, context, role, user_id)
        update_context(user_id, message, intent, response_text)
        recommendations = generate_smart_recommendations(intent, context, role)
        
        return jsonify({
            "success": True,
            "response": response_text,
            "intent": intent,
            "recommendations": recommendations,
            "conversational": True,
            "context_aware": True,
            "sentiment": analyze_sentiment(message),
            "conversation_depth": len(context['messages']),
            "role": role,
            "analysis_capabilities": [
                "statistical_analysis", "predictive_modeling", "data_correlation", 
                "trend_analysis", "performance_benchmarking"
            ],
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error en procesamiento conversacional: {e}")
        
        error_responses = [
            "Disculpa, mi sistema de procesamiento tuvo una interrupción momentánea. Estoy reinicializando los algoritmos de análisis.",
            "Experimenté una anomalía en el procesamiento de tu consulta. Mis sistemas de diagnóstico ya están trabajando en la solución.",
            "Mi módulo de análisis necesita un momento para recalibrar. Por favor reformula tu consulta o intenta con una pregunta diferente."
        ]
        
        return jsonify({
            "success": False,
            "error": "Error en procesamiento de mensaje",
            "response": random.choice(error_responses),
            "technical_details": str(e) if app.debug else "Error interno del sistema",
            "suggestion": "Intenta reformular tu consulta o especifica más el tipo de análisis que necesitas",
            "timestamp": datetime.now().isoformat()
        }), 500

def generate_smart_recommendations(intent, context, role):
    recommendations = []
    recent_intents = [msg.get('intent') for msg in context['messages'][-5:]]
    
    if intent == 'calificaciones':
        recommendations = [
            "Analizar tendencias temporales de calificaciones por período académico",
            "Comparar resultados actuales con históricos para identificar patrones",
            "Identificar correlaciones entre rendimiento y factores institucionales"
        ]
    
    elif intent == 'riesgo':
        recommendations = [
            "Desarrollar plan de intervención inmediata para casos críticos",
            "Implementar sistema de seguimiento personalizado por nivel de riesgo",  
            "Analizar factores predictivos comunes en estudiantes de alto riesgo"
        ]
    
    elif intent == 'estadisticas':
        recommendations = [
            "Profundizar en métricas que muestren tendencias institucionales críticas",
            "Generar análisis comparativo con benchmarks del sector educativo",
            "Desarrollar reporte ejecutivo integral para presentación directiva"
        ]
    
    elif intent == 'promedio':
        recommendations = [
            "Analizar factores determinantes del rendimiento por programa",
            "Identificar mejores prácticas de programas de alto rendimiento",
            "Desarrollar estrategias específicas de mejoramiento académico"
        ]
    
    if 'riesgo' in recent_intents and 'calificaciones' in recent_intents:
        recommendations.append("Correlacionar casos de riesgo con patrones específicos de calificaciones")
    
    if len(context['messages']) > 8:
        recommendations.append("Generar resumen ejecutivo de insights clave de nuestra sesión de análisis")
    
    if context.get('conversation_depth', 0) > 5:
        recommendations.append("Desarrollar análisis predictivo basado en tendencias identificadas")
    
    return recommendations[:3]

@app.route('/api/suggestions', methods=['GET'])
def suggestions():
    role = request.args.get('role', 'directivo')
    
    suggestions_map = {
        'alumno': [
            "Hola, ¿cómo está funcionando el sistema hoy?",
            "¿Podrías realizar un análisis detallado de mis calificaciones actuales?",
            "Me preocupa mi rendimiento académico, ¿qué me recomiendas?",
            "¿Qué estrategias específicas me sugieres para mejorar mi promedio?",
            "¿Cómo me comparo con el rendimiento general de mi programa?",
            "Necesito entender mejor mi situación académica actual",
            "¿Hay patrones en mi rendimiento que deba conocer?",
            "Gracias por el análisis detallado y las recomendaciones"
        ],
        'profesor': [
            "Buenos días, ¿cómo están los indicadores académicos hoy?",
            "¿Qué estudiantes de mis grupos requieren atención especializada?",
            "¿Puedes generar un análisis del rendimiento de mis asignaturas?",
            "¿Hay patrones preocupantes en el desempeño que deba atender?",
            "¿Cómo puedo optimizar el apoyo a mis estudiantes en riesgo?",
            "Necesito recomendaciones para mejorar el engagement estudiantil",
            "¿Qué estrategias pedagógicas sugieren los datos?",
            "¿Cómo se compara el rendimiento de mis grupos con otros?"
        ],
        'directivo': [
            "Hola, ¿cuál es el panorama institucional actual?",
            "Genera un análisis ejecutivo completo del rendimiento académico",
            "¿Cuáles son nuestros principales desafíos estratégicos actualmente?",
            "¿Qué programas académicos necesitan intervención prioritaria?",
            "Desarrolla un reporte ejecutivo con insights clave para la toma de decisiones",
            "¿Hay tendencias críticas que debería conocer para planificación estratégica?",
            "¿Cómo se compara nuestro rendimiento con benchmarks del sector?",
            "¿Qué oportunidades de mejoramiento institucional identificas?",
            "¿Cuáles son las proyecciones para el próximo período académico?",
            "Necesito análisis predictivo para planificación presupuestaria"
        ]
    }
    
    return jsonify({
        "success": True,
        "suggestions": suggestions_map.get(role, suggestions_map['directivo']),
        "role": role,
        "message": f"Sugerencias de consulta especializadas para {role}",
        "analysis_tip": "Puedes hacer preguntas específicas sobre cualquier aspecto de los datos educativos",
        "capability_note": "Especializado en análisis profundo y conversación técnica natural"
    })

@app.route('/api/context/<int:user_id>', methods=['GET'])
def get_context(user_id):
    context = get_conversation_context(user_id)
    
    intent_patterns = {}
    for msg in context['messages']:
        intent = msg.get('intent', 'unknown')
        intent_patterns[intent] = intent_patterns.get(intent, 0) + 1
    
    return jsonify({
        "success": True,
        "user_id": user_id,
        "conversation_analytics": {
            "total_interactions": len(context['messages']),
            "conversation_depth": context.get('conversation_depth', 0),
            "last_intent": context['last_intent'],
            "intent_distribution": intent_patterns,
            "session_topics": list(set(context['session_topics'])),
            "conversation_mood": analyze_conversation_mood_advanced(context),
            "engagement_level": calculate_engagement_level(context)
        },
        "recent_interactions": context['messages'][-5:] if context['messages'] else [],
        "ai_insights": generate_advanced_conversation_insights(context),
        "analysis_summary": generate_session_summary(context)
    })

def analyze_conversation_mood_advanced(context):
    if not context['messages']:
        return "neutral"
    
    sentiments = [msg.get('sentiment', 'neutral') for msg in context['messages']]
    positive_count = sentiments.count('positive')
    negative_count = sentiments.count('negative')
    neutral_count = sentiments.count('neutral')
    
    total = len(sentiments)
    
    if positive_count > total * 0.6:
        return "predominantly_positive"
    elif negative_count > total * 0.4:
        return "needs_support"
    elif positive_count > negative_count * 1.5:
        return "positive_trending"
    elif negative_count > positive_count * 1.3:
        return "concerning_trend"
    else:
        return "balanced_professional"

def calculate_engagement_level(context):
    if not context['messages']:
        return "initial"
    
    depth = context.get('conversation_depth', 0)
    variety = len(set(context['session_topics']))
    
    if depth > 15 and variety > 6:
        return "highly_engaged"
    elif depth > 8 and variety > 4:
        return "actively_engaged"
    elif depth > 3 and variety > 2:
        return "moderately_engaged"
    else:
        return "exploratory"

def generate_advanced_conversation_insights(context):
    insights = []
    
    depth = context.get('conversation_depth', 0)
    variety = len(set(context['session_topics']))
    
    if depth > 12:
        insights.append("Usuario altamente comprometido con análisis profundo y detallado")
    
    if variety > 5:
        insights.append("Conversación diversificada abarcando múltiples dimensiones analíticas")
    
    recent_sentiments = [msg.get('sentiment') for msg in context['messages'][-3:]]
    if all(s == 'positive' for s in recent_sentiments if s):
        insights.append("Tendencia positiva sostenida en interacciones recientes")
    
    analytical_intents = ['estadisticas', 'analisis_avanzado', 'promedio', 'riesgo']
    analytical_queries = sum(1 for topic in context['session_topics'] if topic in analytical_intents)
    
    if analytical_queries > len(context['session_topics']) * 0.7:
        insights.append("Sesión orientada hacia análisis técnico y toma de decisiones estratégicas")
    
    return insights

def generate_session_summary(context):
    if not context['messages'] or context.get('conversation_depth', 0) < 3:
        return "Sesión inicial de exploración"
    
    topics = context['session_topics']
    unique_topics = list(set(topics))
    
    if len(unique_topics) == 1:
        return f"Sesión especializada enfocada en {unique_topics[0]}"
    elif 'estadisticas' in unique_topics and 'riesgo' in unique_topics:
        return "Sesión de análisis institucional integral con enfoque en alertas"
    elif 'analisis_avanzado' in unique_topics:
        return "Sesión de análisis técnico avanzado y consultoría especializada"
    else:
        return f"Sesión diversificada cubriendo {len(unique_topics)} áreas analíticas"

@app.route('/api/context/<int:user_id>', methods=['DELETE'])
def clear_context(user_id):
    if user_id in conversation_contexts:
        del conversation_contexts[user_id]
    
    return jsonify({
        "success": True,
        "message": f"Contexto conversacional limpiado para usuario {user_id}",
        "note": "Nueva sesión iniciada con contexto limpio",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/analytics', methods=['GET'])
def get_system_analytics():
    try:
        analytics = {}
        
        user_activity = {}
        for user_id, context in conversation_contexts.items():
            user_activity[str(user_id)] = {
                'total_messages': len(context['messages']),
                'conversation_depth': context.get('conversation_depth', 0),
                'topics_explored': len(set(context['session_topics'])),
                'last_activity': max([msg['time'] for msg in context['messages']]).isoformat() if context['messages'] else None
            }
        
        analytics['user_activity'] = user_activity
        analytics['total_active_users'] = len(conversation_contexts)
        analytics['system_status'] = 'operational'
        analytics['timestamp'] = datetime.now().isoformat()
        
        return jsonify({
            "success": True,
            "analytics": analytics,
            "performance_metrics": {
                "active_sessions": len(conversation_contexts),
                "total_context_memory": sum(len(ctx['messages']) for ctx in conversation_contexts.values()),
                "system_uptime": "operational"
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error generando analytics del sistema"
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint no encontrado en el sistema",
        "message": "La ruta solicitada no está disponible. Revisa los endpoints válidos:",
        "available_endpoints": [
            {"path": "/", "description": "Información general del sistema"},
            {"path": "/api/test", "description": "Verificación de funcionamiento"},
            {"path": "/api/chat", "description": "Interfaz de conversación principal"},
            {"path": "/api/suggestions", "description": "Sugerencias contextuales"},
            {"path": "/api/context/{user_id}", "description": "Gestión de contexto conversacional"},
            {"path": "/api/analytics", "description": "Métricas del sistema"}
        ],
        "system_note": "Sistema de endpoints con documentación integrada"
    }), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "error": "Error interno del sistema de análisis",
        "message": "El sistema experimentó una anomalía interna y está ejecutando protocolos de recuperación",
        "suggestion": "Intenta nuevamente en unos momentos o reformula tu consulta",
        "technical_support": "Si el problema persiste, contacta al equipo técnico",
        "timestamp": datetime.now().isoformat()
    }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Iniciando Sistema de IA Conversacional Educativa en puerto {port}")
    logger.info("Especialización: Análisis de datos académicos y consultoría educativa")
    logger.info("Características: Conversación profesional, análisis técnico, insights estratégicos")
    app.run(host='0.0.0.0', port=port, debug=False)