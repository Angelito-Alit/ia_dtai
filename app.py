from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
import mysql.connector
from datetime import datetime
import random

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear aplicación Flask
app = Flask(__name__)
CORS(app)

# Contexto de conversación
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
    """Crear conexión a BD"""
    try:
        config = get_db_config()
        connection = mysql.connector.connect(**config)
        logger.info("Conexión a BD exitosa")
        return connection
    except Exception as e:
        logger.error(f" Error BD: {e}")
        return None

def execute_query(query, params=None):
    """Ejecutar consulta"""
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or [])
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        logger.info(f" Query ejecutada: {len(result)} filas")
        return result
    except Exception as e:
        logger.error(f" Error query: {e}")
        if connection:
            connection.close()
        return None

def get_conversation_context(user_id):
    if user_id not in conversation_contexts:
        conversation_contexts[user_id] = {
            'messages': [],
            'last_intent': None
        }
    return conversation_contexts[user_id]

def update_context(user_id, message, intent, response):
    context = get_conversation_context(user_id)
    context['messages'].append({
        'user': message,
        'bot': response[:100],
        'intent': intent,
        'time': datetime.now()
    })
    context['last_intent'] = intent
    
    if len(context['messages']) > 5:
        context['messages'] = context['messages'][-5:]

def classify_intent(message, context):
    """Clasificador conversacional mejorado"""
    msg = message.lower().strip()
    
    # Remover signos de puntuación para mejor análisis
    import re
    msg_clean = re.sub(r'[^\w\s]', '', msg)
    
    # Saludos - más específico
    saludo_patterns = ['hola', 'hello', 'hi', 'hey', 'buenas', 'buenos dias', 'buenas tardes', 'buenas noches']
    if any(pattern in msg_clean for pattern in saludo_patterns):
        return 'saludo'
    
    # Despedidas - más específico
    despedida_patterns = ['adios', 'adiós', 'bye', 'hasta luego', 'nos vemos', 'chao', 'goodbye', 'hasta la vista']
    if any(pattern in msg_clean for pattern in despedida_patterns):
        return 'despedida'
    
    # Agradecimientos
    if any(w in msg for w in ['gracias', 'thank you', 'te lo agradezco', 'muchas gracias']):
        return 'agradecimiento'
    
    # Estados emocionales
    if any(w in msg for w in ['triste', 'deprimido', 'mal', 'terrible', 'horrible', 'preocupado']):
        return 'emocional_negativo'
    
    if any(w in msg for w in ['feliz', 'contento', 'bien', 'genial', 'excelente', 'perfecto']):
        return 'emocional_positivo'
    
    # Preguntas sobre la IA
    if any(pattern in msg for pattern in ['como estas', 'que tal', 'como te va', 'how are you']):
        return 'pregunta_estado'
    
    if any(pattern in msg for pattern in ['quien eres', 'que eres', 'who are you', 'que puedes hacer']):
        return 'pregunta_identidad'
    
    # Consultas académicas - más específicas
    if any(w in msg for w in ['calificaciones', 'notas', 'puntuaciones', 'resultados', 'evaluaciones']):
        return 'calificaciones'
    
    if any(w in msg for w in ['riesgo', 'problema', 'dificultad', 'ayuda', 'atencion']):
        return 'riesgo'
    
    if any(w in msg for w in ['promedio', 'carrera', 'rendimiento', 'desempeño']):
        return 'promedio'
    
    if any(w in msg for w in ['estadisticas', 'resumen', 'general', 'números', 'datos']):
        return 'estadisticas'
    
    # Afirmaciones/Negaciones contextuales
    if context.get('last_intent'):
        if any(w in msg for w in ['sí', 'si', 'claro', 'ok', 'está bien', 'de acuerdo', 'perfecto']):
            return 'afirmacion'
        
        if any(w in msg for w in ['no', 'nada', 'mejor no', 'no gracias']):
            return 'negacion'
    
    # Si no coincide con nada específico
    return 'conversacion_general'

def get_conversational_response(intent, message, context, role='alumno', user_id=1):
    """Generar respuesta conversacional mejorada"""
    
    # Respuestas más naturales y variadas
    responses = {
        'saludo': [
            "¡Hola!  Me alegra verte. ¿En qué puedo ayudarte hoy?",
            "¡Hola!  ¿Cómo estás? Soy tu asistente virtual académico.",
            "¡Hey!  ¿Qué tal? ¿En qué te puedo asistir?",
            "¡Buenos días! ¿En qué puedo ayudarte?"
        ],
        
        'despedida': [
            "¡Hasta luego! Que tengas un excelente día.",
            "¡Nos vemos!  Aquí estaré cuando me necesites.",
            "¡Adiós!  Fue un placer ayudarte.",
            "¡Bye!  ¡Que todo te vaya muy bien!"
        ],
        
        'pregunta_estado': [
            "¡Muy bien, gracias por preguntar!  ¿Y tú cómo estás?",
            "¡Excelente! Funcionando perfectamente y listo para ayudarte. ¿Qué necesitas?",
            "¡Genial! Siempre contento de poder ayudar. ¿En qué te apoyo?"
        ],
        
        'pregunta_identidad': [
            "Soy tu asistente virtual académico . Puedo ayudarte con información sobre estudiantes, profesores, calificaciones y estadísticas del sistema.",
            "¡Hola! Soy una IA especializada en educación. Estoy conectado a la base de datos para darte información actualizada.",
            "Soy tu compañero digital para consultas académicas 📚. ¿Qué te gustaría saber?"
        ],
        
        'emocional_negativo': [
            "Lo siento que te sientas así . ¿Hay algo específico que te preocupa? Tal vez pueda ayudarte.",
            "Entiendo que puede ser frustrante . Estoy aquí para apoyarte. ¿En qué puedo ayudarte?",
            "Siento que estés pasando por un momento difícil 🫂. ¿Quieres que revisemos algo específico?"
        ],
        
        'emocional_positivo': [
            "¡Me alegra escuchar eso!  ¿En qué más puedo ayudarte?",
            "¡Qué bueno!  Me encanta ver esa actitud positiva.",
            "¡Excelente!  ¿Hay algo más en lo que te pueda asistir?"
        ],
        
        'agradecimiento': [
            "¡De nada! 😊 Para eso estoy aquí.",
            "¡Un placer ayudarte! 🤗 ¿Necesitas algo más?",
            "¡Siempre es un gusto! "
        ],
        
        'afirmacion': [
            "¡Perfecto!  ¿En qué más te puedo ayudar?",
            "¡Genial!  ¿Algo más que necesites?",
            "¡Excelente! ¿Qué más quieres saber?"
        ],
        
        'negacion': [
            "Entiendo . ¿Hay algo más en lo que te pueda ayudar?",
            "Sin problema . ¿Alguna otra consulta?",
            "Está bien . ¿Necesitas algo diferente?"
        ]
    }
    
    # Evitar repetir la misma respuesta
    if intent in responses:
        # Filtrar respuestas ya usadas recientemente
        used_responses = [msg['bot'] for msg in context.get('messages', [])[-3:] if 'bot' in msg]
        available_responses = [r for r in responses[intent] if not any(r in used for used in used_responses)]
        
        # Si todas las respuestas fueron usadas, usar cualquiera
        if not available_responses:
            available_responses = responses[intent]
        
        return random.choice(available_responses)
    
    # Consultas académicas con datos REALES de BD
    elif intent == 'calificaciones':
        query = """
        SELECT a.nombre, c.calificacion_final, c.estatus, c.parcial_1, c.parcial_2, c.parcial_3
        FROM calificaciones c
        JOIN asignaturas a ON c.asignatura_id = a.id
        JOIN alumnos al ON c.alumno_id = al.id
        WHERE al.usuario_id = %s
        ORDER BY a.nombre
        LIMIT 10
        """
        data = execute_query(query, [user_id])
        
        if data:
            response = " **Aquí tienes tus calificaciones:**\n\n"
            total_promedio = 0
            materias_count = 0
            materias_riesgo = 0
            
            for row in data:
                if row['calificacion_final']:
                    total_promedio += row['calificacion_final']
                    materias_count += 1
                    if row['calificacion_final'] < 7.0:
                        materias_riesgo += 1
                
                status = "✅" if row['estatus'] == 'aprobado' else "📝" if row['estatus'] == 'cursando' else "❌"
                grade = f"{row['calificacion_final']:.1f}" if row['calificacion_final'] else 'Sin calificar'
                response += f"{status} **{row['nombre']}**: {grade}\n"
                
                # Mostrar parciales si están disponibles
                if row['parcial_1'] or row['parcial_2'] or row['parcial_3']:
                    parciales = []
                    if row['parcial_1']: parciales.append(f"P1: {row['parcial_1']:.1f}")
                    if row['parcial_2']: parciales.append(f"P2: {row['parcial_2']:.1f}")
                    if row['parcial_3']: parciales.append(f"P3: {row['parcial_3']:.1f}")
                    response += f"    {' | '.join(parciales)}\n"
                response += "\n"
            
            if materias_count > 0:
                promedio_actual = total_promedio / materias_count
                response += f" **Tu promedio actual**: {promedio_actual:.2f}\n\n"
                
                if promedio_actual >= 9.0:
                    response += "🌟 ¡Excelente trabajo! Sigues por muy buen camino."
                elif promedio_actual >= 8.0:
                    response += "👍 ¡Muy bien! Tu rendimiento es bueno."
                elif promedio_actual >= 7.0:
                    response += "💪 Vas bien, pero hay espacio para mejorar."
                else:
                    response += "⚠️ Necesitas enfocarte más en tus estudios."
                
                if materias_riesgo > 0:
                    response += f"\n Tienes {materias_riesgo} materia(s) por debajo de 7.0"
            
            response += "\n\n ¿Te gustaría ver estrategias para mejorar en alguna materia específica?"
            return response
        else:
            return " No encontré calificaciones registradas para ti. ¿Es tu primer cuatrimestre? Si crees que es un error, puedes contactar a tu coordinador académico. 😊"
    
    elif intent == 'riesgo':
        query = """
        SELECT u.nombre, u.apellido, al.matricula, rr.nivel_riesgo, rr.tipo_riesgo, rr.descripcion, car.nombre as carrera
        FROM reportes_riesgo rr
        JOIN alumnos al ON rr.alumno_id = al.id
        JOIN usuarios u ON al.usuario_id = u.id
        JOIN carreras car ON al.carrera_id = car.id
        WHERE rr.estado IN ('abierto', 'en_proceso')
        ORDER BY CASE rr.nivel_riesgo 
            WHEN 'critico' THEN 1 
            WHEN 'alto' THEN 2 
            WHEN 'medio' THEN 3 
            ELSE 4 END
        LIMIT 10
        """
        data = execute_query(query)
        
        if data:
            criticos = len([d for d in data if d['nivel_riesgo'] == 'critico'])
            response = f" **Alumnos que necesitan atención** ({len(data)} casos activos):\n\n"
            
            for row in data:
                emoji = "🔴" if row['nivel_riesgo'] == 'critico' else "🟡" if row['nivel_riesgo'] == 'alto' else "🟠"
                response += f"{emoji} **{row['nombre']} {row['apellido']}** ({row['matricula']})\n"
                response += f"   Carrera: {row['carrera']}\n"
                response += f"   Riesgo: {row['nivel_riesgo']} ({row['tipo_riesgo']})\n"
                if row['descripcion']:
                    response += f"    {row['descripcion'][:80]}...\n"
                response += "\n"
            
            if criticos > 0:
                response += f" **ATENCIÓN URGENTE**: {criticos} estudiantes en riesgo crítico requieren intervención inmediata.\n\n"
                response += " **Recomendaciones**:\n"
                response += "• Contactar a padres/tutores hoy mismo\n"
                response += "• Programar citas individuales esta semana\n"
                response += "• Evaluar apoyos adicionales (económicos, psicológicos)\n"
            
            response += "\n❓ ¿Te gustaría que genere un plan de intervención detallado?"
            return response
        else:
            return " ¡Excelente noticia! No hay alumnos en situación de riesgo actualmente. El sistema educativo está funcionando bien. "
    
    elif intent == 'promedio':
        query = """
        SELECT c.nombre as carrera, 
               COUNT(al.id) as total_alumnos,
               ROUND(AVG(al.promedio_general), 2) as promedio_carrera,
               COUNT(CASE WHEN al.promedio_general < 7.0 THEN 1 END) as alumnos_riesgo
        FROM carreras c
        LEFT JOIN alumnos al ON c.id = al.carrera_id
        WHERE al.estado_alumno = 'activo'
        GROUP BY c.id, c.nombre
        ORDER BY promedio_carrera DESC
        LIMIT 10
        """
        data = execute_query(query)
        
        if data:
            response = "**Rendimiento por Carrera:**\n\n"
            for row in data:
                porcentaje_riesgo = (row['alumnos_riesgo'] / row['total_alumnos'] * 100) if row['total_alumnos'] > 0 else 0
                emoji = "🟢" if porcentaje_riesgo < 10 else "🟡" if porcentaje_riesgo < 25 else "🔴"
                
                response += f"{emoji} **{row['carrera']}**\n"
                response += f"   Alumnos: {row['total_alumnos']}\n"
                response += f"   Promedio: {row['promedio_carrera']}\n"
                response += f"   En riesgo: {row['alumnos_riesgo']} ({porcentaje_riesgo:.1f}%)\n\n"
            
            response += " ¿Te gustaría ver un análisis más detallado de alguna carrera específica?"
            return response
        else:
            return " No se encontraron datos de promedios por carrera."
    
    elif intent == 'estadisticas':
        queries = [
            ("Total Alumnos Activos", "SELECT COUNT(*) as total FROM alumnos WHERE estado_alumno = 'activo'"),
            ("Total Carreras", "SELECT COUNT(*) as total FROM carreras WHERE activa = 1"),
            ("Reportes Abiertos", "SELECT COUNT(*) as total FROM reportes_riesgo WHERE estado IN ('abierto', 'en_proceso')"),
            ("Solicitudes Pendientes", "SELECT COUNT(*) as total FROM solicitudes_ayuda WHERE estado IN ('pendiente', 'en_atencion')")
        ]
        
        response = " **Estadísticas del Sistema:**\n\n"
        
        for name, query in queries:
            result = execute_query(query)
            if result:
                response += f"• **{name}**: {result[0]['total']}\n"
        
        # Agregar promedio general del sistema
        avg_query = "SELECT ROUND(AVG(promedio_general), 2) as promedio_sistema FROM alumnos WHERE estado_alumno = 'activo' AND promedio_general > 0"
        avg_result = execute_query(avg_query)
        if avg_result and avg_result[0]['promedio_sistema']:
            response += f"• **Promedio General del Sistema**: {avg_result[0]['promedio_sistema']}\n"
        
        response += "\n ¿Te gustaría un análisis más profundo de algún área específica?"
        return response
    
    elif intent == 'conversacion_general':
        # Respuestas más naturales para conversación general
        general_responses = [
            f"Hmm, entiendo. ¿Hay algo específico sobre la institución en lo que te pueda ayudar? ",
            f"Claro, recibí tu mensaje. ¿Te gustaría que revisemos alguna información académica? ",
            f"Perfecto. Como asistente académico, ¿en qué puedo asistirte específicamente? ",
            f"Entiendo. ¿Necesitas información sobre estudiantes, profesores o estadísticas? "
        ]
        return random.choice(general_responses)
    
    # Default conversacional más natural
    return f"Interesante. ¿En qué puedo ayudarte específicamente? Puedo consultar información sobre estudiantes, profesores, calificaciones y más. "
        query = """
        SELECT a.nombre, c.calificacion_final, c.estatus, c.parcial_1, c.parcial_2, c.parcial_3
        FROM calificaciones c
        JOIN asignaturas a ON c.asignatura_id = a.id
        JOIN alumnos al ON c.alumno_id = al.id
        WHERE al.usuario_id = %s
        ORDER BY a.nombre
        LIMIT 10
        """
        data = execute_query(query, [user_id])
        
        if data:
            response = " **Aquí tienes tus calificaciones:**\n\n"
            total_promedio = 0
            materias_count = 0
            materias_riesgo = 0
            
            for row in data:
                if row['calificacion_final']:
                    total_promedio += row['calificacion_final']
                    materias_count += 1
                    if row['calificacion_final'] < 7.0:
                        materias_riesgo += 1
                
                status = "✅" if row['estatus'] == 'aprobado' else "📝" if row['estatus'] == 'cursando' else "❌"
                grade = f"{row['calificacion_final']:.1f}" if row['calificacion_final'] else 'Sin calificar'
                response += f"{status} **{row['nombre']}**: {grade}\n"
                
                # Mostrar parciales si están disponibles
                if row['parcial_1'] or row['parcial_2'] or row['parcial_3']:
                    parciales = []
                    if row['parcial_1']: parciales.append(f"P1: {row['parcial_1']:.1f}")
                    if row['parcial_2']: parciales.append(f"P2: {row['parcial_2']:.1f}")
                    if row['parcial_3']: parciales.append(f"P3: {row['parcial_3']:.1f}")
                    response += f"    {' | '.join(parciales)}\n"
                response += "\n"
            
            if materias_count > 0:
                promedio_actual = total_promedio / materias_count
                response += f" **Tu promedio actual**: {promedio_actual:.2f}\n\n"
                
                if promedio_actual >= 9.0:
                    response += "🌟 ¡Excelente trabajo! Sigues por muy buen camino."
                elif promedio_actual >= 8.0:
                    response += "👍 ¡Muy bien! Tu rendimiento es bueno."
                elif promedio_actual >= 7.0:
                    response += "💪 Vas bien, pero hay espacio para mejorar."
                else:
                    response += "⚠️ Necesitas enfocarte más en tus estudios."
                
                if materias_riesgo > 0:
                    response += f"\n Tienes {materias_riesgo} materia(s) por debajo de 7.0"
            
            response += "\n\n ¿Te gustaría ver estrategias para mejorar en alguna materia específica?"
            return response
        else:
            return " No encontré calificaciones registradas para ti. ¿Es tu primer cuatrimestre? Si crees que es un error, puedes contactar a tu coordinador académico. 😊"
    
    elif intent == 'riesgo':
        query = """
        SELECT u.nombre, u.apellido, al.matricula, rr.nivel_riesgo, rr.tipo_riesgo, rr.descripcion, car.nombre as carrera
        FROM reportes_riesgo rr
        JOIN alumnos al ON rr.alumno_id = al.id
        JOIN usuarios u ON al.usuario_id = u.id
        JOIN carreras car ON al.carrera_id = car.id
        WHERE rr.estado IN ('abierto', 'en_proceso')
        ORDER BY CASE rr.nivel_riesgo 
            WHEN 'critico' THEN 1 
            WHEN 'alto' THEN 2 
            WHEN 'medio' THEN 3 
            ELSE 4 END
        LIMIT 10
        """
        data = execute_query(query)
        
        if data:
            criticos = len([d for d in data if d['nivel_riesgo'] == 'critico'])
            response = f" **Alumnos que necesitan atención** ({len(data)} casos activos):\n\n"
            
            for row in data:
                emoji = "🔴" if row['nivel_riesgo'] == 'critico' else "🟡" if row['nivel_riesgo'] == 'alto' else "🟠"
                response += f"{emoji} **{row['nombre']} {row['apellido']}** ({row['matricula']})\n"
                response += f"   Carrera: {row['carrera']}\n"
                response += f"   Riesgo: {row['nivel_riesgo']} ({row['tipo_riesgo']})\n"
                if row['descripcion']:
                    response += f"    {row['descripcion'][:80]}...\n"
                response += "\n"
            
            if criticos > 0:
                response += f" **ATENCIÓN URGENTE**: {criticos} estudiantes en riesgo crítico requieren intervención inmediata.\n\n"
                response += " **Recomendaciones**:\n"
                response += "• Contactar a padres/tutores hoy mismo\n"
                response += "• Programar citas individuales esta semana\n"
                response += "• Evaluar apoyos adicionales (económicos, psicológicos)\n"
            
            response += "\n ¿Te gustaría que genere un plan de intervención detallado?"
            return response
        else:
            return " ¡Excelente noticia! No hay alumnos en situación de riesgo actualmente. El sistema educativo está funcionando bien. 😊"
    
    elif intent == 'promedio':
        query = """
        SELECT c.nombre as carrera, 
               COUNT(al.id) as total_alumnos,
               ROUND(AVG(al.promedio_general), 2) as promedio_carrera,
               COUNT(CASE WHEN al.promedio_general < 7.0 THEN 1 END) as alumnos_riesgo
        FROM carreras c
        LEFT JOIN alumnos al ON c.id = al.carrera_id
        WHERE al.estado_alumno = 'activo'
        GROUP BY c.id, c.nombre
        ORDER BY promedio_carrera DESC
        LIMIT 10
        """
        data = execute_query(query)
        
        if data:
            response = " **Rendimiento por Carrera:**\n\n"
            for row in data:
                porcentaje_riesgo = (row['alumnos_riesgo'] / row['total_alumnos'] * 100) if row['total_alumnos'] > 0 else 0
                emoji = "🟢" if porcentaje_riesgo < 10 else "🟡" if porcentaje_riesgo < 25 else "🔴"
                
                response += f"{emoji} **{row['carrera']}**\n"
                response += f"   Alumnos: {row['total_alumnos']}\n"
                response += f"   Promedio: {row['promedio_carrera']}\n"
                response += f"   En riesgo: {row['alumnos_riesgo']} ({porcentaje_riesgo:.1f}%)\n\n"
            
            response += " ¿Te gustaría ver un análisis más detallado de alguna carrera específica?"
            return response
        else:
            return " No se encontraron datos de promedios por carrera."
    
    elif intent == 'estadisticas':
        queries = [
            ("Total Alumnos Activos", "SELECT COUNT(*) as total FROM alumnos WHERE estado_alumno = 'activo'"),
            ("Total Carreras", "SELECT COUNT(*) as total FROM carreras WHERE activa = 1"),
            ("Reportes Abiertos", "SELECT COUNT(*) as total FROM reportes_riesgo WHERE estado IN ('abierto', 'en_proceso')"),
            ("Solicitudes Pendientes", "SELECT COUNT(*) as total FROM solicitudes_ayuda WHERE estado IN ('pendiente', 'en_atencion')")
        ]
        
        response = " **Estadísticas del Sistema:**\n\n"
        
        for name, query in queries:
            result = execute_query(query)
            if result:
                response += f"• **{name}**: {result[0]['total']}\n"
        
        # Agregar promedio general del sistema
        avg_query = "SELECT ROUND(AVG(promedio_general), 2) as promedio_sistema FROM alumnos WHERE estado_alumno = 'activo' AND promedio_general > 0"
        avg_result = execute_query(avg_query)
        if avg_result and avg_result[0]['promedio_sistema']:
            response += f"• **Promedio General del Sistema**: {avg_result[0]['promedio_sistema']}\n"
        
        response += "\n ¿Te gustaría un análisis más profundo de algún área específica?"
        return response
    
    elif intent == 'conversacion_general':
        general_responses = [
            f"Interesante lo que me dices: '{message}' . Como tu asistente académico, ¿hay algo relacionado con tus estudios en lo que te pueda ayudar?",
            f"Entiendo tu mensaje sobre '{message}' . ¿Te gustaría que revisemos algo específico de tu situación académica?",
            f"Gracias por compartir eso conmigo. Como asistente educativo, estoy aquí para apoyarte. ¿Hay alguna consulta académica que tengas?",
            f"Me parece muy interesante lo que mencionas. ¿Podemos enfocar nuestra conversación en cómo te puedo ayudar con tus estudios? "
        ]
        return random.choice(general_responses)
    
    # Default conversacional
    return f"Hmm, entiendo que me dices '{message}' . Como tu asistente académico, ¿en qué puedo ayudarte específicamente? Puedo consultar calificaciones, reportes de riesgo, estadísticas y más. "

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": " FUNCIONANDO",
        "message": "IA Conversacional con MySQL - Railway",
        "version": "2.0.0",
        "features": ["Conversación Natural", "Base de Datos Real", "Contexto Mantenido"],
        "endpoints": ["/api/test", "/api/chat", "/api/suggestions"],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/test', methods=['GET'])
def test():
    try:
        # Test BD
        result = execute_query("SELECT 1 as test, 'Conexión exitosa a MySQL' as mensaje, NOW() as tiempo")
        
        if result:
            return jsonify({
                "success": True,
                "message": "Sistema completamente funcional",
                "database": "MySQL Conectado",
                "conversation": " IA Conversacional Activa",
                "result": result[0],
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({
                "success": False,
                "message": " Error de conexión a BD",
                "database": " MySQL Desconectado"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error en test del sistema"
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({"error": "Mensaje requerido"}), 400
        
        message = data['message'].strip()
        role = data.get('role', 'alumno')
        user_id = data.get('user_id', 1)
        
        if not message:
            return jsonify({
                "success": True,
                "response": " Parece que no escribiste nada. ¿En qué te puedo ayudar?",
                "intent": "mensaje_vacio"
            })
        
        logger.info(f"Chat conversacional: {message} (role: {role}, user: {user_id})")
        
        # Obtener contexto
        context = get_conversation_context(user_id)
        
        # Clasificar intención
        intent = classify_intent(message, context)
        
        # Generar respuesta conversacional
        response_text = get_conversational_response(intent, message, context, role, user_id)
        
        # Actualizar contexto
        update_context(user_id, message, intent, response_text)
        
        return jsonify({
            "success": True,
            "response": response_text,
            "intent": intent,
            "conversational": True,
            "context_messages": len(context['messages']),
            "role": role,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error chat: {e}")
        return jsonify({
            "success": False,
            "error": "Error procesando mensaje",
            "response": "Lo siento, tuve un problema procesando tu mensaje 😅. ¿Puedes intentar de nuevo?",
            "details": str(e)
        }), 500

@app.route('/api/suggestions', methods=['GET'])
def suggestions():
    role = request.args.get('role', 'alumno')
    
    suggestions_map = {
        'alumno': [
            "Hola, ¿cómo estás?",
            "¿Cuáles son mis calificaciones?",
            "¿Cómo van mis materias este cuatrimestre?",
            "Me siento preocupado por mis notas",
            "¿Qué puedes hacer por mí?",
            "Gracias por tu ayuda"
        ],
        'profesor': [
            "¡Buenos días!",
            "¿Qué alumnos están en riesgo?",
            "¿Cuáles son mis grupos asignados?",
            "¿Hay reportes urgentes?",
            "¿Cómo puedo ayudar a mis estudiantes?",
            "Necesito estadísticas de mi clase"
        ],
        'directivo': [
            "Hola, ¿cómo va todo?",
            "¿Cuáles son las estadísticas generales?",
            "¿Cómo va el rendimiento por carrera?",
            "¿Qué alumnos necesitan atención urgente?",
            "Dame un resumen del sistema",
            "¿Hay algo preocupante que deba saber?"
        ]
    }
    
    return jsonify({
        "success": True,
        "suggestions": suggestions_map.get(role, suggestions_map['alumno']),
        "role": role,
        "message": f"Sugerencias conversacionales para {role}"
    })

@app.route('/api/context/<int:user_id>', methods=['GET'])
def get_context(user_id):
    context = get_conversation_context(user_id)
    return jsonify({
        "success": True,
        "user_id": user_id,
        "messages_count": len(context['messages']),
        "last_intent": context['last_intent'],
        "recent_messages": context['messages'][-3:] if context['messages'] else []
    })

@app.route('/api/context/<int:user_id>', methods=['DELETE'])
def clear_context(user_id):
    if user_id in conversation_contexts:
        del conversation_contexts[user_id]
    
    return jsonify({
        "success": True,
        "message": f"Contexto limpiado para usuario {user_id}"
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint no encontrado 😅", 
        "message": "¿Estás seguro de la URL? Aquí están los endpoints disponibles:",
        "endpoints": ["/", "/api/test", "/api/chat", "/api/suggestions"]
    }), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "error": "Error interno del servidor 😱",
        "message": "Algo salió mal, pero trabajaré en arreglarlo"
    }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚂 Iniciando IA Conversacional en puerto {port}")
    app.run(host='0.0.0.0', port=port, debug=False)