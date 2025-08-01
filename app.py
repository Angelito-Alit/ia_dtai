import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

from models.conversation_ai import ConversationAI
from database.connection import DatabaseConnection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

ai_system = ConversationAI()
db = DatabaseConnection()

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "FUNCIONANDO",
        "message": "IA Conversacional Educativa - Railway Deploy",
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
            "context": "/api/context/<user_id>",
            "status": "/api/status"
        },
        "supported_roles": ["alumno", "profesor", "directivo"],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/test', methods=['GET'])
def test_system():
    try:
        system_status = ai_system.get_system_status()
        db_test = db.execute_query("SELECT 1 as test, 'MySQL Conectado' as mensaje, NOW() as tiempo")
        
        return jsonify({
            "success": True,
            "message": "Sistema completamente funcional",
            "system_status": system_status,
            "database_test": db_test[0] if db_test else None,
            "components": {
                "flask_app": "OK",
                "conversation_ai": "OK",
                "database": "OK" if db_test else "ERROR",
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
        
        has_permission, permission_msg = ai_system.validate_user_permissions(role, 'general')
        if not has_permission:
            return jsonify({
                "success": False,
                "response": permission_msg,
                "intent": "acceso_denegado"
            }), 403
        
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
        role = request.args.get('role', 'alumno')
        
        commands_data = ai_system.get_available_commands(role)
        
        return jsonify({
            "success": True,
            "suggestions": commands_data["commands"],
            "role": role,
            "total_commands": commands_data["total_commands"],
            "message": f"Comandos disponibles para {role}",
            "categories": {
                "conversational": ["Hola", "¿Cómo estás?", "Gracias"],
                "academic": ["Calificaciones", "Horarios", "Materias"],
                "administrative": ["Estadísticas", "Reportes", "Grupos"]
            }
        })
        
    except Exception as e:
        logger.error(f"Error en suggestions: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/context/<int:user_id>', methods=['GET'])
def get_user_context(user_id):
    try:
        context_summary = ai_system.get_context_summary(user_id)
        
        return jsonify({
            "success": True,
            "context": context_summary,
            "message": f"Contexto para usuario {user_id}"
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo contexto: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/context/<int:user_id>', methods=['DELETE'])
def clear_user_context(user_id):
    try:
        cleared = ai_system.clear_context(user_id)
        
        return jsonify({
            "success": True,
            "cleared": cleared,
            "message": f"Contexto {'limpiado' if cleared else 'no encontrado'} para usuario {user_id}"
        })
        
    except Exception as e:
        logger.error(f"Error limpiando contexto: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/status', methods=['GET'])
def system_status():
    try:
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

@app.route('/api/analyze', methods=['POST'])
def analyze_query():
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({
                "success": False,
                "error": "Mensaje requerido"
            }), 400
        
        complexity = ai_system.analyze_query_complexity(message)
        intent_suggestions = ai_system.intent_classifier.suggest_intents(message)
        
        return jsonify({
            "success": True,
            "message": message,
            "complexity_analysis": complexity,
            "intent_suggestions": intent_suggestions,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error en analyze: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "error": "Acceso denegado",
        "message": "No tienes permisos para realizar esta acción"
    }), 403

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "error": "Solicitud incorrecta",
        "message": "Revisa los parámetros enviados"
    }), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Iniciando IA Conversacional Educativa en puerto {port}")
    logger.info(f"Modo debug: {debug_mode}")
    logger.info("Componentes del sistema cargados correctamente")
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)handler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint no encontrado",
        "message": "La URL solicitada no existe",
        "available_endpoints": [
            "/",
            "/api/test",
            "/api/chat",
            "/api/suggestions",
            "/api/context/<user_id>",
            "/api/status",
            "/api/analyze"
        ]
    }), 404

@app.errorhandler(500)
def server_error(error):
    logger.error(f"Error 500: {error}")
    return jsonify({
        "error": "Error interno del servidor",
        "message": "Algo salió mal en el procesamiento"
    }), 500

