"""
个性化题库系统配置文件
"""
import os
from datetime import timedelta

class Config:
    """基础配置类"""
    
    # Flask应用配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///question_bank.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Judge0 API配置
    JUDGE0_API_URL = os.getenv('JUDGE0_API_URL', 'https://judge0-ce.p.rapidapi.com')
    RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY', '')
    
    # 推荐算法参数
    RECOMMENDATION_CONFIG = {
        'difficulty_weight': float(os.getenv('DIFFICULTY_WEIGHT', 0.3)),
        'type_weight': float(os.getenv('TYPE_WEIGHT', 0.25)),
        'knowledge_weight': float(os.getenv('KNOWLEDGE_WEIGHT', 0.35)),
        'time_weight': float(os.getenv('TIME_WEIGHT', 0.1)),
        'cache_ttl': int(os.getenv('RECOMMENDATION_CACHE_TTL', 3600)),
        'max_recommendations': int(os.getenv('MAX_RECOMMENDATIONS_PER_REQUEST', 20))
    }
    
    # 分页配置
    QUESTIONS_PER_PAGE = 20
    RECORDS_PER_PAGE = 50
    
    # 缓存配置
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
    
    # Session配置
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # CORS配置
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    TESTING = False
    
    # 开发环境使用SQLite
    if not os.getenv('DATABASE_URL'):
        SQLALCHEMY_DATABASE_URI = 'sqlite:///dev_question_bank.db'

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    DEBUG = True
    
    # 测试环境使用内存数据库
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # 禁用CSRF保护以便测试
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    TESTING = False
    
    # 生产环境必须使用环境变量中的数据库URL
    if not os.getenv('DATABASE_URL'):
        raise ValueError("生产环境必须设置DATABASE_URL环境变量")
    
    # 生产环境安全配置
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # 日志配置
    LOG_LEVEL = 'WARNING'

# 配置映射
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    """获取当前配置"""
    config_name = os.getenv('FLASK_ENV', 'development')
    return config.get(config_name, config['default'])
