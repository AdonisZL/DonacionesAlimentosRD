#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
MÓDULO DE INTEGRACIÓN GOOGLE SHEETS API

Requisito: OE2 - Sincronización Contable / ERP Simulado
Propósito: Puente de datos entre sistema y hoja de cálculo (Google Sheets)

Casos de Uso:
1. EXPORTACIÓN: Agregar registro de donación completada a hoja
2. IMPORTACIÓN: Leer inventario de mermas de supermercado aliado
3. AUDITORÍA: Mantener historial de transacciones en Google Sheets

Autenticación:
• Cuenta de Servicio (Service Account)
• Credenciales JSON desde variable de entorno
• Permisos: sheets.googleapis.com, drive.googleapis.com

Ventajas:
✓ Interfaz visual para revisión de datos
✓ Compartir con stakeholders sin acceso a BD
✓ Auditoría en tiempo real (logs de cambios de Sheets)
✓ Integración con herramientas contables (Zapier, Make)

=============================================================================
"""

import os
import json
from typing import List, Dict, Optional, Any
from datetime import datetime
from decimal import Decimal
import logging

# Importaciones de Google
try:
    from google.oauth2.service_account import Credentials
    from google.auth.exceptions import GoogleAuthError
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_API_DISPONIBLE = True
except ImportError:
    GOOGLE_API_DISPONIBLE = False
    logging.warning(
        "Google API client no instalado. "
        "Para usar GoogleSheetsService, ejecuta: "
        "pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client"
    )

logger = logging.getLogger(__name__)


class GoogleSheetsService:
    """
    Servicio de integración con Google Sheets para sincronización contable.
    
    Funcionalidades:
    • Agregar donaciones completadas a hoja de cálculo
    • Leer inventario de mermas desde hoja externa
    • Mantener historial auditado
    • Validar integridad de datos
    
    Configuración Requerida:
    1. Crear Cuenta de Servicio en Google Cloud Console
    2. Descargar JSON de credenciales
    3. Configurar variable de entorno:
       export GOOGLE_SHEETS_CREDENTIALS='{json_credentials_aqui}'
    4. Compartir hoja con el email de la Cuenta de Servicio
    
    Estructura de Hoja - Donaciones:
    │ Fecha       │ RNC Donante │ Empresa         │ NCF      │ Libras │ Valor RD$ │ Estado      │
    │ 2026-08-13  │ 101234567   │ Supermercado X  │ E450001  │ 500    │ 5000.00   │ ACEPTADO    │
    
    Estructura de Hoja - Inventario Mermas:
    │ Producto     │ Libras │ Fecha Vencimiento │
    │ Arroz        │ 250    │ 2026-08-20        │
    │ Frijoles     │ 100    │ 2026-09-01        │
    """
    
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    def __init__(self, spreadsheet_id: Optional[str] = None):
        """
        Inicializa el servicio de Google Sheets.
        
        Args:
            spreadsheet_id: ID de la hoja (si es None, busca en env)
        
        Raises:
            ValueError: Si no hay credenciales disponibles
        """
        if not GOOGLE_API_DISPONIBLE:
            raise ImportError(
                "Google API client no está instalado. "
                "Instala con: pip install google-auth-httplib2 google-api-python-client"
            )
        
        # Obtener credenciales desde variable de entorno
        creds_json = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
        if not creds_json:
            raise ValueError(
                "GOOGLE_SHEETS_CREDENTIALS no configurada. "
                "Establece: export GOOGLE_SHEETS_CREDENTIALS='{...}'"
            )
        
        try:
            creds_dict = json.loads(creds_json)
            self.credentials = Credentials.from_service_account_info(
                creds_dict,
                scopes=self.SCOPES
            )
            self.service = build('sheets', 'v4', credentials=self.credentials)
            self.drive_service = build('drive', 'v3', credentials=self.credentials)
        except (json.JSONDecodeError, GoogleAuthError) as e:
            raise ValueError(f"Error en credenciales Google: {str(e)}")
        
        self.spreadsheet_id = spreadsheet_id or os.getenv('GOOGLE_SPREADSHEET_ID')
        if not self.spreadsheet_id:
            logger.warning(
                "GOOGLE_SPREADSHEET_ID no configurada. "
                "Los métodos que requieren ID de hoja fallarán."
            )
    
    def _ejecutar_solicitud(self, request, accion: str = "Acción"):
        """
        Ejecuta solicitud con manejo de errores.
        
        Args:
            request: Solicitud de Google API
            accion: Descripción de la acción (para logging)
        
        Returns:
            Respuesta o None si hay error
        """
        try:
            response = request.execute()
            logger.info(f"✓ {accion} completada")
            return response
        except HttpError as e:
            logger.error(f"✗ Error en {accion}: {str(e)}")
            return None
    
    def agregar_donacion_a_hoja(
        self,
        sheet_name: str,
        donacion: Dict[str, Any]
    ) -> bool:
        """
        Agrega un registro de donación completada a la hoja de cálculo.
        
        Args:
            sheet_name: Nombre de la hoja (ej: "Donaciones_2026_08")
            donacion: Dict con datos de donación
                {
                    "fecha": "2026-08-13",
                    "rnc_donante": "101234567",
                    "empresa": "Supermercado XYZ",
                    "ncf": "E450000000001",
                    "libras_totales": 500.00,
                    "valor_rd": 5000.00,
                    "estado": "ACEPTADO"
                }
        
        Returns:
            True si se agregó exitosamente
        
        Ejemplo de Uso:
        ```python
        service = GoogleSheetsService()
        
        donacion = {
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "rnc_donante": "101234567",
            "empresa": "Supermercado Principal",
            "ncf": "E450000000001",
            "libras_totales": 500.0,
            "valor_rd": 5000.00,
            "estado": "ACEPTADO"
        }
        
        exito = service.agregar_donacion_a_hoja("Donaciones", donacion)
        ```
        """
        if not self.spreadsheet_id:
            logger.error("spreadsheet_id no configurado")
            return False
        
        # Preparar fila
        fila = [
            donacion.get("fecha", ""),
            donacion.get("rnc_donante", ""),
            donacion.get("empresa", ""),
            donacion.get("ncf", ""),
            str(donacion.get("libras_totales", "")),
            f"{donacion.get('valor_rd', 0):.2f}",
            donacion.get("estado", "")
        ]
        
        try:
            # Solicitud para agregar fila
            request = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=f"'{sheet_name}'!A:G",
                valueInputOption="USER_ENTERED",
                body={"values": [fila]}
            )
            
            resultado = self._ejecutar_solicitud(
                request,
                f"Agregar donación a {sheet_name}"
            )
            
            return resultado is not None
        
        except Exception as e:
            logger.error(f"Error agregando donación: {str(e)}")
            return False
    
    def leer_inventario_mermas(
        self,
        sheet_name: str = "Inventario_Mermas"
    ) -> List[Dict[str, Any]]:
        """
        Lee inventario de mermas desde hoja de supermercado aliado.
        
        Estructura de hoja esperada:
        │ Producto       │ Libras │ Fecha Vencimiento │
        │ Arroz          │ 250    │ 2026-08-20        │
        │ Frijoles       │ 100    │ 2026-09-01        │
        
        Args:
            sheet_name: Nombre de la hoja con inventario
        
        Returns:
            Lista de productos disponibles
                [{
                    "producto": "Arroz",
                    "libras": 250,
                    "fecha_vencimiento": "2026-08-20"
                }, ...]
        
        Uso:
        ```python
        service = GoogleSheetsService()
        mermas = service.leer_inventario_mermas("Inventario_Mermas")
        
        for producto in mermas:
            print(f"{producto['producto']}: {producto['libras']} libras")
        ```
        """
        if not self.spreadsheet_id:
            logger.error("spreadsheet_id no configurado")
            return []
        
        try:
            # Leer datos
            request = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f"'{sheet_name}'!A:C"
            )
            
            resultado = self._ejecutar_solicitud(
                request,
                f"Leer inventario de {sheet_name}"
            )
            
            if not resultado or 'values' not in resultado:
                return []
            
            valores = resultado['values']
            productos = []
            
            # Saltar encabezado (fila 0)
            for fila in valores[1:]:
                if len(fila) >= 3:
                    productos.append({
                        "producto": fila[0],
                        "libras": float(fila[1]) if fila[1] else 0,
                        "fecha_vencimiento": fila[2]
                    })
            
            return productos
        
        except Exception as e:
            logger.error(f"Error leyendo inventario: {str(e)}")
            return []
    
    def crear_hoja_si_no_existe(
        self,
        titulo_hoja: str,
        encabezados: List[str]
    ) -> bool:
        """
        Crea una nueva hoja si no existe.
        
        Args:
            titulo_hoja: Nombre de la hoja
            encabezados: Lista de encabezados para la primera fila
        
        Returns:
            True si se creó o ya existía
        """
        if not self.spreadsheet_id:
            logger.error("spreadsheet_id no configurado")
            return False
        
        try:
            # Intentar agregar hoja
            request = self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body={
                    "requests": [{
                        "addSheet": {
                            "properties": {
                                "title": titulo_hoja
                            }
                        }
                    }]
                }
            )
            
            resultado = self._ejecutar_solicitud(
                request,
                f"Crear hoja {titulo_hoja}"
            )
            
            if resultado:
                # Agregar encabezados
                self.service.spreadsheets().values().update(
                    spreadsheetId=self.spreadsheet_id,
                    range=f"'{titulo_hoja}'!A1:G1",
                    valueInputOption="USER_ENTERED",
                    body={"values": [encabezados]}
                ).execute()
            
            return resultado is not None
        
        except HttpError as e:
            # Si la hoja ya existe, no es un error
            if "already exists" in str(e):
                return True
            logger.error(f"Error creando hoja: {str(e)}")
            return False
    
    def crear_backup_en_drive(self) -> Optional[str]:
        """
        Crea una copia de seguridad del spreadsheet en Google Drive.
        
        Returns:
            ID del archivo de respaldo o None
        """
        if not self.spreadsheet_id:
            logger.error("spreadsheet_id no configurado")
            return None
        
        try:
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file_body = {
                'name': f"Backup_Donaciones_{fecha}",
                'parents': ['root']  # Guardar en raíz de Drive
            }
            
            request = self.drive_service.files().copy(
                fileId=self.spreadsheet_id,
                body=file_body
            )
            
            resultado = self._ejecutar_solicitud(
                request,
                "Crear backup en Drive"
            )
            
            if resultado:
                return resultado.get('id')
            return None
        
        except Exception as e:
            logger.error(f"Error creando backup: {str(e)}")
            return None


class GoogleSheetsValidator:
    """
    Validador para sincronización de datos en Google Sheets.
    """
    
    @staticmethod
    def validar_donacion(donacion: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Valida que una donación tenga todos los campos requeridos.
        
        Args:
            donacion: Dict con datos de donación
        
        Returns:
            Tupla: (es_valida, lista_de_errores)
        """
        errores = []
        campos_requeridos = [
            "fecha", "rnc_donante", "empresa", "ncf",
            "libras_totales", "valor_rd", "estado"
        ]
        
        for campo in campos_requeridos:
            if campo not in donacion or not donacion[campo]:
                errores.append(f"Campo requerido faltante: {campo}")
        
        return len(errores) == 0, errores


# Ejemplo de uso
if __name__ == "__main__":
    print("📊 PRUEBA DE GOOGLE SHEETS SERVICE")
    print("=" * 60)
    
    # Nota: Requiere GOOGLE_SHEETS_CREDENTIALS en variable de entorno
    print("Para usar este servicio:")
    print("1. Crear Cuenta de Servicio en Google Cloud")
    print("2. Descargar JSON de credenciales")
    print("3. Exportar: export GOOGLE_SHEETS_CREDENTIALS='{...}'")
    print("4. Compartir hoja con email de la Cuenta de Servicio")
    print()
    
    # Simulación sin credenciales reales
    print("Estructura de datos esperada:")
    print()
    print("Donación para agregar:")
    donacion_ejemplo = {
        "fecha": "2026-08-13",
        "rnc_donante": "101234567",
        "empresa": "Supermercado Principal",
        "ncf": "E450000000001",
        "libras_totales": 500.0,
        "valor_rd": 5000.00,
        "estado": "ACEPTADO"
    }
    
    for k, v in donacion_ejemplo.items():
        print(f"  {k}: {v}")
    
    print()
    print("Inventario de mermas esperado:")
    inventario = [
        {"producto": "Arroz integral", "libras": 250, "fecha_vencimiento": "2026-08-20"},
        {"producto": "Frijoles rojos", "libras": 100, "fecha_vencimiento": "2026-09-01"}
    ]
    
    for item in inventario:
        print(f"  {item}")
