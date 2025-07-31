from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
import mysql.connector
from datetime import datetime
import re
import random

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear aplicación Flask
app = Flask(__name__)
CORS(app)

# Contexto de conversación simple (en memoria)
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
        return connection
    except Exception as e:
        logger.error(f"Error BD: {e}")
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
        return result
    except Exception as e:
        logger.error(f"Error query: {e}")
        if connection:
            connection.close()
        return None

def get_conversation_context(user_id):
    """Obtener contexto de conversación"""
    if user_id not in conversation_contexts:
        conversation_contexts[user_id] = {
            'messages': [],
            'last_intent': None,
            'user_name': None,
            'mood': 'neutral'
        }
    return conversation_contexts[user_id]

def update_context(user_id, message, intent, response):
    """Actualizar contexto"""
    context = get_conversation_context(user_id)
    context['messages'].append({
        'user': message,
        'bot': response,
        'intent': intent,
        'time': datetime.now()
    })
    context['last_intent'] = intent
    
    # Mantener solo últimas 5 conversaciones
    if len(context['messages']) > 5:
        context['messages'] = context['messages'][-5:]

def classify_intent(message, context):
    """Clasificador conversacional inteligente"""
    msg = message.lower().strip()
    
    # Saludos y cortesías
    if any(w in msg for w in ['hola', 'hello', 'hi', 'buenos días', 'buenas tardes', 'buenas noches']):
        return 'saludo'
    
    if any(w in msg for w in ['gracias', 'thank you', 'te lo agradezco']):
        return 'agradecimiento'
    
    if any(w in msg for w in ['adiós', 'bye', 'hasta luego', 'nos vemos']):
        return 'despedida'
    
    # Estados emocionales
    if any(w in msg for w in ['triste', 'deprimido', 'mal', 'terrible', 'horrible']):
        return 'emocional_negativo'
    
    if any(w in msg for w in ['feliz', 'contento', 'bien', 'genial', 'excelente']):
        return 'emocional_positivo'
    
    # Preguntas sobre la IA
    if any(w in msg for w in ['cómo estás', 'que tal', 'como estas', 'how are you']):
        return 'pregunta_estado'
    
    if any(w in msg for w in ['quién eres', 'que eres', 'who are you', 'qué puedes hacer']):
        return 'pregunta_identidad'
    
    # Consultas académicas
    if any(w in msg for w in ['calificaciones', 'notas', 'puntuaciones', 'resultados']):
        return 'calificaciones'
    
    if any(w in msg for w in ['riesgo', 'problema', 'dificultad', 'ayuda']):
        return 'riesgo'
    
    if any(w in msg for w in ['promedio', 'carrera', 'rendimiento']):
        return 'promedio'
    
    if any(w in msg for w in ['estadisticas', 'resumen', 'general', 'números']):
        return 'estadisticas'
    
    # Seguimientos contextuales
    if context['last_intent'] and any(w in msg for w in ['más', 'otro', 'también', 'además']):
        return f"mas_{context['last_intent']}"
    
    if any(w in msg for w in ['sí', 'si', 'claro', 'ok', 'está bien']):
        return 'afirmacion'
    
    if any(w in msg for w in ['no', 'nada', 'mejor no']):
        return 'negacion'
    
    return 'conversacion_general'

def get_conversational_response(intent, message, context, role='alumno', user_id=1):
    """Generar respuesta conversacional inteligente"""
    
    responses = {
        'saludo': [
            "¡Hola! 😊 ¿Cómo estás? Soy tu asistente virtual académico.",
            "¡Buenos días! 🌟 ¿En qué te puedo ayudar hoy?",
            "¡Hola! Me alegra verte por aquí. ¿Qué necesitas saber?",
            "¡Hey! 👋 ¿Cómo van las cosas? ¿En qué te puedo asistir?"
        ],
        
        'pregunta_estado': [
            "¡Muy bien, gracias por preguntar! 🤖 Estoy aquí para ayudarte con tus consultas académicas.",
            "¡Excelente! Funcionando al 100% y listo para ayudarte. ¿Qué necesitas?",
            "¡Perfecto! Siempre contento de poder ayudar a estudiantes como tú. ¿En qué te apoyo?"
        ],
        
        'pregunta_identidad': [
            "Soy tu asistente virtual académico 🤖. Puedo ayudarte con calificaciones, reportes de riesgo, estadísticas y más. ¡Pregúntame lo que necesites!",
            "¡Hola! Soy una IA especializada en educación. Mi trabajo es ayudarte con tus consultas académicas y darte recomendaciones personalizadas.",
            "Soy tu compañero digital para todo lo académico 📚. Consulto la base de datos en tiempo real para darte información actualizada."
        ],
        
        'emocional_negativo': [
            "Lo siento mucho que te sientas así 😔. Recuerda que los desafíos académicos son temporales y siempre hay oportunidades de mejorar. ¿Te gustaría que revisemos tu situación académica juntos?",
            "Entiendo que puede ser frustrante 💙. Estoy aquí para apoyarte. ¿Hay algo específico que te preocupa? Podemos buscar soluciones juntos.",
            "Sé que a veces puede ser abrumador 🫂. Pero recuerda que cada dificultad es una oportunidad de crecimiento. ¿En qué área necesitas más apoyo?"
        ],
        
        'emocional_positivo': [
            "¡Me alegra mucho escuchar eso! 😄 ¡Sigue así! ¿Hay algo en lo que pueda ayudarte para mantener ese buen ánimo?",
            "¡Qué bueno! 🎉 La actitud positiva es clave para el éxito académico. ¿Quieres revisar cómo van tus materias?",
            "¡Excelente! 🌟 Me encanta ver estudiantes motivados. ¿En qué más puedo apoyarte?"
        ],
        
        'agradecimiento': [
            "¡De nada! 😊 Para eso estoy aquí. ¿Necesitas algo más?",
            "¡Un placer ayudarte! 🤗 Cualquier otra cosa que necesites, solo pregunta.",
            "¡Siempre es un gusto! 👍 ¿Hay algo más en lo que te pueda asistir?"
        ],
        
        'despedida': [
            "¡Hasta luego! 👋 Que tengas un excelente día. Aquí estaré cuando me necesites.",
            "¡Nos vemos! 😊 ¡Que te vaya súper bien en tus estudios!",
            "¡Adiós! 🌟 Recuerda que siempre puedes contar conmigo para tus consultas académicas."
        ],
        
        'afirmacion': [
            "¡Perfecto! 👍 ¿En qué más te puedo ayudar?",
            "¡Genial! 😊 ¿Hay algo más que quieras saber?",
            "¡Excelente! ¿Qué más necesitas?"
        ],
        
        'negacion': [
            "Entiendo 👌. Si cambias de opinión o necesitas algo más, aquí estaré.",
            "Sin problema 😊. ¿Hay algo diferente en lo que te pueda ayudar?",
            "Está bien 👍. Cualquier otra consulta que tengas, solo dímelo."
        ]
    }
    
    # Respuestas conversacionales
    if intent in responses:
        return random.choice(responses[intent])
    
    # Consultas académicas con datos
    elif intent == 'calificaciones':
        query = """
        SELECT a.nombre, c.calificacion_final, c.estatus
        FROM calificaciones c
        JOIN asignaturas a ON c.asignatura_id = a.id
        JOIN alumnos al ON c.alumno_id = al.id
        WHERE al.usuario_id = %s
        LIMIT 5
        """
        data = execute_query(query, [user_id])
        
        if data:
            response = "📊 **Estadísticas del Sistema:**\n\n"
        for name, query in queries:
            result = execute_query(query)
            if result:
                response += f"• {name}: {result[0]['total']}\n"
        
        return response
    
    else:
        return f"🤖 Hola! Recibí tu mensaje. El sistema está funcionando correctamente. ¿En qué te puedo ayudar?"

@app.route('/', methods=['GET'])
def home():
    """Página principal"""
    return jsonify({
        "status": "✅ FUNCIONANDO",
        "message": "IA Conversacional - Railway",
        "version": "1.0.0",
        "endpoints": ["/api/test", "/api/chat", "/api/suggestions"],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/test', methods=['GET'])
def test():
    """Test de conexión"""
    try:
        # Test BD
        result = execute_query("SELECT 1 as test, 'Conexión exitosa' as mensaje")
        
        if result:
            return jsonify({
                "success": True,
                "message": "🚀 Sistema completamente funcional",
                "database": "✅ Conectado",
                "result": result[0],
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({
                "success": False,
                "message": "❌ Error de conexión a BD",
                "database": "❌ Desconectado"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error en test del sistema"
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat principal"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({"error": "Mensaje requerido"}), 400
        
        message = data['message']
        role = data.get('role', 'alumno')
        user_id = data.get('user_id', 1)
        
        logger.info(f"Chat: {message} (role: {role})")
        
        # Clasificar y responder
        intent = classify_intent(message)
        response_text = get_response(intent, role, user_id)
        
        return jsonify({
            "success": True,
            "response": response_text,
            "intent": intent,
            "role": role,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error chat: {e}")
        return jsonify({
            "success": False,
            "error": "Error procesando mensaje",
            "details": str(e)
        }), 500

@app.route('/api/suggestions', methods=['GET'])
def suggestions():
    """Sugerencias por rol"""
    role = request.args.get('role', 'alumno')
    
    suggestions_map = {
        'alumno': [
            "¿Cuáles son mis calificaciones?",
            "¿Cómo van mis materias?",
            "¿Tengo algún problema académico?"
        ],
        'profesor': [
            "¿Qué alumnos están en riesgo?",
            "¿Cuáles son mis grupos?",
            "¿Hay reportes pendientes?"
        ],
        'directivo': [
            "¿Cuáles son las estadísticas generales?",
            "¿Cómo va el rendimiento por carrera?",
            "¿Qué alumnos necesitan atención?"
        ]
    }
    
    return jsonify({
        "success": True,
        "suggestions": suggestions_map.get(role, suggestions_map['alumno']),
        "role": role
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint no encontrado"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Error interno del servidor"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚂 Iniciando servidor en puerto {port}")
    app.run(host='0.0.0.0', port=port, debug=False)**Aquí tienes tus calificaciones:**\n\n"
            total_promedio = 0
            materias_count = 0
            
            for row in data:
                if row['calificacion_final']:
                    total_promedio += row['calificacion_final']
                    materias_count += 1
                
                status = "✅" if row['estatus'] == 'aprobado' else "📝" if row['estatus'] == 'cursando' else "❌"
                grade = f"{row['calificacion_final']:.1f}" if row['calificacion_final'] else 'Sin calificar'
                response += f"{status} **{row['nombre']}**: {grade}\n"
            
            if materias_count > 0:
                promedio_actual = total_promedio / materias_count
                response += f"\n📈 **Tu promedio actual**: {promedio_actual:.2f}\n"
                
                if promedio_actual >= 9.0:
                    response += "\n🌟 ¡Excelente trabajo! Sigues por muy buen camino."
                elif promedio_actual >= 8.0:
                    response += "\n👍 ¡Muy bien! Tu rendimiento es bueno."
                elif promedio_actual >= 7.0:
                    response += "\n💪 Vas bien, pero hay espacio para mejorar."
                else:
                    response += "\n⚠️ Necesitas enfocarte más en tus estudios. ¿Te gustaría algunas recomendaciones?"
            
            response += "\n\n❓ ¿Te gustaría ver estrategias para mejorar en alguna materia específica?"
            return response
        else:
            return "📚 No encontré calificaciones registradas para ti. ¿Es tu primer cuatrimestre? Si crees que es un error, puedes contactar a tu coordinador académico. 😊"
    
    elif intent == 'riesgo':
        query = """
        SELECT u.nombre, u.apellido, rr.nivel_riesgo, rr.tipo_riesgo, rr.descripcion
        FROM reportes_riesgo rr
        JOIN alumnos al ON rr.alumno_id = al.id
        JOIN usuarios u ON al.usuario_id = u.id
        WHERE rr.estado IN ('abierto', 'en_proceso')
        ORDER BY CASE rr.nivel_riesgo 
            WHEN 'critico' THEN 1 
            WHEN 'alto' THEN 2 
            WHEN 'medio' THEN 3 
            ELSE 4 END
        LIMIT 8
        """
        data = execute_query(query)
        
        if data:
            criticos = len([d for d in data if d['nivel_riesgo'] == 'critico'])
            response = f"🚨 **Alumnos que necesitan atención** ({len(data)} casos activos):\n\n"
            
            for row in data:
                emoji = "🔴" if row['nivel_riesgo'] == 'critico' else "🟡" if row['nivel_riesgo'] == 'alto' else "🟠"
                response += f"{emoji} **{row['nombre']} {row['apellido']}**\n"
                response += f"   Riesgo: {row['nivel_riesgo']} ({row['tipo_riesgo']})\n"
                if row['descripcion']:
                    response += f"   📝 {row['descripcion'][:80]}...\n"
                response += "\n"
            
            if criticos > 0:
                response += f"\n🚨 **ATENCIÓN URGENTE**: {criticos} estudiantes en riesgo crítico requieren intervención inmediata.\n"
                response += "\n💡 **Recomendaciones**:\n"
                response += "• Contactar a padres/tutores hoy mismo\n"
                response += "• Programar citas individuales esta semana\n"
                response += "• Evaluar apoyos adicionales (económicos, psicológicos)\n"
            
            response += "\n❓ ¿Te gustaría que genere un plan de intervención detallado?"
            return response
        else:
            return "✅ ¡Excelente noticia! No hay alumnos en situación de riesgo actualmente. El sistema educativo está funcionando bien. 😊"
    
    elif intent == 'conversacion_general':
        general_responses = [
            f"Interesante lo que me dices: '{message}' 🤔. Como tu asistente académico, ¿hay algo relacionado con tus estudios en lo que te pueda ayudar?",
            f"Entiendo tu mensaje sobre '{message}' 😊. ¿Te gustaría que revisemos algo específico de tu situación académica?",
            f"Gracias por compartir eso conmigo. Como asistente educativo, estoy aquí para apoyarte. ¿Hay alguna consulta académica que tengas?",
            f"Me parece muy interesante lo que mencionas. ¿Podemos enfocar nuestra conversación en cómo te puedo ayudar con tus estudios? 📚"
        ]
        return random.choice(general_responses)
    
    # Default conversacional
    return f"Hmm, entiendo que me dices '{message}' 🤔. Como tu asistente académico, ¿en qué puedo ayudarte específicamente? Puedo consultar calificaciones, reportes de riesgo, estadísticas y más. 😊"

@app.route('/', methods=['GET'])
def home():
    """Página principal"""
    return jsonify({
        "status": "✅ FUNCIONANDO",
        "message": "IA Conversacional Inteligente - Railway",
        "version": "2.0.0",
        "features": ["Conversación Natural", "Contexto Mantenido", "Consultas BD", "Respuestas Emocionales"],
        "endpoints": ["/api/test", "/api/chat", "/api/suggestions"],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/test', methods=['GET'])
def test():
    """Test de conexión"""
    try:
        # Test BD
        result = execute_query("SELECT 1 as test, 'Conexión exitosa' as mensaje")
        
        if result:
            return jsonify({
                "success": True,
                "message": "🚀 Sistema completamente funcional",
                "database": "✅ Conectado",
                "conversation": "✅ IA Conversacional Activa",
                "result": result[0],
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({
                "success": False,
                "message": "❌ Error de conexión a BD",
                "database": "❌ Desconectado"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error en test del sistema"
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat conversacional inteligente"""
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
                "response": "😅 Parece que no escribiste nada. ¿En qué te puedo ayudar?",
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
    """Sugerencias conversacionales por rol"""
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
    """Ver contexto de conversación"""
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
    """Limpiar contexto de conversación"""
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
    app.run(host='0.0.0.0', port=port, debug=False)**Estadísticas del Sistema:**\n\n"
        for name, query in queries:
            result = execute_query(query)
            if result:
                response += f"• {name}: {result[0]['total']}\n"
        
        return response
    
    else:
        return f"🤖 Hola! Recibí tu mensaje. El sistema está funcionando correctamente. ¿En qué te puedo ayudar?"

@app.route('/', methods=['GET'])
def home():
    """Página principal"""
    return jsonify({
        "status": "✅ FUNCIONANDO",
        "message": "IA Conversacional - Railway",
        "version": "1.0.0",
        "endpoints": ["/api/test", "/api/chat", "/api/suggestions"],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/test', methods=['GET'])
def test():
    """Test de conexión"""
    try:
        # Test BD
        result = execute_query("SELECT 1 as test, 'Conexión exitosa' as mensaje")
        
        if result:
            return jsonify({
                "success": True,
                "message": "🚀 Sistema completamente funcional",
                "database": "✅ Conectado",
                "result": result[0],
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({
                "success": False,
                "message": "❌ Error de conexión a BD",
                "database": "❌ Desconectado"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error en test del sistema"
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat principal"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({"error": "Mensaje requerido"}), 400
        
        message = data['message']
        role = data.get('role', 'alumno')
        user_id = data.get('user_id', 1)
        
        logger.info(f"Chat: {message} (role: {role})")
        
        # Clasificar y responder
        intent = classify_intent(message)
        response_text = get_response(intent, role, user_id)
        
        return jsonify({
            "success": True,
            "response": response_text,
            "intent": intent,
            "role": role,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error chat: {e}")
        return jsonify({
            "success": False,
            "error": "Error procesando mensaje",
            "details": str(e)
        }), 500

@app.route('/api/suggestions', methods=['GET'])
def suggestions():
    """Sugerencias por rol"""
    role = request.args.get('role', 'alumno')
    
    suggestions_map = {
        'alumno': [
            "¿Cuáles son mis calificaciones?",
            "¿Cómo van mis materias?",
            "¿Tengo algún problema académico?"
        ],
        'profesor': [
            "¿Qué alumnos están en riesgo?",
            "¿Cuáles son mis grupos?",
            "¿Hay reportes pendientes?"
        ],
        'directivo': [
            "¿Cuáles son las estadísticas generales?",
            "¿Cómo va el rendimiento por carrera?",
            "¿Qué alumnos necesitan atención?"
        ]
    }
    
    return jsonify({
        "success": True,
        "suggestions": suggestions_map.get(role, suggestions_map['alumno']),
        "role": role
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint no encontrado"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Error interno del servidor"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚂 Iniciando servidor en puerto {port}")
    app.run(host='0.0.0.0', port=port, debug=False)