from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

db = None
ai = None

def initialize_components():
    global db, ai
    try:
        from database.connection import DatabaseConnection
        from models.simple_enhanced_conversation_ai import SimpleEnhancedConversationAI
        
        db = DatabaseConnection()
        ai = SimpleEnhancedConversationAI()
        logger.info("Simple enhanced components initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing simple enhanced components: {e}")
        return False

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
    if not db:
        if not initialize_components():
            return jsonify({
                "success": False,
                "message": "Error inicializando componentes",
                "database": "Error de inicializacion"
            }), 500
    
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
    if not ai:
        if not initialize_components():
            return jsonify({
                "success": False,
                "error": "Error inicializando IA",
                "response": "Sistema no disponible temporalmente",
            }), 500
    
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
            "Cual es mi promedio general?",
            "Que asignaturas he cursado y que calificaciones tengo?",
            "Que reportes de riesgo he recibido?",
            "Que materias estoy cursando actualmente?",
            "Que solicitudes de ayuda he hecho?",
            "En que grupo estoy asignado?",
            "Cuales son mis datos de contacto?"
        ],
        'profesor': [
            "Buenos dias!",
            "Que asignaturas imparto este cuatrimestre?",
            "Que grupos tengo asignados?",
            "Cuales son mis horarios de clase?",
            "Que reportes de riesgo he emitido?",
            "Que calificaciones he capturado?",
            "Soy tutor academico de algun alumno?",
            "Que encuestas he creado?"
        ],
        'directivo': [
            "Hola, como va todo?",
            "Que alumnos tienen reportes abiertos?",
            "Cuales son las solicitudes pendientes?",
            "Que noticias estan activas?",
            "Cuantos alumnos hay por carrera?",
            "Que carreras estan activas?",
            "Cuales son los posts mas vistos del foro?",
            "Que tipos de problemas reportan mas los alumnos?"
        ]
    }
    
    return jsonify({
        "success": True,
        "suggestions": suggestions_map.get(role, suggestions_map['alumno']),
        "role": role,
        "message": f"Sugerencias de consultas especificas para {role}",
        "note": "Puedes hacer preguntas especificas mencionando nombres de personas, materias, grupos, etc."
    })

@app.route('/api/capabilities', methods=['GET'])
def capabilities():
    return jsonify({
        "success": True,
        "message": "Capacidades del sistema de IA",
        "categories": {
            "alumnos": [
                "Promedio general de un alumno especifico",
                "Alumnos en un cuatrimestre determinado",
                "Cantidad de alumnos por carrera",
                "Alumnos con bajas temporales o definitivas",
                "Grupo y aula asignados a un alumno",
                "Datos de contacto y tutor de un alumno",
                "Evolucion del promedio de un alumno",
                "Asignaturas cursadas y calificaciones",
                "Reportes de riesgo recibidos",
                "Solicitudes de ayuda realizadas",
                "Encuestas contestadas",
                "Participacion en el foro",
                "Interacciones en posts y comentarios"
            ],
            "profesores": [
                "Asignaturas que imparte un profesor",
                "Grupos asignados por cuatrimestre",
                "Horarios de un profesor",
                "Alumnos de grupos especificos",
                "Reportes de riesgo emitidos",
                "Calificaciones capturadas",
                "Experiencia y especialidad",
                "Funciones como tutor academico",
                "Encuestas creadas"
            ],
            "directivos": [
                "Noticias publicadas",
                "Categorias de foro y encuestas creadas",
                "Solicitudes de ayuda asignadas",
                "Conversaciones de chatbot iniciadas"
            ],
            "sistema": [
                "Estadisticas generales",
                "Reportes de riesgo por tipo y nivel",
                "Solicitudes pendientes",
                "Noticias activas",
                "Posts mas populares del foro",
                "Categorias con mas contenido",
                "Tipos de problemas mas reportados",
                "Encuestas y sus respuestas"
            ]
        },
        "usage_examples": [
            "Cual es el promedio del alumno Juan Perez?",
            "Que grupos tiene asignados el profesor Maria Lopez?",
            "Que alumnos estan en riesgo critico?",
            "Cuales son las noticias activas?",
            "Que encuestas ha creado el profesor Rodriguez?",
            "Cuantos alumnos hay en Ingenieria en Sistemas?",
            "Que solicitudes de ayuda estan pendientes?"
        ],
        "note": "Especifica nombres completos, IDs o titulos segun sea necesario para obtener resultados precisos."
    })

@app.route('/api/context/<int:user_id>', methods=['GET'])
def get_context(user_id):
    if not ai:
        if not initialize_components():
            return jsonify({
                "success": False,
                "error": "Sistema no inicializado"
            }), 500
    
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
    if not ai:
        if not initialize_components():
            return jsonify({
                "success": False,
                "error": "Sistema no inicializado"
            }), 500
    
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
    
    if initialize_components():
        logger.info("Aplicacion lista para recibir requests")
    else:
        logger.warning("Aplicacion iniciada con problemas de inicializacion")
    
    app.run(host='0.0.0.0', port=port, debug=False)