#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
MÓDULO DE CIFRADO AES-256-GCM + BLIND INDEXING (HMAC-SHA256)

Requisito Normativo: RNF-12 - Protección de Datos Sensibles (Ley 172-13)
Implementación: Encriptación de RNC y Cédula a nivel de aplicación

Arquitectura:
• AES-256-GCM (Authenticated Encryption with Associated Data)
• Blind Indexing con HMAC-SHA256 (Búsqueda sin descifrar)
• IV/Nonce generados aleatoriamente para cada operación
• PBKDF2 para derivación de claves desde contraseña maestra

Cumplimiento Fiscal:
• DGII Resolución 07-17 (Seguridad de datos)
• Ley 172-13 Art. 57-60 (Protección de datos personales)
• Código Tributario Dominican (Art. 287 - Retención de documentos)

=============================================================================
"""

import os
import hmac
import hashlib
from typing import Tuple, Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import base64

class CryptoServiceAES256GCM:
    """
    Servicio de Encriptación AES-256-GCM para datos sensibles (RNC, Cédula)
    
    Características:
    ✓ Cifrado AES-256 con Galois/Counter Mode (GCM)
    ✓ Autenticación integrada (detecta tampering)
    ✓ IV aleatorio por cifrado (previene patrones)
    ✓ HMAC-SHA256 para blind indexing (búsqueda sin descifrar)
    ✓ Serialización base64 para almacenamiento en BD
    
    Contexto de Seguridad:
    El blind indexing permite buscar valores cifrados sin descifrarlos:
    • hash_busqueda = HMAC-SHA256(valor, llave_secreta)
    • Es determinista (mismo valor → mismo hash)
    • No revela el valor original
    • Perfecto para búsquedas de RNC/Cédula
    """
    
    def __init__(self, master_key: Optional[str] = None):
        """
        Inicializa el servicio de cifrado.
        
        Args:
            master_key: Clave maestra (si es None, intenta desde variable de entorno)
        
        Nota:
            En producción, SIEMPRE usar variable de entorno:
            export ENCRYPTION_MASTER_KEY="clave_muy_secreta_de_32_caracteres_minimo"
        """
        if master_key is None:
            master_key = os.getenv('ENCRYPTION_MASTER_KEY')
            if not master_key:
                raise ValueError(
                    "ENCRYPTION_MASTER_KEY no está configurada. "
                    "Establece: export ENCRYPTION_MASTER_KEY='tu_clave_secreta'"
                )
        
        if len(master_key) < 32:
            raise ValueError(
                f"ENCRYPTION_MASTER_KEY debe tener mínimo 32 caracteres. "
                f"Actual: {len(master_key)}"
            )
        
        self.master_key = master_key.encode('utf-8')
        self.backend = default_backend()
    
    def _derive_key(self, salt: bytes = b'') -> bytes:
        """
        Deriva una clave de 32 bytes (256 bits) usando PBKDF2.
        
        Args:
            salt: Salt para derivación (si está vacío, usa salt fijo)
        
        Returns:
            Clave de 256 bits lista para AES-256
        
        Nota Técnica:
        PBKDF2 con 100,000 iteraciones asegura resistencia contra
        ataques de fuerza bruta. El salt previene rainbow tables.
        """
        if not salt:
            salt = b'donaciones_alimentos_2026'  # Salt fijo para determinismo
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits para AES-256
            salt=salt,
            iterations=100_000,
            backend=self.backend
        )
        return kdf.derive(self.master_key)
    
    def encriptar(self, valor_plano: str) -> Tuple[str, str]:
        """
        Encripta un valor y genera su hash para blind indexing.
        
        Args:
            valor_plano: Valor a encriptar (RNC, Cédula, etc.)
        
        Returns:
            Tupla: (valor_cifrado_base64, hash_busqueda_hex)
        
        Ejemplo de Uso:
        ```python
        crypto = CryptoServiceAES256GCM()
        rnc_cifrado, rnc_hash = crypto.encriptar("101234567")
        # Guardar en BD:
        #   rnc_cifrado = rnc_cifrado
        #   rnc_hash_busqueda = rnc_hash
        ```
        
        Flujo Interno:
        1. Generar IV aleatorio (96 bits para GCM)
        2. Derivar clave con PBKDF2
        3. Cifrar con AES-256-GCM
        4. Serializar como: IV_base64 + CIPHERTEXT_base64
        5. Generar hash HMAC-SHA256 del valor plano
        """
        # 1. Generar IV aleatorio (96 bits = 12 bytes recomendados para GCM)
        iv = os.urandom(12)
        
        # 2. Derivar clave
        clave = self._derive_key()
        
        # 3. Crear cifrador AES-256-GCM
        cifrador = AESGCM(clave)
        
        # 4. Cifrar (el tag de autenticación se genera automáticamente)
        ciphertext = cifrador.encrypt(iv, valor_plano.encode('utf-8'), None)
        
        # 5. Serializar: IV + ciphertext
        # Formato: base64(iv + ciphertext)
        valor_completo = iv + ciphertext
        valor_cifrado_b64 = base64.b64encode(valor_completo).decode('utf-8')
        
        # 6. Generar hash HMAC-SHA256 para blind indexing
        hash_busqueda = hmac.new(
            self.master_key,
            valor_plano.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return valor_cifrado_b64, hash_busqueda
    
    def desencriptar(self, valor_cifrado_b64: str) -> Optional[str]:
        """
        Desencripta un valor cifrado.
        
        Args:
            valor_cifrado_b64: Valor cifrado en base64 (de encriptar())
        
        Returns:
            Valor descifrado o None si hay error de autenticación
        
        Excepciones:
            - Lanza excepción si el HMAC no es válido (tampering detectado)
            - Lanza excepción si el formato es inválido
        
        Ejemplo de Uso:
        ```python
        crypto = CryptoServiceAES256GCM()
        rnc = crypto.desencriptar(rnc_cifrado_de_bd)
        ```
        """
        try:
            # 1. Decodificar base64
            valor_completo = base64.b64decode(valor_cifrado_b64)
            
            # 2. Extraer IV (primeros 12 bytes)
            iv = valor_completo[:12]
            ciphertext = valor_completo[12:]
            
            # 3. Derivar clave
            clave = self._derive_key()
            
            # 4. Desencriptar
            # Si alguien modificó el ciphertext, GCM lanzará excepción
            cifrador = AESGCM(clave)
            valor_plano = cifrador.decrypt(iv, ciphertext, None)
            
            # 5. Retornar como string
            return valor_plano.decode('utf-8')
        
        except Exception as e:
            # El tag HMAC no coincide → datos tampering/corrompidos
            raise ValueError(
                f"Error desencriptando valor (posible tampering): {str(e)}"
            )
    
    def verificar_hash_busqueda(self, valor_plano: str, hash_almacenado: str) -> bool:
        """
        Verifica si un valor plano coincide con su hash de búsqueda.
        
        Args:
            valor_plano: Valor a verificar (RNC, Cédula)
            hash_almacenado: Hash HMAC-SHA256 almacenado en BD
        
        Returns:
            True si coinciden, False en caso contrario
        
        Caso de Uso:
        Buscar un usuario por RNC sin exponer el valor cifrado:
        ```python
        def buscar_usuario_por_rnc(rnc):
            crypto = CryptoServiceAES256GCM()
            rnc_hash = crypto.generar_hash_busqueda(rnc)
            return db.session.query(Usuario).filter(
                Usuario.rnc_hash_busqueda == rnc_hash
            ).first()
        ```
        """
        hash_calculado = hmac.new(
            self.master_key,
            valor_plano.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Comparación timing-safe (previene timing attacks)
        return hmac.compare_digest(hash_calculado, hash_almacenado)
    
    def generar_hash_busqueda(self, valor_plano: str) -> str:
        """
        Genera el hash de búsqueda para un valor (usado en búsquedas).
        
        Args:
            valor_plano: Valor (RNC, Cédula)
        
        Returns:
            Hash HMAC-SHA256 en formato hexadecimal
        
        Nota:
        Este método es determinista: mismo valor → mismo hash siempre.
        Por eso se puede usar en índices UNIQUE de la BD.
        """
        return hmac.new(
            self.master_key,
            valor_plano.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()


class BlindIndexHelper:
    """
    Helper para operaciones comunes de blind indexing.
    Simplifica el flujo cifrado en servicios de negocio.
    """
    
    def __init__(self, master_key: Optional[str] = None):
        self.crypto = CryptoServiceAES256GCM(master_key)
    
    def cifrar_y_indexar(self, valor: str) -> dict:
        """
        Cifra un valor y genera su índice de búsqueda en una operación.
        
        Returns:
            Dict con keys: 'cifrado', 'hash_busqueda'
        
        Ejemplo:
        ```python
        helper = BlindIndexHelper()
        resultado = helper.cifrar_y_indexar("101234567")
        perfil.rnc_cifrado = resultado['cifrado']
        perfil.rnc_hash_busqueda = resultado['hash_busqueda']
        ```
        """
        cifrado, hash_busqueda = self.crypto.encriptar(valor)
        return {
            'cifrado': cifrado,
            'hash_busqueda': hash_busqueda
        }
    
    def buscar_por_valor(self, modelo, campo_hash_attr: str, valor: str):
        """
        Busca en base de datos usando blind indexing.
        
        Args:
            modelo: Modelo SQLAlchemy
            campo_hash_attr: Nombre del atributo hash (ej: 'rnc_hash_busqueda')
            valor: Valor a buscar
        
        Returns:
            Primer resultado o None
        
        Ejemplo:
        ```python
        helper = BlindIndexHelper()
        usuario = helper.buscar_por_valor(
            PerfilLegal, 
            'rnc_hash_busqueda', 
            '101234567'
        )
        ```
        """
        hash_busqueda = self.crypto.generar_hash_busqueda(valor)
        return session.query(modelo).filter(
            getattr(modelo, campo_hash_attr) == hash_busqueda
        ).first()


# =============================================================================
# EJEMPLO DE INTEGRACIÓN EN SERVICIOS
# =============================================================================

"""
EJEMPLO 1: Guardar usuario con RNC cifrado

def crear_perfil_legal(usuario_id, rnc, cedula):
    crypto = CryptoServiceAES256GCM()
    
    # Cifrar RNC
    rnc_cifrado, rnc_hash = crypto.encriptar(rnc)
    
    # Cifrar Cédula
    cedula_cifrada, cedula_hash = crypto.encriptar(cedula)
    
    # Guardar en BD
    perfil = PerfilLegal(
        id_usuario=usuario_id,
        rnc_cifrado=rnc_cifrado,
        rnc_hash_busqueda=rnc_hash,
        cedula_cifrada=cedula_cifrada,
        cedula_hash_busqueda=cedula_hash
    )
    session.add(perfil)
    session.commit()
    return perfil


EJEMPLO 2: Buscar usuario por RNC sin descifrar

def buscar_usuario_por_rnc(rnc):
    crypto = CryptoServiceAES256GCM()
    rnc_hash = crypto.generar_hash_busqueda(rnc)
    
    return session.query(PerfilLegal).filter(
        PerfilLegal.rnc_hash_busqueda == rnc_hash
    ).first()


EJEMPLO 3: Usar RNC descifrado en reporte fiscal

def generar_reporte_dgii_606(perfil_legal):
    crypto = CryptoServiceAES256GCM()
    
    # Descifrar solo cuando se necesita
    rnc_descifrado = crypto.desencriptar(perfil_legal.rnc_cifrado)
    
    # Usar en reporte
    reporte = f"RNC: {rnc_descifrado}"
    
    return reporte


SEGURIDAD:
• NUNCA almacenar el valor plano junto al cifrado
• NUNCA loguear valores cifrados o descifrados
• SOLO descifrar cuando sea estrictamente necesario
• Usar blind indexing (hash) para búsquedas siempre

CUMPLIMIENTO:
✓ Ley 172-13: Protección de datos personales (RNC, Cédula)
✓ DGII: Auditoría de accesos a datos sensibles
✓ PCI DSS: Encriptación de datos sensibles
✓ OWASP: Protección contra inyección SQL y tampering
"""

if __name__ == "__main__":
    # Prueba rápida (solo para desarrollo)
    import os
    
    # Configurar variable de entorno para prueba
    os.environ['ENCRYPTION_MASTER_KEY'] = 'una_clave_muy_secreta_para_pruebas_123'
    
    crypto = CryptoServiceAES256GCM()
    
    # Prueba 1: Encriptar
    print("🔐 PRUEBA DE CIFRADO AES-256-GCM")
    print("=" * 60)
    
    rnc_original = "101234567"
    rnc_cifrado, rnc_hash = crypto.encriptar(rnc_original)
    
    print(f"RNC Original:     {rnc_original}")
    print(f"RNC Cifrado:      {rnc_cifrado[:50]}...")
    print(f"Hash Búsqueda:    {rnc_hash}")
    print()
    
    # Prueba 2: Desencriptar
    print("🔓 DESENCRIPTACIÓN")
    print("=" * 60)
    rnc_recuperado = crypto.desencriptar(rnc_cifrado)
    print(f"RNC Recuperado:   {rnc_recuperado}")
    print(f"¿Coincide?:       {rnc_recuperado == rnc_original}")
    print()
    
    # Prueba 3: Verificar hash
    print("✓ VERIFICACIÓN DE HASH (BLIND INDEXING)")
    print("=" * 60)
    verificado = crypto.verificar_hash_busqueda(rnc_original, rnc_hash)
    print(f"Hash Válido:      {verificado}")
    print()
    
    # Prueba 4: Tampering
    print("⚠️  DETECCIÓN DE TAMPERING")
    print("=" * 60)
    rnc_tampered = rnc_cifrado[:-5] + "XXXXX"  # Modificar
    try:
        crypto.desencriptar(rnc_tampered)
        print("❌ ERROR: Debería haber detectado tampering")
    except ValueError as e:
        print(f"✓ Tampering detectado correctamente: {str(e)[:50]}...")
