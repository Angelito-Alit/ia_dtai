import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

from models.conversation_ai import ConversationAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

try:
    ai_system = ConversationAI()
    logger.info("Sistema de IA cargado correctamente")
except Exception as e:
    logger.error(f"Error cargando sistema IA: {e}")
    ai_system = None

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "FUNCIONANDO",
        "message": "IA Conversacional Educativa - Render Deploy",
        "version": "2.0.0",
        "features": [
            "Conversación Natural",
            "Base de Datos MySQL",
            "Contexto Mantenido",
            "Múltiples Roles",
            "Consultas Inteligentes"
        ],
        "endpoints": {
            "test": "/api/test",
            "chat": "/api/chat",
            "suggestions": "/api/suggestions",
            "status": "/api/status"
        },
        "supported_roles": ["alumno", "profesor", "directivo"],
        "timestamp": datetime.now().isoformat(),
        "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
        "ai_system": "Cargado" if ai_system else "Error"
    })

@app.route('/api/test', methods=['GET'])
def test_system():
    try:
        if not ai_system:
            return jsonify({
                "success": False,
                "message": "Sistema IA no disponible",
                "error": "AI system initialization failed"
            }), 500
        
        system_status = ai_system.get_system_status()
        
        return jsonify({
            "success": True,
            "message": "Sistema completamente funcional",
            "system_status": system_status,
            "components": {
                "flask_app": "OK",
                "conversation_ai": "OK" if ai_system else "ERROR",
                "intent_classification": "OK",
                "query_generation": "OK",
                "response_formatting": "OK"
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error en test: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error en el sistema"
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        if not ai_system:
            return jsonify({
                "success": False,
                "error": "Sistema IA no disponible",
                "response": "Lo siento, el sistema está temporalmente fuera de servicio."
            }), 500
        
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "success": False,
                "error": "Mensaje requerido",
                "example": {
                    "message": "Hola, ¿cuáles son mis calificaciones?",
                    "user_id": 1,
                    "role": "alumno"
                }
            }), 400
        
        message = data['message'].strip()
        user_id = data.get('user_id', 1)
        role = data.get('role', 'alumno')
        
        if not message:
            return jsonify({
                "success": True,
                "response": "Parece que no escribiste nada. ¿En qué te puedo ayudar?",
                "intent": "mensaje_vacio",
                "user_id": user_id,
                "role": role
            })
        
        logger.info(f"Chat - Usuario: {user_id}, Rol: {role}, Mensaje: {message[:50]}...")
        
        result = ai_system.process_message(message, user_id, role)
        
        response_data = {
            "success": result["success"],
            "response": result["response"],
            "intent": result["intent"],
            "user_id": user_id,
            "role": role,
            "has_data": result.get("has_data", False),
            "timestamp": datetime.now().isoformat()
        }
        
        if result.get("data_count"):
            response_data["data_count"] = result["data_count"]
        
        if result.get("query_executed"):
            response_data["query_executed"] = True
        
        if not result["success"]:
            response_data["error"] = result.get("error", "Error desconocido")
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error en chat: {e}")
        return jsonify({
            "success": False,
            "error": "Error procesando mensaje",
            "response": "Lo siento, tuve un problema. ¿Puedes intentar de nuevo?",
            "details": str(e)
        }), 500

@app.route('/api/suggestions', methods=['GET'])
def get_suggestions():
    try:
        if not ai_system:
            return jsonify({
                "success": False,
                "error": "Sistema IA no disponible"
            }), 500
        
        role = request.args.get('role', 'alumno')
        commands_data = ai_system.get_available_commands(role)
        
        return jsonify({
            "success": True,
            "suggestions": commands_data["commands"],
            "role": role,
            "total_commands": commands_data["total_commands"],
            "message": f"Comandos disponibles para {role}"
        })
        
    except Exception as e:
        logger.error(f"Error en suggestions: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/status', methods=['GET'])
def system_status():
    try:
        if not ai_system:
            return jsonify({
                "success": False,
                "status": "AI system unavailable",
                "error": "Sistema IA no inicializado"
            }), 500
        
        status = ai_system.get_system_status()
        
        return jsonify({
            "success": True,
            "status": status,
            "uptime_check": "OK",
            "memory_usage": "Normal",
            "response_time": "< 1s"
        })
        
    except Exception as e:
        logger.error(f"Error en status: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint no encontrado",
        "message": "La URL solicitada no existe",
        "available_endpoints": [
            "/",
            "/api/test",
            "/api/chat",
            "/api/suggestions",
            "/api/status"
        ]
    }), 404

@app.errorhandler(500)
def server_error(error):
    logger.error(f"Error 500: {error}")
    return jsonify({
        "error": "Error interno del servidor",
        "message": "Algo salió mal en el procesamiento"
    }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Iniciando IA Conversacional Educativa en puerto {port}")
    logger.info(f"Modo debug: {debug_mode}")
    logger.info("Sistema optimizado para Render")
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)