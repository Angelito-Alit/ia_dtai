
from .conversation_ai import ConversationAI
from .query_generator import QueryGenerator
from .response_formatter import ResponseFormatter

__all__ = [
    'ConversationAI',
    'QueryGenerator', 
    'ResponseFormatter'
]

__version__ = '1.0.0'
__author__ = 'Sistema IA Educativo'

from .connection import DatabaseConnection
from .schema_analyzer import SchemaAnalyzer
from .query_executor import QueryExecutor

__all__ = [
    'DatabaseConnection',
    'SchemaAnalyzer',
    'QueryExecutor'
]

__version__ = '1.0.0'
DEFAULT_CONFIG = {
    'host': 'bluebyte.space',
    'port': 3306,
    'database': 'bluebyte_dtai_web',
    'charset': 'utf8mb4',
    'autocommit': True
}

from .text_processor import TextProcessor
from .intent_classifier import IntentClassifier

__all__ = [
    'TextProcessor',
    'IntentClassifier'
]

__version__ = '1.0.0'
TEXT_CONFIG = {
    'remove_accents': True,
    'lowercase': True,
    'remove_punctuation': False,  
    'min_word_length': 2,
    'max_word_length': 50
}

CLASSIFICATION_CONFIG = {
    'confidence_threshold': 0.6,
    'max_suggestions': 5,
    'fallback_intent': 'consulta_general'
}

from .training_data import (
    TRAINING_DATA,
    get_all_training_data,
    get_training_data_by_intent,
    validate_training_data,
    DOMAIN_ENTITIES
)
from .train_model import AIModelTrainer

__all__ = [
    'TRAINING_DATA',
    'get_all_training_data',
    'get_training_data_by_intent', 
    'validate_training_data',
    'DOMAIN_ENTITIES',
    'AIModelTrainer'
]

__version__ = '1.0.0'
TRAINING_CONFIG = {
    'test_size': 0.2,
    'validation_size': 0.1,
    'random_state': 42,
    'cv_folds': 5,
    'min_samples_per_intent': 3,
    'max_features': 5000,
    'ngram_range': (1, 2)
}
IMPORTANT_METRICS = [
    'accuracy',
    'precision',
    'recall',
    'f1_score',
    'confusion_matrix',
    'classification_report'
]

import logging
import os
from datetime import datetime
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('ai_system.log') if os.path.exists('.') else logging.NullHandler()
    ]
)

logger = logging.getLogger(__name__)
__version__ = '1.0.0'
__author__ = 'Sistema IA Educativo'
__email__ = 'soporte@sistemaai.edu'
__status__ = 'Production'
SYSTEM_CONFIG = {
    'version': __version__,
    'name': 'IA Conversacional Educativa',
    'description': 'Sistema de IA para consultas académicas en lenguaje natural',
    'supported_languages': ['es'],
    'supported_roles': ['alumno', 'profesor', 'directivo'],
    'database_engine': 'MySQL',
    'ml_frameworks': ['scikit-learn', 'pandas', 'numpy'],
    'deployment_platforms': ['Vercel', 'Railway', 'Heroku'],
    'max_query_length': 500,
    'max_response_length': 2000,
    'cache_ttl_minutes': 5,
    'rate_limit_per_minute': 60
}
USER_ROLES = {
    'alumno': {
        'description': 'Estudiante del sistema educativo',
        'permissions': [
            'ver_calificaciones_propias',
            'consultar_horario_propio',
            'solicitar_ayuda',
            'ver_noticias_publicas'
        ],
        'restricted_data': ['datos_otros_alumnos', 'informacion_personal_terceros']
    },
    'profesor': {
        'description': 'Personal docente',
        'permissions': [
            'ver_grupos_asignados',
            'consultar_alumnos_grupos',
            'crear_reportes_riesgo',
            'ver_estadisticas_grupos',
            'gestionar_calificaciones_grupos'
        ],
        'restricted_data': ['datos_financieros', 'informacion_directivos']
    },
    'directivo': {
        'description': 'Personal administrativo y directivo',
        'permissions': [
            'ver_estadisticas_generales',
            'consultar_todos_reportes',
            'gestionar_solicitudes_ayuda',
            'ver_analytics_sistema',
            'acceder_datos_agregados'
        ],
        'restricted_data': ['datos_personales_detallados']
    }
}
SUPPORTED_QUERIES = {
    'academicas': [
        'calificaciones',
        'promedios',
        'asignaturas',
        'horarios',
        'grupos'
    ],
    'administrativas': [
        'reportes_riesgo',
        'solicitudes_ayuda',
        'estadisticas',
        'usuarios'
    ],
    'comunicacion': [
        'noticias',
        'foros',
        'encuestas'
    ]
}
SYSTEM_LIMITS = {
    'max_concurrent_users': 100,
    'max_query_complexity': 'MEDIA',
    'max_result_rows': 1000,
    'cache_max_size_mb': 50,
    'session_timeout_minutes': 30
}

def get_system_info():
    return {
        'system': SYSTEM_CONFIG,
        'roles': USER_ROLES,
        'queries': SUPPORTED_QUERIES,
        'limits': SYSTEM_LIMITS,
        'startup_time': datetime.now().isoformat(),
        'status': 'active'
    }

def validate_system_requirements():
    required_modules = [
        'flask', 'mysql.connector', 'pandas', 'sklearn',
        'numpy', 'nltk', 'flask_cors'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        logger.error(f"Módulos faltantes: {missing_modules}")
        return False
    
    logger.info("Todos los requisitos del sistema están satisfechos")
    return True
logger.info(f"Sistema {SYSTEM_CONFIG['name']} v{__version__} iniciado")
logger.info(f"Soporte para roles: {list(USER_ROLES.keys())}")
logger.info(f"Tipos de consulta: {list(SUPPORTED_QUERIES.keys())}")
if not validate_system_requirements():
    logger.warning("Sistema iniciado con dependencias faltantes")
__all__ = [
    'SYSTEM_CONFIG',
    'USER_ROLES', 
    'SUPPORTED_QUERIES',
    'SYSTEM_LIMITS',
    'get_system_info',
    'validate_system_requirements'
]