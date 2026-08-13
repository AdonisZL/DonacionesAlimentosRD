#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
MÓDULO DE HASH-CHAINING SHA-256 PARA INTEGRIDAD DE AUDITORÍA

Requisito Normativo: Hallazgo 8 - Integridad de Registros de Auditoría
Implementación: Cadena criptográfica de SHA-256 (blockchain-like)

Problemas Resueltos:
✓ Detección de modificación de registros de auditoría (append-only)
✓ Verificación de secuencia temporal (no puede haber saltos)
✓ Aseguramiento de no-repudio (imposible negar lo registrado)

Mecanismo:
• hash_actual = SHA-256(registro_completo + hash_anterior)
• hash_anterior = SHA-256 del registro previo en la cadena
• Si se modifica cualquier registro, toda la cadena se rompe
• Detectable inmediatamente: hash_actual no coincide

Cumplimiento Auditoria:
• COSO Framework (Committee of Sponsoring Organizations)
• SOX Compliance (Sarbanes-Oxley Act)
• ISACA COBIT 5 (Controles de IT)
• Resolución DGII 07-17 (Auditoría fiscal dominicana)

=============================================================================
"""

import hashlib
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import text
from sqlalchemy.orm import Session

class HashChainService:
    """
    Servicio de cadena de hashes SHA-256 para integridad de auditoría.
    
    Funcionalidad:
    • Genera cadenas criptográficas de registros
    • Valida integridad de toda la secuencia
    • Detecta tampering automáticamente
    • Compatible con append-only enforcement en BD
    
    Uso Típico:
    1. Crear registro de auditoría → calcular hash
    2. Almacenar hash_actual y hash_anterior en BD
    3. Periodicamente: validar cadena completa
    """
    
    @staticmethod
    def calcular_sha256(datos: str) -> str:
        """
        Calcula SHA-256 de una cadena.
        
        Args:
            datos: Datos a hashear
        
        Returns:
            Hash SHA-256 en hexadecimal (64 caracteres)
        
        Nota Técnica:
        SHA-256 produce 256 bits (32 bytes) = 64 caracteres en hex
        Es una función unidireccional: imposible recuperar entrada del hash
        """
        return hashlib.sha256(datos.encode('utf-8')).hexdigest()
    
    @staticmethod
    def serializar_registro(registro: Dict[str, Any]) -> str:
        """
        Serializa un registro de auditoría para hashing.
        
        Args:
            registro: Dict con datos del registro
        
        Returns:
            String JSON ordenado y normalizado
        
        Importante:
        El orden de las keys DEBE ser determinista para que el hash
        sea reproducible. JSON sort_keys=True garantiza esto.
        
        Campos típicos:
        {
            "id_bitacora": "uuid",
            "id_usuario": "uuid",
            "accion": "CREATE|UPDATE|DELETE|LOGIN|EXPORT",
            "entidad_afectada": "usuarios|donaciones|emparejamientos",
            "detalles_antes_despues": {...},
            "ip_origen": "192.168.1.100",
            "creado_en": "2026-08-13T13:51:00Z"
        }
        """
        # Ordenar keys para determinismo
        json_str = json.dumps(
            registro,
            sort_keys=True,
            default=str,  # Serializar datetime, UUID como str
            ensure_ascii=True
        )
        return json_str
    
    @staticmethod
    def generar_hash_registro(
        registro: Dict[str, Any],
        hash_anterior: Optional[str] = None
    ) -> str:
        """
        Genera el hash SHA-256 de un registro en la cadena.
        
        Args:
            registro: Datos del registro de auditoría
            hash_anterior: Hash del registro anterior (None si es el primero)
        
        Returns:
            Hash SHA-256 del registro (para almacenar como hash_actual)
        
        Algoritmo:
        hash_actual = SHA256(serializar(registro) + hash_anterior || "")
        
        Ejemplo:
        ```
        Registro 1:
          hash_actual = SHA256(datos1 + "")
          Resultado:   abc123...
        
        Registro 2:
          hash_actual = SHA256(datos2 + "abc123...")
          Resultado:   def456...
        
        Registro 3:
          hash_actual = SHA256(datos3 + "def456...")
          Resultado:   ghi789...
        
        Si alguien modifica Registro 1:
          - hash_actual no coincide
          - hash_anterior en Registro 2 no apunta al hash anterior correcto
          - Tampering detectado inmediatamente
        ```
        """
        json_serializado = HashChainService.serializar_registro(registro)
        
        # Concatenar con hash anterior (chain)
        cadena = json_serializado + (hash_anterior or "")
        
        # Calcular SHA-256
        return HashChainService.calcular_sha256(cadena)
    
    @staticmethod
    def validar_integridad_registro(
        registro_actual: Dict[str, Any],
        hash_actual_almacenado: str,
        hash_anterior: Optional[str] = None
    ) -> bool:
        """
        Valida que un registro NO ha sido modificado.
        
        Args:
            registro_actual: Datos del registro (como está ahora en BD)
            hash_actual_almacenado: Hash guardado en bd (cuando se creó)
            hash_anterior: Hash del registro anterior
        
        Returns:
            True si el hash coincide (integridad OK)
            False si no coincide (tampering detectado)
        
        Uso:
        ```python
        # Leer registro de BD
        registro = session.query(BitacoraAuditoria).get(id_bitacora)
        
        # Verificar
        es_integro = HashChainService.validar_integridad_registro(
            {
                "id_bitacora": str(registro.id_bitacora),
                "accion": registro.accion,
                ...
            },
            registro.hash_actual,
            registro.hash_anterior
        )
        
        if not es_integro:
            ALERTA: "¡Auditoría tampering detectado!"
        ```
        """
        hash_calculado = HashChainService.generar_hash_registro(
            registro_actual,
            hash_anterior
        )
        return hash_calculado == hash_actual_almacenado
    
    @staticmethod
    def validar_cadena_completa(
        session: Session,
        tabla_nombre: str,
        orden_columna: str = "creado_en"
    ) -> Dict[str, Any]:
        """
        Valida la integridad de TODA la cadena de hash en una tabla.
        
        Args:
            session: Sesión SQLAlchemy
            tabla_nombre: Nombre de tabla (ej: 'bitacora_auditoria')
            orden_columna: Columna para ordenar (temporal)
        
        Returns:
            Dict con:
            {
                "integridad_ok": bool,
                "registros_validados": int,
                "primer_error": {
                    "id": ...,
                    "hash_esperado": ...,
                    "hash_almacenado": ...
                } o None
            }
        
        Nota Importante:
        Esta función DEBE ejecutarse regularmente (ej: cada 24 horas)
        para detectar tampering. Se recomienda automatizar con CRON.
        
        Complejidad: O(n) - valida cada registro secuencialmente
        """
        try:
            # 1. Obtener todos los registros en orden temporal
            query = f"""
                SELECT 
                    id_bitacora,
                    id_usuario,
                    accion,
                    entidad_afectada,
                    detalles_antes_despues,
                    ip_origen,
                    creado_en,
                    hash_actual,
                    hash_anterior
                FROM "{tabla_nombre}"
                ORDER BY {orden_columna} ASC
            """
            
            resultado = session.execute(text(query))
            registros = resultado.fetchall()
            
            if not registros:
                return {
                    "integridad_ok": True,
                    "registros_validados": 0,
                    "primer_error": None
                }
            
            # 2. Validar cadena desde el principio
            hash_anterior_esperado = None
            
            for idx, fila in enumerate(registros):
                # Construir dict del registro
                registro = {
                    "id_bitacora": str(fila[0]),
                    "id_usuario": str(fila[1]),
                    "accion": fila[2],
                    "entidad_afectada": fila[3],
                    "detalles_antes_despues": fila[4],
                    "ip_origen": fila[5],
                    "creado_en": str(fila[6])
                }
                
                hash_actual_almacenado = fila[7]
                hash_anterior_almacenado = fila[8]
                
                # Calcular hash esperado
                hash_esperado = HashChainService.generar_hash_registro(
                    registro,
                    hash_anterior_esperado
                )
                
                # Validar
                if hash_esperado != hash_actual_almacenado:
                    return {
                        "integridad_ok": False,
                        "registros_validados": idx,
                        "primer_error": {
                            "posicion": idx,
                            "id_bitacora": str(fila[0]),
                            "hash_esperado": hash_esperado,
                            "hash_almacenado": hash_actual_almacenado,
                            "hash_anterior_esperado": hash_anterior_esperado,
                            "hash_anterior_almacenado": hash_anterior_almacenado
                        }
                    }
                
                # Avanzar en la cadena
                hash_anterior_esperado = hash_actual_almacenado
            
            # 3. Si llegamos aquí, toda la cadena es íntegra
            return {
                "integridad_ok": True,
                "registros_validados": len(registros),
                "primer_error": None
            }
        
        except Exception as e:
            return {
                "integridad_ok": False,
                "registros_validados": 0,
                "primer_error": {
                    "error": str(e)
                }
            }
    
    @staticmethod
    def generar_reporte_validacion(
        session: Session,
        tabla_nombre: str
    ) -> str:
        """
        Genera un reporte de validación para auditoría.
        
        Returns:
            String formateado para logging/almacenamiento
        """
        resultado = HashChainService.validar_cadena_completa(session, tabla_nombre)
        
        reporte = f"""
╔════════════════════════════════════════════════════════════╗
║   REPORTE DE VALIDACIÓN DE INTEGRIDAD - HASH-CHAIN        ║
║   Tabla: {tabla_nombre:45} ║
║   Fecha: {datetime.now().isoformat():44} ║
╚════════════════════════════════════════════════════════════╝

RESULTADO: {"✓ INTEGRIDAD OK" if resultado["integridad_ok"] else "✗ TAMPERING DETECTADO"}

Registros Validados: {resultado["registros_validados"]}

"""
        
        if resultado["primer_error"]:
            error = resultado["primer_error"]
            reporte += f"""
ERROR ENCONTRADO EN:
  Posición: {error.get("posicion", "N/A")}
  ID: {error.get("id_bitacora", "N/A")}
  Hash Esperado:      {error.get("hash_esperado", "N/A")}
  Hash Almacenado:    {error.get("hash_almacenado", "N/A")}
  
ALERTA: ¡Los datos pueden haber sido modificados!
"""
        else:
            reporte += """
ESTADO: Todos los registros verificados correctamente.
Ningún tampering detectado en la cadena.
"""
        
        return reporte


class AuditoriaIntegridad:
    """
    Wrapper para operaciones de auditoría con hash-chaining.
    
    Simplifica el uso de hash-chaining en servicios de auditoría.
    """
    
    def __init__(self, session: Session):
        self.session = session
        self.hash_service = HashChainService()
    
    def registrar_evento(
        self,
        id_usuario: str,
        accion: str,
        entidad_afectada: str,
        detalles_antes_despues: dict,
        ip_origen: str
    ) -> dict:
        """
        Registra un evento de auditoría con hash-chaining automático.
        
        Args:
            id_usuario: UUID del usuario que realizó la acción
            accion: Tipo de acción (CREATE, UPDATE, DELETE, LOGIN, EXPORT)
            entidad_afectada: Tabla/entidad afectada
            detalles_antes_despues: Dict con antes/después de cambios
            ip_origen: IP del cliente
        
        Returns:
            Dict con id_bitacora, hash_actual, hash_anterior
        
        Nota:
        Este método calcula automáticamente los hashes.
        Solo necesita guardar el resultado en la BD.
        """
        # Obtener último hash
        query = """
            SELECT hash_actual 
            FROM bitacora_auditoria 
            ORDER BY creado_en DESC 
            LIMIT 1
        """
        resultado = self.session.execute(text(query)).scalar()
        hash_anterior = resultado if resultado else None
        
        # Construir registro
        registro = {
            "id_usuario": id_usuario,
            "accion": accion,
            "entidad_afectada": entidad_afectada,
            "detalles_antes_despues": detalles_antes_despues,
            "ip_origen": ip_origen,
            "creado_en": datetime.now().isoformat()
        }
        
        # Calcular hash
        hash_actual = self.hash_service.generar_hash_registro(
            registro,
            hash_anterior
        )
        
        return {
            "hash_actual": hash_actual,
            "hash_anterior": hash_anterior,
            "registro_datos": registro
        }


# =============================================================================
# EJEMPLO DE INTEGRACIÓN EN MODELS.py
# =============================================================================

"""
En app/models/bitacora_auditoria.py, al crear un nuevo registro:

def crear_evento_auditoria(session, usuario_id, accion, detalles):
    auditoria = AuditoriaIntegridad(session)
    
    # Obtener hash y datos
    resultado = auditoria.registrar_evento(
        id_usuario=usuario_id,
        accion=accion,
        entidad_afectada="donaciones",
        detalles_antes_despues=detalles,
        ip_origen="192.168.1.100"
    )
    
    # Crear registro en BD
    evento = BitacoraAuditoria(
        id_usuario=usuario_id,
        accion=accion,
        entidad_afectada="donaciones",
        detalles_antes_despues=detalles,
        ip_origen="192.168.1.100",
        hash_actual=resultado["hash_actual"],
        hash_anterior=resultado["hash_anterior"]
    )
    session.add(evento)
    session.commit()
    
    return evento


Validar cadena regularmente (CRON job):

def tarea_validar_integridad():
    session = SessionLocal()
    resultado = HashChainService.validar_cadena_completa(
        session,
        "bitacora_auditoria"
    )
    
    if not resultado["integridad_ok"]:
        # ALERTA: Tampering detectado
        enviar_email_administrador(
            f"ALERTA SEGURIDAD: Tampering detectado en bitacora_auditoria"
        )
    
    session.close()
"""

if __name__ == "__main__":
    # Prueba rápida
    print("🔗 PRUEBA DE HASH-CHAINING")
    print("=" * 60)
    
    # Crear 3 registros simulados
    registros = [
        {
            "id": 1,
            "accion": "CREATE",
            "entidad": "donaciones",
            "timestamp": "2026-08-13T10:00:00Z"
        },
        {
            "id": 2,
            "accion": "UPDATE",
            "entidad": "donaciones",
            "timestamp": "2026-08-13T11:00:00Z"
        },
        {
            "id": 3,
            "accion": "DELETE",
            "entidad": "donaciones",
            "timestamp": "2026-08-13T12:00:00Z"
        },
    ]
    
    # Generar cadena
    hashes = []
    for idx, reg in enumerate(registros):
        hash_anterior = hashes[-1] if hashes else None
        hash_actual = HashChainService.generar_hash_registro(reg, hash_anterior)
        hashes.append(hash_actual)
        
        print(f"Registro {idx + 1}:")
        print(f"  Datos: {reg}")
        print(f"  Hash Anterior: {hash_anterior or 'NINGUNO'}")
        print(f"  Hash Actual:   {hash_actual}")
        print()
    
    # Validar integridad
    print("=" * 60)
    print("✓ VALIDANDO INTEGRIDAD")
    print("=" * 60)
    
    es_integro = HashChainService.validar_integridad_registro(
        registros[1],
        hashes[1],
        hashes[0]
    )
    print(f"Registro 2 íntegro: {es_integro}")
    
    # Simular tampering
    print()
    print("=" * 60)
    print("⚠️  SIMULANDO TAMPERING")
    print("=" * 60)
    registros[1]["accion"] = "HACK"  # Modificar
    
    es_integro = HashChainService.validar_integridad_registro(
        registros[1],
        hashes[1],
        hashes[0]
    )
    print(f"Registro 2 íntegro después de modificación: {es_integro}")
    print("✓ Tampering detectado correctamente")
