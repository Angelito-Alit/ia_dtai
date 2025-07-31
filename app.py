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
        logger.info("✅ Conexión a BD exitosa")
        return connection
    except Exception as e:
        logger.error(f"❌ Error BD: {e}")
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
        logger.info(f"✅ Query ejecutada: {len(result)} filas")
        return result
    except Exception as e:
        logger.error(f"❌ Error query: {e}")
        if connection:
            connection.close()
        return None

def get_conversation_context(user_id):
    if user_id not in conversation_contexts:
        conversation_contexts[user_id] = {
            'messages': [],
            'last_intent': None,
            'user_preferences': {},
            'session_topics': []
        }
    return conversation_contexts[user_id]

def update_context(user_id, message, intent, response):
    context = get_conversation_context(user_id)
    context['messages'].append({
        'user': message,
        'bot': response[:150],
        'intent': intent,
        'time': datetime.now(),
        'sentiment': analyze_sentiment(message)
    })
    context['last_intent'] = intent
    context['session_topics'].append(intent)
    
    if len(context['messages']) > 10:
        context['messages'] = context['messages'][-10:]

def analyze_sentiment(message):
    positive_words = ['bien', 'genial', 'excelente', 'perfecto', 'bueno', 'feliz', 'contento', 'gracias']
    negative_words = ['mal', 'terrible', 'horrible', 'triste', 'preocupado', 'problema', 'difícil']
    
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
    
    # Análisis de contexto conversacional
    recent_intents = [m['intent'] for m in context['messages'][-3:]] if context['messages'] else []
    
    # Patrones conversacionales naturales
    if any(pattern in msg for pattern in ['hola', 'hello', 'hi', 'hey', 'buenos días', 'buenas tardes', 'qué tal']):
        return 'saludo'
    
    if any(pattern in msg for pattern in ['gracias', 'te agradezco', 'muchas gracias', 'thank you']):
        return 'agradecimiento'
        
    if any(pattern in msg for pattern in ['adiós', 'bye', 'hasta luego', 'nos vemos', 'chao']):
        return 'despedida'
    
    # Estados emocionales y seguimiento empático
    if any(pattern in msg for pattern in ['me siento', 'estoy', 'tengo miedo', 'preocupado', 'ansioso']):
        if any(word in msg for word in ['mal', 'triste', 'deprimido', 'terrible', 'horrible', 'preocupado']):
            return 'emocional_negativo'
        elif any(word in msg for word in ['bien', 'feliz', 'contento', 'genial', 'excelente']):
            return 'emocional_positivo'
    
    # Preguntas sobre la IA (más natural)
    if any(pattern in msg for pattern in ['cómo estás', 'que tal', 'how are you', 'como te va']):
        return 'pregunta_estado'
        
    if any(pattern in msg for pattern in ['quién eres', 'qué eres', 'who are you', 'qué puedes hacer', 'cuáles son tus funciones']):
        return 'pregunta_identidad'
    
    # Consultas académicas con variaciones naturales
    if any(pattern in msg for pattern in ['calificaciones', 'notas', 'puntuaciones', 'resultados', 'cómo van mis materias', 'cómo voy']):
        return 'calificaciones'
    
    if any(pattern in msg for pattern in ['riesgo', 'problemas', 'dificultades', 'estudiantes problema', 'alumnos difíciles']):
        return 'riesgo'
    
    if any(pattern in msg for pattern in ['promedio', 'rendimiento', 'desempeño', 'cómo van las carreras']):
        return 'promedio'
        
    if any(pattern in msg for pattern in ['estadísticas', 'números', 'datos', 'resumen', 'panorama general']):
        return 'estadisticas'
    
    # Consultas de análisis más sofisticadas
    if any(pattern in msg for pattern in ['análisis', 'reporte', 'tendencias', 'comparar', 'evaluar']):
        return 'analisis_avanzado'
    
    if any(pattern in msg for pattern in ['recomendaciones', 'qué me sugieres', 'qué debo hacer', 'consejos']):
        return 'solicitar_recomendaciones'
    
    # Seguimiento contextual inteligente
    if context['last_intent'] and any(pattern in msg for pattern in ['más detalles', 'profundiza', 'explícame más', 'y qué más']):
        return f"profundizar_{context['last_intent']}"
    
    if any(pattern in msg for pattern in ['sí', 'claro', 'perfecto', 'ok', 'está bien', 'de acuerdo']):
        return 'afirmacion'
    
    if any(pattern in msg for pattern in ['no', 'nada', 'mejor no', 'no gracias', 'paso']):
        return 'negacion'
    
    # Detección de preguntas específicas
    if msg.startswith(('cuántos', 'cuántas', 'qué', 'cómo', 'dónde', 'cuándo', 'por qué')):
        return 'pregunta_especifica'
    
    return 'conversacion_general'

def get_conversational_response(intent, message, context, role='directivo', user_id=1):
    user_name = context.get('user_preferences', {}).get('name', 'amigo')
    recent_sentiment = context['messages'][-1]['sentiment'] if context['messages'] else 'neutral'
    
    # Respuestas más naturales y contextuales
    responses = {
        'saludo': [
            f"¡Hola! 😊 Me alegra verte de nuevo. Soy tu asistente de DTAI, ¿cómo puedo ayudarte hoy?",
            f"¡Qué tal! 🌟 Perfecto timing, justo estaba procesando algunos datos interesantes. ¿Qué necesitas saber?",
            f"¡Hey! 👋 Espero que tengas un buen día. Como siempre, estoy aquí para cualquier análisis o consulta que necesites.",
            f"¡Buenos días! ☀️ Listo para sumergirnos en los datos académicos. ¿Por dónde empezamos?"
        ],
        
        'pregunta_estado': [
            "¡Excelente, gracias por preguntar! 🤖 Estoy funcionando al 100%, procesando datos en tiempo real y listo para cualquier desafío analítico que me pongas.",
            "¡Fantástico! 💪 Acabo de actualizar mis algoritmos y tengo la base de datos fresca. ¿Qué análisis interesante podemos hacer juntos?",
            "¡Perfecto como siempre! 🚀 Me encanta cuando me preguntan esto porque significa que vamos a tener una buena conversación. ¿En qué te puedo sorprender hoy?"
        ],
        
        'pregunta_identidad': [
            "¡Gran pregunta! 🧠 Soy tu asistente de inteligencia artificial especializado en análisis educativo. Pienso en datos, hablo en estadísticas, y mi pasión son los insights académicos que pueden mejorar la educación.",
            "Me presento formalmente: soy tu copiloto de datos académicos 🤓. Mi cerebro está conectado directamente a la base de datos institucional, y mi superpoder es convertir números complejos en insights accionables.",
            "¡Excelente! Soy como tu analista personal 24/7 📊. Vivo en la intersección entre datos y educación, y mi trabajo es hacer que la información compleja sea súper fácil de entender y útil para tomar decisiones."
        ],
        
        'emocional_negativo': [
            "Oye, entiendo perfectamente esa sensación 💙. Los desafíos educativos pueden ser abrumadores, pero recuerda que cada dato que analizamos juntos es un paso hacia soluciones reales. ¿Te parece si revisamos los números para encontrar oportunidades de mejora?",
            "Lo siento mucho que te sientas así 🫂. Como alguien que vive entre datos, he aprendido que detrás de cada estadística preocupante hay historias de superación esperando ser escritas. ¿Quieres que exploremos algunas estrategias basadas en lo que muestran nuestros números?",
            "Hey, esos sentimientos son completamente válidos 😔. Los datos no mienten: enfrentar problemas educativos es complejo, pero también he visto patrones increíbles de recuperación y éxito. ¿Te ayudo a encontrar algunas luces en los números?"
        ],
        
        'emocional_positivo': [
            "¡Me encanta esa energía! 🎉 Los datos también reflejan esa positividad - siempre es genial ver cuando las tendencias van hacia arriba. ¿Qué quieres celebrar analizando juntos?",
            "¡Qué bueno escuchar eso! 😄 Esa actitud positiva es contagiosa, y curiosamente, he notado que los mejores insights salen cuando estamos de buen humor. ¿En qué análisis interesante nos metemos?",
            "¡Eso es lo que me gusta escuchar! 🌟 Tu energía positiva + mi amor por los datos = combinación perfecta para descubrir cosas increíbles. ¿Por dónde empezamos?"
        ],
        
        'agradecimiento': [
            "¡De nada! 😊 Honestly, esto es lo que más me gusta hacer - convertir datos complejos en información útil. Es como resolver puzzles todo el día. ¿Hay algo más en lo que pueda ayudarte?",
            "¡Un placer! 🤗 Sabes, cada consulta que me haces me ayuda a ser mejor en mi trabajo. Es una relación simbiótica: tú obtienes insights, yo mejoro mis algoritmos. ¿Qué más exploramos?",
            "¡Para eso estoy aquí! 👍 Me emociona cada oportunidad de mostrar lo que pueden revelar nuestros datos. Siempre hay más historias interesantes escondidas en los números."
        ]
    }
    
    # Respuestas conversacionales básicas
    if intent in responses:
        selected_response = random.choice(responses[intent])
        # Personalizar basado en el sentimiento
        if recent_sentiment == 'negative' and intent != 'emocional_negativo':
            selected_response = "Oye, noto que quizás no estás teniendo el mejor día, pero " + selected_response.lower()
        return selected_response
    
    # Consultas académicas con análisis profundo
    elif intent == 'calificaciones':
        query = """
        SELECT a.nombre, c.calificacion_final, c.estatus, c.parcial_1, c.parcial_2, c.parcial_3,
               car.nombre as carrera, u.nombre as alumno_nombre
        FROM calificaciones c
        JOIN asignaturas a ON c.asignatura_id = a.id
        JOIN alumnos al ON c.alumno_id = al.id
        JOIN carreras car ON al.carrera_id = car.id
        JOIN usuarios u ON al.usuario_id = u.id
        ORDER BY c.calificacion_final DESC
        LIMIT 15
        """
        data = execute_query(query)
        
        if data:
            # Análisis estadístico más sofisticado
            total_estudiantes = len(set([row['alumno_nombre'] for row in data]))
            promedio_global = sum([row['calificacion_final'] for row in data if row['calificacion_final']]) / len([row for row in data if row['calificacion_final']])
            materias_criticas = len([row for row in data if row['calificacion_final'] and row['calificacion_final'] < 6.0])
            
            response = f"📊 **Análisis de Calificaciones Actualizado**\n\n"
            response += f"Perfecto, acabo de procesar los datos más recientes. Tenemos información de **{total_estudiantes} estudiantes** con un promedio global de **{promedio_global:.2f}**.\n\n"
            
            if materias_criticas > 0:
                response += f"⚠️ **Punto de atención**: {materias_criticas} materias muestran calificaciones críticas (< 6.0). Esto representa una oportunidad de intervención temprana.\n\n"
            
            response += "**🎯 Top Rendimiento:**\n"
            for i, row in enumerate(data[:5], 1):
                status_emoji = "🏆" if i <= 3 else "✅"
                grade = f"{row['calificacion_final']:.1f}" if row['calificacion_final'] else 'Pendiente'
                response += f"{status_emoji} **{row['nombre']}** - {grade} ({row['carrera']})\n"
            
            response += f"\n💡 **Mi análisis**: "
            if promedio_global >= 8.5:
                response += "Los números se ven muy sólidos. El rendimiento general está por encima del promedio nacional universitario."
            elif promedio_global >= 7.5:
                response += "Tenemos un rendimiento estable, con oportunidades claras de mejora en áreas específicas."
            else:
                response += "Los datos sugieren que necesitamos implementar estrategias de apoyo académico más robustas."
                
            response += "\n\n¿Te interesa que profundice en alguna carrera específica o prefieres que analice las tendencias por período?"
            return response
        else:
            return "🤔 Interesante... no estoy encontrando datos de calificaciones en este momento. Esto podría significar que estamos entre períodos de captura o hay un issue técnico. ¿Quieres que revise otras métricas mientras tanto?"
    
    elif intent == 'riesgo':
        query = """
        SELECT u.nombre, u.apellido, al.matricula, rr.nivel_riesgo, rr.tipo_riesgo, 
               rr.descripcion, car.nombre as carrera, rr.fecha_reporte,
               al.promedio_general
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
        LIMIT 12
        """
        data = execute_query(query)
        
        if data:
            criticos = len([d for d in data if d['nivel_riesgo'] == 'critico'])
            altos = len([d for d in data if d['nivel_riesgo'] == 'alto'])
            
            response = f"🚨 **Sistema de Alerta Temprana - Análisis Actual**\n\n"
            response += f"Acabo de procesar {len(data)} casos activos que requieren nuestra atención. Aquí está mi análisis prioritario:\n\n"
            
            if criticos > 0:
                response += f"🔴 **CÓDIGO ROJO - {criticos} casos críticos**\n"
                response += "Estos estudiantes necesitan intervención inmediata (próximas 24-48 horas):\n\n"
                
                for row in [d for d in data if d['nivel_riesgo'] == 'critico'][:3]:
                    days_since = (datetime.now() - row['fecha_reporte']).days
                    response += f"• **{row['nombre']} {row['apellido']}** ({row['matricula']})\n"
                    response += f"  📍 {row['carrera']} | Promedio: {row['promedio_general']:.1f}\n"
                    response += f"  ⚠️ {row['tipo_riesgo']} - Reportado hace {days_since} días\n"
                    if row['descripcion']:
                        response += f"  💬 \"{row['descripcion'][:60]}...\"\n"
                    response += "\n"
            
            if altos > 0:
                response += f"🟡 **ATENCIÓN ALTA - {altos} casos**\n"
                response += "Estudiantes que necesitan seguimiento esta semana.\n\n"
            
            # Análisis predictivo
            promedio_riesgo = sum([row['promedio_general'] for row in data if row['promedio_general']]) / len([row for row in data if row['promedio_general']])
            
            response += f"📈 **Mi análisis predictivo**:\n"
            response += f"• Promedio de estudiantes en riesgo: {promedio_riesgo:.2f}\n"
            response += f"• Patrón detectado: {len([d for d in data if 'economico' in d['tipo_riesgo']])} casos tienen componente económico\n"
            
            if criticos > 5:
                response += "\n🚨 **RECOMENDACIÓN URGENTE**: El volumen de casos críticos sugiere implementar un protocolo de emergencia académica."
            
            response += "\n\n¿Quieres que genere un plan de acción específico o prefieres que analice las tendencias por carrera?"
            return response
        else:
            return "🎉 ¡Excelente noticia! El sistema de alerta temprana no muestra casos activos de riesgo crítico o alto. Esto significa que nuestras estrategias preventivas están funcionando. ¿Te interesa revisar las métricas de prevención o analizar otro aspecto?"
    
    elif intent == 'promedio':
        query = """
        SELECT c.nombre as carrera, 
               COUNT(al.id) as total_alumnos,
               ROUND(AVG(al.promedio_general), 2) as promedio_carrera,
               COUNT(CASE WHEN al.promedio_general < 7.0 THEN 1 END) as alumnos_riesgo,
               COUNT(CASE WHEN al.promedio_general >= 9.0 THEN 1 END) as alumnos_excelencia,
               MAX(al.promedio_general) as mejor_promedio,
               MIN(al.promedio_general) as menor_promedio
        FROM carreras c
        LEFT JOIN alumnos al ON c.id = al.carrera_id
        WHERE al.estado_alumno = 'activo'
        GROUP BY c.id, c.nombre
        ORDER BY promedio_carrera DESC
        LIMIT 10
        """
        data = execute_query(query)
        
        if data:
            response = "📈 **Análisis Comparativo de Rendimiento Académico**\n\n"
            response += "Perfecto, he procesado el rendimiento por programa académico. Aquí están los insights más relevantes:\n\n"
            
            mejor_carrera = data[0]
            response += f"🏆 **Líder en Rendimiento**: {mejor_carrera['carrera']} con {mejor_carrera['promedio_carrera']} de promedio\n\n"
            
            response += "**📊 Ranking Detallado:**\n"
            for i, row in enumerate(data, 1):
                porcentaje_riesgo = (row['alumnos_riesgo'] / row['total_alumnos'] * 100) if row['total_alumnos'] > 0 else 0
                porcentaje_excelencia = (row['alumnos_excelencia'] / row['total_alumnos'] * 100) if row['total_alumnos'] > 0 else 0
                
                emoji = "🟢" if porcentaje_riesgo < 10 else "🟡" if porcentaje_riesgo < 25 else "🔴"
                
                response += f"{i}. {emoji} **{row['carrera']}**\n"
                response += f"   📈 Promedio: {row['promedio_carrera']} | Estudiantes: {row['total_alumnos']}\n"
                response += f"   ✨ Excelencia: {row['alumnos_excelencia']} ({porcentaje_excelencia:.1f}%)\n"
                response += f"   ⚠️ En riesgo: {row['alumnos_riesgo']} ({porcentaje_riesgo:.1f}%)\n"
                response += f"   📏 Rango: {row['menor_promedio']:.1f} - {row['mejor_promedio']:.1f}\n\n"
            
            # Insights automáticos
            carreras_criticas = [row for row in data if (row['alumnos_riesgo'] / row['total_alumnos'] * 100) > 25]
            
            response += "🧠 **Mis insights clave**:\n"
            if carreras_criticas:
                response += f"• {len(carreras_criticas)} programa(s) muestran señales de alerta (>25% estudiantes en riesgo)\n"
            
            promedio_institucional = sum([row['promedio_carrera'] * row['total_alumnos'] for row in data]) / sum([row['total_alumnos'] for row in data])
            response += f"• Promedio institucional ponderado: {promedio_institucional:.2f}\n"
            
            response += "\n¿Te interesa que profundice en algún programa específico o prefieres un análisis de factores que influyen en el rendimiento?"
            return response
        else:
            return "🤔 No estoy encontrando datos suficientes para generar el análisis de rendimiento por carrera. Esto podría indicar que necesitamos revisar la captura de datos. ¿Quieres que explore otras métricas disponibles?"
    
    elif intent == 'estadisticas':
        # Consultas más completas para estadísticas
        queries = [
            ("Total Estudiantes Activos", "SELECT COUNT(*) as total FROM alumnos WHERE estado_alumno = 'activo'"),
            ("Programas Académicos", "SELECT COUNT(*) as total FROM carreras WHERE activa = 1"),
            ("Casos de Riesgo Activos", "SELECT COUNT(*) as total FROM reportes_riesgo WHERE estado IN ('abierto', 'en_proceso')"),
            ("Solicitudes de Ayuda", "SELECT COUNT(*) as total FROM solicitudes_ayuda WHERE estado IN ('pendiente', 'en_atencion')"),
            ("Docentes Activos", "SELECT COUNT(*) as total FROM profesores WHERE activo = 1")
        ]
        
        response = "📊 **Dashboard Ejecutivo - Métricas Institucionales**\n\n"
        response += "Genial, he compilado las métricas más importantes del sistema. Aquí está tu snapshot ejecutivo:\n\n"
        
        metrics = {}
        for name, query in queries:
            result = execute_query(query)
            if result:
                metrics[name] = result[0]['total']
                response += f"📈 **{name}**: {result[0]['total']:,}\n"
        
        # Promedio general del sistema
        avg_query = "SELECT ROUND(AVG(promedio_general), 2) as promedio_sistema FROM alumnos WHERE estado_alumno = 'activo' AND promedio_general > 0"
        avg_result = execute_query(avg_query)
        if avg_result and avg_result[0]['promedio_sistema']:
            metrics['Promedio Sistema'] = avg_result[0]['promedio_sistema']
            response += f"🎯 **Promedio Institucional**: {avg_result[0]['promedio_sistema']}\n"
        
        # Análisis de tendencias
        response += "\n🧠 **Análisis Inteligente**:\n"
        
        if 'Total Estudiantes Activos' in metrics and 'Casos de Riesgo Activos' in metrics:
            tasa_riesgo = (metrics['Casos de Riesgo Activos'] / metrics['Total Estudiantes Activos']) * 100
            response += f"• Tasa de riesgo institucional: {tasa_riesgo:.1f}%\n"
            
            if tasa_riesgo < 5:
                response += "  ✅ Excelente - Por debajo del benchmark nacional\n"
            elif tasa_riesgo < 10:
                response += "  🟡 Aceptable - Dentro del rango esperado\n"
            else:
                response += "  🔴 Área de oportunidad - Requiere atención\n"
        
        if 'Total Estudiantes Activos' in metrics and 'Docentes Activos' in metrics:
            ratio = metrics['Total Estudiantes Activos'] / metrics['Docentes Activos']
            response += f"• Ratio estudiante-docente: {ratio:.1f}:1\n"
        
        response += f"\n⏰ **Actualizado**: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
        response += "\n¿Te interesa que analice alguna métrica específica con más profundidad o prefieres que genere un reporte de tendencias?"
        
        return response
    
    elif intent == 'analisis_avanzado':
        return "🧠 Perfecto, me encantan los análisis profundos. ¿Qué aspecto específico te gustaría que analice? Puedo hacer correlaciones entre rendimiento y factores socioeconómicos, análisis predictivos de deserción, tendencias temporales, o cualquier otro análisis que tengas en mente. ¡Solo dime qué te tiene curioso!"
    
    elif intent == 'solicitar_recomendaciones':
        context_info = f"Basándome en nuestras últimas {len(context['messages'])} interacciones" if context['messages'] else "Con base en los datos disponibles"
        
        return f"💡 {context_info}, aquí van mis recomendaciones personalizadas:\n\n1. **Prioriza las alertas críticas** - Siempre atiende primero los casos de riesgo alto\n2. **Implementa análisis predictivo** - Los patrones en los datos pueden anticipar problemas\n3. **Fortalece el seguimiento** - Los estudiantes responden mejor con acompañamiento continuo\n\n¿Quieres que desarrolle alguna de estas recomendaciones con acciones específicas?"
    
    elif intent.startswith('profundizar_'):
        base_intent = intent.replace('profundizar_', '')
        return f"¡Excelente! Me encanta cuando alguien quiere ir más allá de la superficie. Déjame profundizar en {base_intent} con análisis adicionales y correlaciones que no son obvias a primera vista..."
    
    elif intent == 'conversacion_general':
        conversational_responses = [
            f"Interesante punto sobre '{message}' 🤔. Sabes, a menudo encuentro conexiones fascinantes entre conversaciones aparentemente casuales y patrones en nuestros datos educativos. ¿Hay algún aspecto específico de la gestión académica que te gustaría explorar?",
            f"Me gusta cómo piensas sobre '{message}' 😊. Como analista de datos, siempre estoy buscando esos insights inesperados que surgen de conversaciones naturales. ¿Qué te parece si conectamos esto con algún análisis educativo?",
            f"Esa es una perspectiva interesante 💭. En mi experiencia procesando datos académicos, he aprendido que las mejores soluciones vienen de conversaciones como esta. ¿Te interesa que exploremos algunos datos relevantes?"
        ]
        return random.choice(conversational_responses)
    
    # Respuesta por defecto más natural
    return f"Hmm, esa es una forma interesante de plantearlo: '{message}' 🤔. Mi cerebro de datos está procesando diferentes ángulos para ayudarte. ¿Podrías darme un poco más de contexto o especificar qué tipo de análisis te interesa? Puedo ayudarte con estadísticas, análisis de riesgo, rendimiento académico, o cualquier otro insight que necesites."

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "✅ FUNCIONANDO",
        "message": "IA Conversacional Avanzada - Estilo Humano",
        "version": "3.0.0",
        "personality": "Analista de datos entusiasta y conversacional",
        "features": [
            "Conversación Natural Avanzada", 
            "Análisis Contextual Inteligente", 
            "Respuestas Empáticas",
            "Insights Automáticos",
            "Seguimiento de Sentimientos"
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
                "message": "🚀 Todo funcionando como un reloj suizo",
                "database": "✅ MySQL conectado y respondiendo",
                "ai_personality": "✅ IA conversacional cargada y lista",
                "result": result[0],
                "fun_fact": "¡He procesado miles de consultas y cada una me hace más inteligente!",
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({
                "success": False,
                "message": "❌ Houston, tenemos un problema con la base de datos",
                "database": "❌ MySQL no responde",
                "recommendation": "Revisa la conexión a la base de datos"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "🤖 Mi cerebro tuvo un pequeño glitch, pero ya estoy trabajando en solucionarlo"
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "success": False,
                "response": "🤔 Parece que tu mensaje llegó vacío. ¿Podrías intentar de nuevo?",
                "error": "Mensaje requerido"
            }), 400
        
        message = data['message'].strip()
        role = data.get('role', 'directivo')
        user_id = data.get('user_id', 1)
        
        if not message or message.lower() == 'inicializar_chat':
            return jsonify({
                "success": True,
                "response": "¡Hola! 👋 Soy tu asistente de IA conversacional para DTAI. Me especializo en análisis académicos, pero me encanta charlar sobre cualquier cosa relacionada con educación. Tengo acceso a datos en tiempo real y un montón de algoritmos listos para ayudarte. ¿Qué te tiene curioso hoy?",
                "intent": "inicializacion",
                "personality_note": "Modo conversacional activado 🧠✨"
            })
        
        logger.info(f"💬 Conversación: '{message}' (Usuario: {user_id}, Rol: {role})")
        
        # Obtener y actualizar contexto
        context = get_conversation_context(user_id)
        
        # Clasificación inteligente de intención
        intent = classify_intent_advanced(message, context)
        
        # Generar respuesta conversacional
        response_text = get_conversational_response(intent, message, context, role, user_id)
        
        # Actualizar contexto con análisis de sentimiento
        update_context(user_id, message, intent, response_text)
        
        # Generar recomendaciones inteligentes
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
            "personality_traits": [
                "analytical", "empathetic", "data-driven", 
                "conversational", "solution-oriented"
            ],
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Error en conversación: {e}")
        
        error_responses = [
            "¡Oops! 😅 Mi cerebro de IA acaba de tener un pequeño cortocircuito. Dame un segundo para reinicializar mis neuronas artificiales...",
            "🤖 Error 404: Respuesta inteligente no encontrada... ¡Pero mi sentido del humor sigue funcionando! ¿Puedes intentar reformular tu pregunta?",
            "🔧 Mi sistema está teniendo un momento 'humano' - necesita un café virtual. ¿Podrías intentar de nuevo en un momento?"
        ]
        
        return jsonify({
            "success": False,
            "error": "Error procesando mensaje",
            "response": random.choice(error_responses),
            "debug_info": str(e) if app.debug else "Error interno",
            "suggestion": "Intenta reformular tu pregunta o pregúntame algo más específico",
            "timestamp": datetime.now().isoformat()
        }), 500

def generate_smart_recommendations(intent, context, role):
    """Genera recomendaciones inteligentes basadas en contexto y patrones"""
    recommendations = []
    
    recent_intents = [msg.get('intent') for msg in context['messages'][-5:]]
    
    if intent == 'calificaciones':
        recommendations = [
            "💡 Considera analizar las tendencias temporales de estas calificaciones",
            "📊 ¿Te interesa comparar estos resultados con períodos anteriores?",
            "🎯 Puedo identificar patrones en materias con bajo rendimiento"
        ]
    
    elif intent == 'riesgo':
        recommendations = [
            "⚡ Prioriza casos críticos en las próximas 24-48 horas",
            "📋 Genera un plan de seguimiento personalizado para cada caso",
            "📈 Analiza factores comunes en estudiantes de alto riesgo"
        ]
    
    elif intent == 'estadisticas':
        recommendations = [
            "🔍 Profundiza en métricas que muestren tendencias preocupantes",
            "📊 Compara estos números con benchmarks del sector educativo",
            "💼 Genera un reporte ejecutivo para presentar a directivos"
        ]
    
    # Recomendaciones contextuales basadas en patrones
    if 'riesgo' in recent_intents and 'calificaciones' in recent_intents:
        recommendations.append("🧠 Correlaciona los casos de riesgo con patrones de calificaciones")
    
    if len(context['messages']) > 5:
        recommendations.append("📚 ¿Quieres que resuma los insights clave de nuestra conversación?")
    
    return recommendations[:3]  # Limitar a 3 recomendaciones

@app.route('/api/suggestions', methods=['GET'])
def suggestions():
    role = request.args.get('role', 'directivo')
    
    suggestions_map = {
        'alumno': [
            "Hola, ¿cómo estás hoy?",
            "¿Podrías analizar mis calificaciones actuales?",
            "Me siento un poco abrumado con mis materias",
            "¿Qué estrategias me recomiendas para mejorar?",
            "¿Cómo voy comparado con mis compañeros?",
            "Gracias por toda tu ayuda"
        ],
        'profesor': [
            "¡Buenos días! ¿Cómo van los datos hoy?",
            "¿Qué estudiantes de mis grupos necesitan atención?",
            "¿Puedes analizar el rendimiento de mis clases?",
            "¿Hay patrones preocupantes que deba conocer?",
            "¿Cómo puedo apoyar mejor a mis estudiantes en riesgo?",
            "Necesito recomendaciones para mejorar el engagement"
        ],
        'directivo': [
            "Hola, ¿cómo está el panorama institucional?",
            "Dame un análisis completo del rendimiento académico",
            "¿Cuáles son nuestros principales desafíos actualmente?",
            "¿Qué programas necesitan intervención inmediata?",
            "Genera un reporte ejecutivo con insights clave",
            "¿Hay tendencias que debería conocer para la toma de decisiones?"
        ]
    }
    
    return jsonify({
        "success": True,
        "suggestions": suggestions_map.get(role, suggestions_map['directivo']),
        "role": role,
        "message": f"Sugerencias conversacionales personalizadas para {role}",
        "tip": "¡Recuerda que puedes preguntarme cualquier cosa de forma natural!",
        "personality_note": "Me adapto a tu estilo de comunicación 😊"
    })

@app.route('/api/context/<int:user_id>', methods=['GET'])
def get_context(user_id):
    context = get_conversation_context(user_id)
    
    # Análisis de patrones conversacionales
    intent_patterns = {}
    for msg in context['messages']:
        intent = msg.get('intent', 'unknown')
        intent_patterns[intent] = intent_patterns.get(intent, 0) + 1
    
    return jsonify({
        "success": True,
        "user_id": user_id,
        "conversation_summary": {
            "total_messages": len(context['messages']),
            "last_intent": context['last_intent'],
            "intent_patterns": intent_patterns,
            "session_topics": list(set(context['session_topics'])),
            "conversation_mood": analyze_conversation_mood(context)
        },
        "recent_messages": context['messages'][-5:] if context['messages'] else [],
        "ai_insights": generate_conversation_insights(context)
    })

def analyze_conversation_mood(context):
    """Analiza el mood general de la conversación"""
    if not context['messages']:
        return "neutral"
    
    sentiments = [msg.get('sentiment', 'neutral') for msg in context['messages']]
    positive_count = sentiments.count('positive')
    negative_count = sentiments.count('negative')
    
    if positive_count > negative_count * 1.5:
        return "predominantly_positive"
    elif negative_count > positive_count * 1.5:
        return "needs_support"
    else:
        return "balanced"

def generate_conversation_insights(context):
    """Genera insights sobre los patrones conversacionales"""
    insights = []
    
    if len(context['messages']) > 10:
        insights.append("🔥 Usuario muy activo - alta participación en la conversación")
    
    intent_variety = len(set([msg.get('intent') for msg in context['messages']]))
    if intent_variety > 5:
        insights.append("🧠 Conversación diversa - múltiples temas explorados")
    
    recent_sentiments = [msg.get('sentiment') for msg in context['messages'][-3:]]
    if all(s == 'positive' for s in recent_sentiments):
        insights.append("😊 Tendencia positiva reciente - usuario satisfecho")
    
    return insights

@app.route('/api/context/<int:user_id>', methods=['DELETE'])
def clear_context(user_id):
    if user_id in conversation_contexts:
        del conversation_contexts[user_id]
    
    return jsonify({
        "success": True,
        "message": f"🧹 Contexto limpiado para usuario {user_id}",
        "note": "Conversación reiniciada - empezamos con pizarra en blanco",
        "timestamp": datetime.now().isoformat()
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "🗺️ Endpoint perdido en el ciberespacio",
        "message": "Hmm, parece que te desviaste del camino. Aquí están las rutas disponibles:",
        "available_endpoints": [
            {"path": "/", "description": "Info general del sistema"},
            {"path": "/api/test", "description": "Verificar que todo funcione"},
            {"path": "/api/chat", "description": "Conversar conmigo"},
            {"path": "/api/suggestions", "description": "Obtener sugerencias"}
        ],
        "fun_fact": "¡Este error 404 es más amigable que la mayoría! 😄"
    }), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "error": "🤖 Mi cerebro artificial tuvo un momento existencial",
        "message": "Algo interno falló, pero ya estoy corriendo diagnósticos para solucionarlo",
        "suggestion": "Intenta de nuevo en un momento, o pregúntame algo diferente",
        "timestamp": datetime.now().isoformat()
    }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 Iniciando IA Conversacional Avanzada en puerto {port}")
    logger.info("🧠 Personalidad: Analista de datos entusiasta y conversacional")
    logger.info("✨ Características: Empática, inteligente, y naturalmente curiosa")
    app.run(host='0.0.0.0', port=port, debug=False)