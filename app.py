from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
import traceback
from datetime import datetime
import sys

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Crear aplicación Flask
app = Flask(__name__)
CORS(app, origins=["*"])

# Variables globales para IA
ai_instance = None
db_connection = None

def initialize_ai():
    """Inicializar la IA completa con ML"""
    global ai_instance, db_connection
    
    try:
        logger.info("Inicializando IA conversacional completa...")
        
        # Importar módulos después de instalar dependencias
        from database.connection import DatabaseConnection
        from models.conversation_ai import ConversationAI
        
        # Inicializar conexión a la base de datos
        db_connection = DatabaseConnection()
        
        # Test de conexión
        if not db_connection.test_connection():
            raise Exception("No se pudo conectar a la base de datos")
        
        # Inicializar la IA
        ai_instance = ConversationAI(db_connection)
        ai_instance.initialize()
        
        logger.info("IA inicializada correctamente con ML")
        return True
        
    except ImportError as e:
        logger.error(f"Error importando módulos: {e}")
        logger.info("Algunos módulos pueden estar instalándose...")
        return False
    except Exception as e:
        logger.error(f"Error inicializando IA: {e}")
        logger.error(traceback.format_exc())
        return False

def get_ai_instance():
    """Obtener instancia de IA (lazy loading)"""
    global ai_instance
    
    if ai_instance is None:
        if not initialize_ai():
            raise Exception("No se pudo inicializar la IA")
    
    return ai_instance

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "message": "IA Conversacional con ML - Railway",
        "version": "2.0.0",
        "features": [
            "Machine Learning",
            "Procesamiento Natural",
            "Generación Automática SQL",
            "Conversación Contextual",
            "Recomendaciones Inteligentes"
        ],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/test', methods=['GET'])
def test_system():
    """Probar sistema completo"""
    try:
        results = {
            "database": "❌",
            "ai_modules": "❌", 
            "ml_models": "❌",
            "overall": "❌"
        }
        
        # Test base de datos
        try:
            global db_connection
            if db_connection is None:
                from database.connection import DatabaseConnection
                db_connection = DatabaseConnection()
            
            if db_connection.test_connection():
                results["database"] = "✅"
                logger.info("✅ Base de datos: OK")
        except Exception as e:
            logger.error(f"❌ Base de datos: {e}")
        
        # Test módulos IA
        try:
            from models.conversation_ai import ConversationAI
            from utils.text_processor import TextProcessor
            from utils.intent_classifier import IntentClassifier
            results["ai_modules"] = "✅"
            logger.info("✅ Módulos IA: OK")
        except Exception as e:
            logger.error(f"❌ Módulos IA: {e}")
        
        # Test ML
        try:
            import sklearn
            import pandas
            import numpy
            results["ml_models"] = "✅"
            logger.info("✅ Librerías ML: OK")
        except Exception as e:
            logger.error(f"❌ Librerías ML: {e}")
        
        # Overall status
        if all(status == "✅" for status in results.values() if status != "❌"):
            results["overall"] = "✅"
            message = "🚀 Sistema completamente funcional"
        else:
            message = "⚠️ Sistema parcialmente funcional"
        
        return jsonify({
            "success": results["overall"] == "✅",
            "message": message,
            "tests": results,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error en test del sistema: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error probando el sistema"
        }), 500

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    """Endpoint principal para conversación con IA completa"""
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"})
    
    try:
        # Obtener instancia de IA
        ai = get_ai_instance()
        
        # Obtener datos del request
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "error": "Mensaje requerido"
            }), 400
        
        user_message = data['message']
        user_role = data.get('role', 'alumno')
        user_id = data.get('user_id', 1)
        
        logger.info(f"Procesando mensaje: {user_message} (Role: {user_role}, ID: {user_id})")
        
        # Procesar mensaje con la IA completa
        response = ai.process_message(
            message=user_message,
            user_role=user_role,
            user_id=user_id
        )
        
        return jsonify({
            "success": True,
            "response": response['text'],
            "data": response.get('data', None),
            "query_used": response.get('query', None),
            "recommendations": response.get('recommendations', []),
            "intent": response.get('intent'),
            "entities": response.get('entities', {}),
            "confidence": response.get('confidence', 0.0),
            "conversational": True,
            "timestamp": response.get('timestamp')
        })
        
    except Exception as e:
        logger.error(f"Error en chat: {e}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            "success": False,
            "error": "Error procesando mensaje",
            "details": str(e),
            "suggestion": "Verifica que todos los módulos estén instalados correctamente"
        }), 500

@app.route('/api/suggestions', methods=['GET'])
def get_suggestions():
    """Obtener sugerencias inteligentes"""
    try:
        ai = get_ai_instance()
        role = request.args.get('role', 'alumno')
        suggestions = ai.get_suggestions(role)
        
        return jsonify({
            "success": True,
            "suggestions": suggestions,
            "role": role
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo sugerencias: {e}")
        return jsonify({
            "success": False,
            "error": "Error obteniendo sugerencias"
        }), 500

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Obtener analytics del sistema"""
    try:
        ai = get_ai_instance()
        analytics = ai.get_system_analytics()
        
        return jsonify({
            "success": True,
            "analytics": analytics
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo analytics: {e}")
        return jsonify({
            "success": False,
            "error": "Error obteniendo analytics"
        }), 500

@app.route('/api/train', methods=['POST'])
def train_model():
    """Endpoint para entrenar/re-entrenar modelos"""
    try:
        # Solo permitir a directivos
        data = request.get_json()
        user_role = data.get('role', '')
        
        if user_role != 'directivo':
            return jsonify({
                "success": False,
                "error": "Solo directivos pueden entrenar modelos"
            }), 403
        
        logger.info("Iniciando entrenamiento de modelos...")
        
        from training.train_model import AIModelTrainer
        
        trainer = AIModelTrainer()
        metrics = trainer.train_all_models()
        trainer.save_models()
        
        return jsonify({
            "success": True,
            "message": "Modelos entrenados exitosamente",
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error entrenando modelos: {e}")
        return jsonify({
            "success": False,
            "error": "Error en entrenamiento",
            "details": str(e)
        }), 500

@app.route('/api/schema', methods=['GET'])
def get_schema_info():
    """Obtener información del esquema de la base de datos"""
    try:
        from database.schema_analyzer import SchemaAnalyzer
        
        global db_connection
        if db_connection is None:
            from database.connection import DatabaseConnection
            db_connection = DatabaseConnection()
        
        analyzer = SchemaAnalyzer(db_connection)
        schema_summary = analyzer.get_schema_summary()
        
        return jsonify({
            "success": True,
            "schema": schema_summary
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo esquema: {e}")
        return jsonify({
            "success": False,
            "error": "Error obteniendo información del esquema"
        }), 500

@app.route('/api/conversation/context/<int:user_id>', methods=['GET'])
def get_conversation_context(user_id):
    """Obtener contexto de conversación de un usuario"""
    try:
        ai = get_ai_instance()
        context = ai.get_conversation_context()
        
        return jsonify({
            "success": True,
            "context": context,
            "user_id": user_id
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo contexto: {e}")
        return jsonify({
            "success": False,
            "error": "Error obteniendo contexto de conversación"
        }), 500

@app.route('/api/conversation/clear/<int:user_id>', methods=['POST'])
def clear_conversation_context(user_id):
    """Limpiar contexto de conversación"""
    try:
        ai = get_ai_instance()
        ai.clear_context()
        
        return jsonify({
            "success": True,
            "message": f"Contexto limpiado para usuario {user_id}"
        })
        
    except Exception as e:
        logger.error(f"Error limpiando contexto: {e}")
        return jsonify({
            "success": False,
            "error": "Error limpiando contexto"
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint no encontrado",
        "available_endpoints": [
            "GET /",
            "GET /api/test", 
            "POST /api/chat",
            "GET /api/suggestions",
            "GET /api/analytics",
            "POST /api/train",
            "GET /api/schema"
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Error 500: {str(error)}")
    return jsonify({
        "error": "Error interno del servidor",
        "message": "Revisa los logs para más detalles"
    }), 500

# Intentar inicializar IA al arrancar
@app.before_first_request
def startup():
    """Inicializar sistema al arrancar"""
    logger.info("🚀 Iniciando IA Conversacional en Railway...")
    try:
        success = initialize_ai()
        if success:
            logger.info("✅ Sistema inicializado correctamente")
        else:
            logger.warning("⚠️ Sistema iniciado parcialmente")
    except Exception as e:
        logger.error(f"❌ Error en inicialización: {e}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"🚂 Iniciando servidor Railway en puerto {port}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )