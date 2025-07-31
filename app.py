from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging

from core.database_manager import DatabaseManager
from core.conversation_engine import ConversationEngine
from core.intent_classifier import IntentClassifier
from core.response_generator import ResponseGenerator
from utils.context_manager import ContextManager
from utils.analytics import AnalyticsManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Inicializar componentes principales
db_manager = DatabaseManager()
context_manager = ContextManager()
intent_classifier = IntentClassifier() 
response_generator = ResponseGenerator(db_manager)
conversation_engine = ConversationEngine(db_manager, context_manager, intent_classifier, response_generator)
analytics_manager = AnalyticsManager()

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "ACTIVO",
        "system": "IA Conversacional DTAI",
        "version": "5.0.0",
        "description": "Sistema inteligente de análisis académico conversacional",
        "capabilities": [
            "Análisis académico integral",
            "Conversación natural fluida", 
            "Reportes ejecutivos automatizados",
            "Análisis predictivo educativo",
            "Gestión de alertas tempranas",
            "Insights estratégicos personalizados"
        ],
        "endpoints": {
            "chat": "/api/chat - Interfaz de conversación principal",
            "test": "/api/test - Verificación del sistema",
            "suggestions": "/api/suggestions - Sugerencias contextuales",
            "context": "/api/context/{user_id} - Gestión de contexto",
            "analytics": "/api/analytics - Métricas del sistema"
        }
    })

@app.route('/api/test', methods=['GET'])
def test_system():
    try:
        db_status = db_manager.test_connection()
        
        if db_status['success']:
            return jsonify({
                "success": True,
                "message": "Sistema completamente operacional",
                "database": "Conectado y funcionando correctamente",
                "ai_engine": "Cargado y optimizado",
                "conversation_engine": "Activo y procesando",
                "performance": "Óptimo",
                "test_result": db_status['data'],
                "timestamp": db_status['timestamp']
            })
        else:
            return jsonify({
                "success": False,
                "message": "Problema detectado en conexión de base de datos",
                "database": "Error de conectividad",
                "recommendation": "Verificar configuración de base de datos",
                "error": db_status.get('error')
            }), 500
            
    except Exception as e:
        logger.error(f"Error en test del sistema: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error interno durante verificación del sistema"
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "success": False,
                "response": "No recibí tu mensaje correctamente. ¿Podrías intentar enviarlo de nuevo?",
                "error": "Mensaje no válido"
            }), 400
        
        message = data['message'].strip()
        role = data.get('role', 'directivo')
        user_id = data.get('user_id', 1)
        
        if not message:
            return jsonify({
                "success": True,
                "response": "Parece que no escribiste nada. ¿En qué puedo ayudarte hoy? Puedo analizar estadísticas, revisar casos de riesgo, generar reportes, o responder cualquier pregunta sobre los datos académicos.",
                "intent": "mensaje_vacio",
                "suggestions": conversation_engine.get_contextual_suggestions(role)
            })
        
        # Procesar mensaje a través del motor conversacional
        response_data = conversation_engine.process_message(message, role, user_id)
        
        # Registrar analytics
        analytics_manager.log_interaction(user_id, message, response_data.get('intent'))
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error procesando chat: {e}")
        
        error_response = conversation_engine.generate_error_response(str(e))
        
        return jsonify({
            "success": False,
            "error": "Error procesando mensaje",
            "response": error_response,
            "suggestion": "Intenta reformular tu pregunta o pregúntame algo más específico sobre los datos académicos"
        }), 500

@app.route('/api/suggestions', methods=['GET'])
def get_suggestions():
    role = request.args.get('role', 'directivo')
    context_type = request.args.get('context', 'general')
    
    suggestions = conversation_engine.get_suggestions_by_role(role, context_type)
    
    return jsonify({
        "success": True,
        "suggestions": suggestions,
        "role": role,
        "context": context_type,
        "total_suggestions": len(suggestions)
    })

@app.route('/api/context/<int:user_id>', methods=['GET'])
def get_user_context(user_id):
    try:
        context_data = context_manager.get_detailed_context(user_id)
        analytics_data = analytics_manager.get_user_analytics(user_id)
        
        return jsonify({
            "success": True,
            "user_id": user_id,
            "context": context_data,
            "analytics": analytics_data,
            "conversation_insights": conversation_engine.generate_conversation_insights(context_data)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error obteniendo contexto del usuario"
        }), 500

@app.route('/api/context/<int:user_id>', methods=['DELETE'])
def clear_user_context(user_id):
    try:
        context_manager.clear_context(user_id)
        analytics_manager.reset_user_session(user_id)
        
        return jsonify({
            "success": True,
            "message": f"Contexto limpiado para usuario {user_id}",
            "note": "Nueva sesión iniciada con historial limpio"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error limpiando contexto"
        }), 500

@app.route('/api/analytics', methods=['GET'])
def get_system_analytics():
    try:
        system_analytics = analytics_manager.get_system_analytics()
        conversation_stats = conversation_engine.get_system_stats()
        
        return jsonify({
            "success": True,
            "system_analytics": system_analytics,
            "conversation_stats": conversation_stats,
            "database_stats": db_manager.get_connection_stats()
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
        "error": "Ruta no encontrada",
        "message": "El endpoint que buscas no existe en el sistema",
        "available_endpoints": [
            {"path": "/", "method": "GET", "description": "Información del sistema"},
            {"path": "/api/test", "method": "GET", "description": "Verificar estado del sistema"},
            {"path": "/api/chat", "method": "POST", "description": "Conversación con IA"},
            {"path": "/api/suggestions", "method": "GET", "description": "Obtener sugerencias"},
            {"path": "/api/context/{user_id}", "method": "GET/DELETE", "description": "Gestionar contexto"},
            {"path": "/api/analytics", "method": "GET", "description": "Analytics del sistema"}
        ],
        "suggestion": "Verifica la URL y el método HTTP utilizado"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Error interno del sistema",
        "message": "El sistema experimentó un problema interno",
        "suggestion": "Intenta de nuevo en unos momentos",
        "support": "Si el problema persiste, contacta al equipo de soporte técnico"
    }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"=== Iniciando Sistema IA Conversacional DTAI ===")
    logger.info(f"Puerto: {port}")
    logger.info(f"Modo: {'Desarrollo' if app.debug else 'Producción'}")
    logger.info(f"Componentes: Motor conversacional, Base de datos, Analytics")
    logger.info("============================================")
    
    app.run(host='0.0.0.0', port=port, debug=False)