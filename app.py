from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
from datetime import datetime

from database.connection import DatabaseConnection
from models.conversation_ai import ConversationAI
from utils.text_processor import TextProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

db = DatabaseConnection()
ai = ConversationAI()
processor = TextProcessor()

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "FUNCIONANDO",
        "message": "IA Conversacional con MySQL - Railway",
        "version": "2.0.0",
        "features": ["Conversacion Natural", "Base de Datos Real", "Contexto Mantenido"],
        "endpoints": ["/api/test", "/api/chat", "/api/suggestions"],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/test', methods=['GET'])
def test():
    try:
        result = db.execute_query("SELECT 1 as test, 'Conexion exitosa a MySQL' as mensaje, NOW() as tiempo")
        
        if result:
            return jsonify({
                "success": True,
                "message": "Sistema completamente funcional",
                "database": "MySQL Conectado",
                "conversation": "IA Conversacional Activa",
                "result": result[0],
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({
                "success": False,
                "message": "Error de conexion a BD",
                "database": "MySQL Desconectado"
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
                "response": "Parece que no escribiste nada. En que te puedo ayudar?",
                "intent": "mensaje_vacio"
            })
        
        logger.info(f"Chat conversacional: {message} (role: {role}, user: {user_id})")
        
        response_data = ai.process_message(message, role, user_id)
        
        return jsonify({
            "success": True,
            **response_data,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error chat: {e}")
        return jsonify({
            "success": False,
            "error": "Error procesando mensaje",
            "response": "Lo siento, tuve un problema procesando tu mensaje. Puedes intentar de nuevo?",
            "details": str(e)
        }), 500

@app.route('/api/suggestions', methods=['GET'])
def suggestions():
    role = request.args.get('role', 'alumno')
    
    suggestions_map = {
        'alumno': [
            "Hola, como estas?",
            "Cuales son mis calificaciones?",
            "Como van mis materias este cuatrimestre?",
            "Me siento preocupado por mis notas",
            "Que puedes hacer por mi?",
            "Gracias por tu ayuda"
        ],
        'profesor': [
            "Buenos dias!",
            "Que alumnos estan en riesgo?",
            "Cuales son mis grupos asignados?",
            "Hay reportes urgentes?",
            "Como puedo ayudar a mis estudiantes?",
            "Necesito estadisticas de mi clase"
        ],
        'directivo': [
            "Hola, como va todo?",
            "Cuales son las estadisticas generales?",
            "Como va el rendimiento por carrera?",
            "Que alumnos necesitan atencion urgente?",
            "Dame un resumen del sistema",
            "Hay algo preocupante que deba saber?"
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
    context = ai.get_user_context(user_id)
    return jsonify({
        "success": True,
        "user_id": user_id,
        "messages_count": len(context['messages']),
        "last_intent": context['last_intent'],
        "recent_messages": context['messages'][-3:] if context['messages'] else []
    })

@app.route('/api/context/<int:user_id>', methods=['DELETE'])
def clear_context(user_id):
    ai.clear_user_context(user_id)
    return jsonify({
        "success": True,
        "message": f"Contexto limpiado para usuario {user_id}"
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint no encontrado", 
        "message": "Estas seguro de la URL? Aqui estan los endpoints disponibles:",
        "endpoints": ["/", "/api/test", "/api/chat", "/api/suggestions"]
    }), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "error": "Error interno del servidor",
        "message": "Algo salio mal, pero trabajare en arreglarlo"
    }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Iniciando IA Conversacional en puerto {port}")
    app.run(host='0.0.0.0', port=port, debug=False)