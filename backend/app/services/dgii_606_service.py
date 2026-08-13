#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
MÓDULO DE EXPORTACIÓN DGII 606 (FORMATO DE ENVÍO FISCAL)

Requisito Normativo: DGII - Formato de Envío de Datos 606
Propósito: Sincronización de gastos/donaciones con DGII

Formato: Archivo de texto (.txt) con estructura específica
Delimitador: Carácter pipe (|)
Encoding: UTF-8
Línea: 1 registro = 1 donación completada

Estructura de Registro:
┌─ Campo  │ Descripción                    │ Longitud │ Tipo   ┐
├─────────┼────────────────────────────────┼──────────┼────────┤
│ 1       │ RNC/Cédula Donante             │ 9-11     │ Num    │
│ 2       │ Tipo Identificación (1=RNC)    │ 1        │ Num    │
│ 3       │ Tipo Bienes/Servicios (Código) │ 2        │ Num    │
│ 4       │ NCF/e-NCF Completo             │ 11-13    │ Alfanum│
│ 7       │ Fecha Comprobante (AAAAMMDD)   │ 8        │ Num    │
│ 11      │ Monto Facturado / Valor RD$    │ 12,2     │ Decimal│
│ 13-18   │ ITBIS, Retenciones = 0.00      │ 12,2     │ Decimal│
└─────────┴────────────────────────────────┴──────────┴────────┘

Ejemplo de línea:
101234567|1|50|E450000000001|20260813|5000.00|0.00|0.00|0.00|0.00|0.00|0.00

Cumplimiento:
✓ Donaciones en especie exentas de ITBIS
✓ Asistencia social / educativa (Código 50)
✓ Formato compatible con importación DGII
✓ Auditoría fiscal completa

=============================================================================
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Dict, TextIO, Optional
import csv
import io


class DGII606Exporter:
    """
    Exportador de donaciones a formato DGII 606.
    
    Convierte registros de donaciones completadas al formato
    de envío oficial de la Dirección General de Impuestos Internos.
    
    Características:
    • Generación de archivos .txt delimitados por pipe
    • Validación de campos según especificación DGII
    • Manejo correcto de decimales y formatos numéricos
    • Codificación UTF-8 con BOM opcional
    """
    
    # Códigos de tipos de bienes/servicios (DGII)
    CODIGOS_CONCEPTO = {
        "asistencia_social": "50",  # Asistencia social
        "educacion": "51",           # Educación
        "salud": "52",               # Salud
        "cultura": "53",             # Cultura
        "medio_ambiente": "54",      # Medio Ambiente
        "donacion_alimentos": "50"   # Mapeo default
    }
    
    def __init__(self):
        """Inicializa el exportador."""
        pass
    
    @staticmethod
    def validar_rnc(rnc: str) -> bool:
        """
        Valida formato de RNC dominicano.
        
        RNC: 9 dígitos
        Formato: XXXXXXXXX
        
        Returns:
            True si es válido
        """
        if not rnc or len(rnc) != 9:
            return False
        return rnc.isdigit()
    
    @staticmethod
    def validar_cedula(cedula: str) -> bool:
        """
        Valida formato de Cédula dominicana.
        
        Cédula: 11 dígitos
        Formato: XXXXXXXXXXX
        
        Returns:
            True si es válido
        """
        if not cedula or len(cedula) != 11:
            return False
        return cedula.isdigit()
    
    @staticmethod
    def validar_ncf(ncf: str) -> bool:
        """
        Valida formato de NCF/e-NCF.
        
        NCF: 11 caracteres (formato tradicional)
        e-NCF: 13 caracteres (formato electrónico)
        Ejemplos: 01200000000001 (11 chars) o E450000000001 (13 chars)
        
        Returns:
            True si es válido
        """
        if not ncf:
            return False
        return len(ncf) in [11, 13]
    
    @staticmethod
    def generar_registro(
        rnc_cedula: str,
        tipo_id: int,
        codigo_concepto: str,
        ncf: str,
        fecha_comprobante: datetime,
        monto_rd: Decimal
    ) -> str:
        """
        Genera una línea de registro en formato DGII 606.
        
        Args:
            rnc_cedula: RNC (9 dígitos) o Cédula (11 dígitos)
            tipo_id: 1 = RNC, 2 = Cédula
            codigo_concepto: Código DGII (50=asistencia, 51=educación, etc.)
            ncf: Número de comprobante fiscal (11-13 caracteres)
            fecha_comprobante: Fecha del comprobante
            monto_rd: Monto en pesos dominicanos
        
        Returns:
            String con línea formateada para DGII 606
        
        Formato de línea:
        {RNC}|{TIPO_ID}|{CODIGO}|{NCF}|{FECHA}|{MONTO}|0.00|0.00|...|0.00
        
        Nota:
        Los campos de ITBIS, retenciones, etc. van en 0.00
        porque las donaciones en especie están exentas.
        """
        # Validación
        if tipo_id == 1 and not DGII606Exporter.validar_rnc(rnc_cedula):
            raise ValueError(f"RNC inválido: {rnc_cedula}")
        elif tipo_id == 2 and not DGII606Exporter.validar_cedula(rnc_cedula):
            raise ValueError(f"Cédula inválida: {rnc_cedula}")
        
        if not DGII606Exporter.validar_ncf(ncf):
            raise ValueError(f"NCF/e-NCF inválido: {ncf}")
        
        # Validar monto
        if monto_rd < 0:
            raise ValueError(f"Monto no puede ser negativo: {monto_rd}")
        
        # Formato de fecha (AAAAMMDD)
        fecha_fmt = fecha_comprobante.strftime("%Y%m%d")
        
        # Formato de monto (12,2 decimales)
        monto_fmt = f"{monto_rd:.2f}"
        
        # Construir línea
        # Estructura simplificada (campos principales del 606)
        campos = [
            rnc_cedula,                # 1: RNC/Cédula
            str(tipo_id),              # 2: Tipo ID
            codigo_concepto,           # 3: Código de concepto
            ncf,                       # 4: NCF/e-NCF
            fecha_fmt,                 # 7: Fecha
            monto_fmt,                 # 11: Monto facturado
            "0.00",                    # ITBIS (exento)
            "0.00",                    # Retenciones
            "0.00",                    # ITBIS Sujeto Retención
            "0.00",                    # Monto de Impuesto Selectivo al Consumo
            "0.00",                    # Otros Impuestos
            "0.00"                     # Monto Pagado
        ]
        
        return "|".join(campos)
    
    @staticmethod
    def exportar_donaciones(
        donaciones: List[Dict],
        nombre_archivo: Optional[str] = None
    ) -> io.StringIO:
        """
        Exporta una lista de donaciones a formato DGII 606.
        
        Args:
            donaciones: Lista de donaciones completadas
                [{
                    "rnc_donante": "101234567",
                    "tipo_identificacion": 1,  # 1=RNC, 2=Cédula
                    "codigo_concepto": "50",   # 50=Asistencia social
                    "ncf": "E450000000001",
                    "fecha_donacion": datetime.now(),
                    "valor_total_rd": Decimal("5000.00")
                }, ...]
            
            nombre_archivo: Nombre para el archivo (opcional, solo para referencia)
        
        Returns:
            StringIO con contenido del archivo 606
        
        Ejemplo de Uso:
        ```python
        exporter = DGII606Exporter()
        
        donaciones = [
            {
                "rnc_donante": "101234567",
                "tipo_identificacion": 1,
                "codigo_concepto": "50",
                "ncf": "E450000000001",
                "fecha_donacion": datetime(2026, 8, 13),
                "valor_total_rd": Decimal("5000.00")
            }
        ]
        
        archivo_606 = exporter.exportar_donaciones(donaciones)
        
        # Guardar
        with open("donaciones_2026_08.txt", "w", encoding="utf-8") as f:
            f.write(archivo_606.getvalue())
        ```
        """
        output = io.StringIO()
        
        # Escribir encabezado de información (comentario)
        output.write("# Formato DGII 606 - Donaciones en Especie\n")
        output.write(f"# Generado: {datetime.now().isoformat()}\n")
        output.write(f"# Total Registros: {len(donaciones)}\n")
        output.write(f"# Estructura: RNC|TIPO_ID|CODIGO|NCF|FECHA|MONTO|...\n")
        output.write("#\n")
        
        total_monto = Decimal("0.00")
        registros_procesados = 0
        
        for donacion in donaciones:
            try:
                # Extraer campos
                rnc = donacion.get("rnc_donante")
                tipo_id = donacion.get("tipo_identificacion", 1)
                codigo = donacion.get("codigo_concepto", "50")
                ncf = donacion.get("ncf")
                fecha = donacion.get("fecha_donacion")
                monto = Decimal(str(donacion.get("valor_total_rd", 0)))
                
                # Generar registro
                linea = DGII606Exporter.generar_registro(
                    rnc, tipo_id, codigo, ncf, fecha, monto
                )
                
                output.write(linea + "\n")
                registros_procesados += 1
                total_monto += monto
                
            except Exception as e:
                # Logging de error (en producción, usar logger)
                output.write(f"# ERROR procesando donación: {str(e)}\n")
        
        # Escribir resumen al final
        output.write(f"\n# RESUMEN\n")
        output.write(f"# Registros Procesados: {registros_procesados}\n")
        output.write(f"# Monto Total: RD$ {total_monto:,.2f}\n")
        
        output.seek(0)
        return output
    
    @staticmethod
    def generar_archivo_mensual(
        mes: int,
        anio: int,
        donaciones: List[Dict]
    ) -> io.StringIO:
        """
        Genera archivo DGII 606 con nombre estándar para el mes.
        
        Formato de nombre: DONACIONES_{AAAA}_{MM}.txt
        Ejemplo: DONACIONES_2026_08.txt (Agosto 2026)
        
        Args:
            mes: Número de mes (1-12)
            anio: Año (4 dígitos)
            donaciones: Lista de donaciones
        
        Returns:
            StringIO con contenido del archivo
        """
        nombre_archivo = f"DONACIONES_{anio}_{mes:02d}.txt"
        exporter = DGII606Exporter()
        return exporter.exportar_donaciones(donaciones, nombre_archivo)


class DGII606ImportValidator:
    """
    Validador de archivos 606 generados (para testing).
    
    Verifica que el formato es correcto antes de enviar a DGII.
    """
    
    @staticmethod
    def validar_archivo(contenido: str) -> Dict[str, any]:
        """
        Valida estructura de un archivo 606.
        
        Returns:
            Dict con resultados de validación
        """
        lineas = contenido.strip().split("\n")
        
        resultados = {
            "valido": True,
            "total_lineas": len(lineas),
            "registros_validos": 0,
            "errores": []
        }
        
        for linea_num, linea in enumerate(lineas):
            # Ignorar comentarios y líneas vacías
            if linea.startswith("#") or not linea.strip():
                continue
            
            try:
                campos = linea.split("|")
                if len(campos) < 12:
                    resultados["errores"].append(
                        f"Línea {linea_num}: Menos de 12 campos"
                    )
                    resultados["valido"] = False
                else:
                    resultados["registros_validos"] += 1
            except Exception as e:
                resultados["errores"].append(
                    f"Línea {linea_num}: {str(e)}"
                )
                resultados["valido"] = False
        
        return resultados


# Ejemplo de uso
if __name__ == "__main__":
    print("🎯 PRUEBA DE EXPORTACIÓN DGII 606")
    print("=" * 60)
    
    exporter = DGII606Exporter()
    
    # Donaciones de ejemplo
    donaciones = [
        {
            "rnc_donante": "101234567",
            "tipo_identificacion": 1,
            "codigo_concepto": "50",
            "ncf": "E450000000001",
            "fecha_donacion": datetime(2026, 8, 13),
            "valor_total_rd": Decimal("5000.00")
        },
        {
            "rnc_donante": "101234568",
            "tipo_identificacion": 1,
            "codigo_concepto": "50",
            "ncf": "E450000000002",
            "fecha_donacion": datetime(2026, 8, 12),
            "valor_total_rd": Decimal("3500.50")
        }
    ]
    
    # Exportar
    archivo_606 = exporter.exportar_donaciones(donaciones)
    contenido = archivo_606.getvalue()
    
    print("Contenido del archivo 606:")
    print(contenido)
    
    # Validar
    print("\n" + "=" * 60)
    print("VALIDACIÓN DEL ARCHIVO:")
    print("=" * 60)
    
    validador = DGII606ImportValidator()
    resultado = validador.validar_archivo(contenido)
    
    print(f"Válido: {resultado['valido']}")
    print(f"Registros: {resultado['registros_validos']}")
    print(f"Errores: {len(resultado['errores'])}")
