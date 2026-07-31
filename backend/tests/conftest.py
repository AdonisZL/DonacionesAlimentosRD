"""Configuración compartida para pruebas / 测试共享配置."""

import os
import sys
from pathlib import Path

# Asegurar que el backend está en el path / 确保 backend 在路径中
RAIZ_BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ_BACKEND))

# Establecer variable de entorno para modo prueba / 设置测试模式环境变量
os.environ.setdefault("BD_HOST", "localhost")
os.environ.setdefault("BD_PUERTO", "5432")
os.environ.setdefault("BD_NOMBRE", "donaciones_alimentos")
os.environ.setdefault("BD_USUARIO", "postgres")
os.environ.setdefault("BD_CONTRASENA", "test")
os.environ.setdefault("JWT_SECRETO", "secreto_para_pruebas_unitarias")
os.environ.setdefault("JWT_ALGORITMO", "HS256")
os.environ.setdefault("JWT_MINUTOS_EXPIRACION", "60")
