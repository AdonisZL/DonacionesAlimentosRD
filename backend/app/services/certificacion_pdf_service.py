#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
MÓDULO DE GENERACIÓN DE CERTIFICACIÓN FISCAL PDF (e-CF Tipo 45/NCF Tipo 15)

Requisito Normativo: Ley 11-92, DGII, Código Tributario Dominicano Art. 287

Documento Generado:
• Tipo: Certificación Fiscal de Donación (e-CF 45 / NCF 15)
• Propósito: Deducibilidad de donaciones ISR hasta 5%
• Cumplimiento: Artículo 287 del Código Tributario
• Formato: PDF profesional con firma digital

Contenido Obligatorio:
✓ Encabezado con datos de la institución receptora (ASFL/Banco)
✓ Datos del donante (Razón Social, RNC 9 dígitos)
✓ Número de e-NCF (Formato: E450000000001 o B1500000001)
✓ Fecha de emisión (DD/MM/AAAA)
✓ UUID de trazabilidad fiscal
✓ Tabla detallada de alimentos donados (Descripción, Cantidad, Valor RD$)
✓ Monto total en RD$
✓ Pie de página con texto legal (Artículo 287)
✓ Área de firma digital/fotográfica

Cumplimiento DGII:
• Formato compatible con importación al sistema DGII
• Estructura de datos fiscalmente válida
• Trazabilidad completa (UUID único por documento)

=============================================================================
"""

import io
import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Optional, BinaryIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    PageBreak, Image
)
import hashlib


class CertificacionFiscalPDF:
    """
    Generador de Certificación Fiscal de Donación en PDF.
    
    Cumple con:
    • Formato de Certificación Fiscal Dominicana
    • Ley 11-92 (Régimen Tributario)
    • Artículo 287 (Deducción de donaciones)
    • DGII (Dirección General de Impuestos Internos)
    
    Estructura del documento:
    1. Encabezado (Logo, datos institución)
    2. Título ("CERTIFICACIÓN DE DONACIÓN")
    3. Datos del Donante y Receptor
    4. Datos Fiscales (e-NCF, UUID, Fecha)
    5. Tabla de Alimentos Donados
    6. Resumen (Cantidad total, Valor total RD$)
    7. Pie de página legal
    8. Áreas de firma
    """
    
    # Constantes de configuración
    PAPEL = letter  # 8.5" x 11"
    MARGEN = 0.5 * inch
    ANCHO_EFECTIVO = PAPEL[0] - (2 * MARGEN)
    
    # Datos de la institución receptora (BANCO DE ALIMENTOS)
    INSTITUCION = {
        "nombre": "BANCO DE ALIMENTOS DE LA REPÚBLICA DOMINICANA",
        "rnc": "101234567",  # RNC ficticio para demostración
        "telefono": "+1-809-000-0002",
        "direccion": "Avenida 27 de Febrero #123, Santo Domingo",
        "email": "banco@donacionesalimentos.com"
    }
    
    def __init__(self):
        """Inicializa el generador de certificaciones."""
        self.stylesheet = getSampleStyleSheet()
        self._setup_estilos()
    
    def _setup_estilos(self):
        """Define estilos personalizados para el PDF."""
        self.stylesheet.add(ParagraphStyle(
            name='Titulo',
            parent=self.stylesheet['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1a472a'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.stylesheet.add(ParagraphStyle(
            name='Subtitle',
            parent=self.stylesheet['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#2d5a3d'),
            spaceAfter=6,
            alignment=TA_CENTER
        ))
        
        self.stylesheet.add(ParagraphStyle(
            name='Label',
            parent=self.stylesheet['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#333333'),
            spaceAfter=3
        ))
        
        self.stylesheet.add(ParagraphStyle(
            name='Valor',
            parent=self.stylesheet['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#000000'),
            fontName='Helvetica-Bold',
            spaceAfter=3
        ))
    
    def generar_ncf(self) -> str:
        """
        Genera un número e-NCF único (Número de Comprobante Fiscal).
        
        Formato: E45 + 10 dígitos secuenciales
        Ejemplo: E450000000001
        
        En producción, validar contra DGII y usar secuencia real.
        Para demostración, generar aleatorio manteniendo formato.
        
        Estructura DGII:
        • Posiciones 1-3: Tipo de comprobante (E45 = e-CF Tipo 45)
        • Posiciones 4-13: Secuencial único por año
        
        Returns:
            String con formato E450000000001
        """
        # Generar 10 dígitos aleatorios
        secuencial = str(uuid.uuid4().int % 10000000000).zfill(10)
        return f"E45{secuencial}"
    
    def generar_uuid_fiscal(self) -> str:
        """
        Genera UUID único para trazabilidad fiscal.
        
        En producción: Emitido por DGII
        Para demo: UUID v4 estándar
        """
        return str(uuid.uuid4())
    
    def generar_hash_documento(self, contenido: str) -> str:
        """
        Genera hash SHA-256 del documento para integridad (Hallazgo 8).
        
        Args:
            contenido: Contenido serializador del PDF
        
        Returns:
            Hash SHA-256 para almacenar en BD
        """
        return hashlib.sha256(contenido.encode('utf-8')).hexdigest()
    
    def crear_certificacion(
        self,
        donante: Dict[str, str],
        detalles_alimentos: List[Dict],
        fecha_donacion: datetime,
        uuid_fiscal: Optional[str] = None,
        ncf: Optional[str] = None
    ) -> BinaryIO:
        """
        Crea la Certificación Fiscal en formato PDF.
        
        Args:
            donante: Dict con datos del donante
                {
                    "razon_social": "Supermercado XYZ S.A.",
                    "rnc": "101234567",
                    "direccion": "Calle Principal #100",
                    "telefono": "+1-809-555-5555"
                }
            
            detalles_alimentos: Lista de Dict con items
                [{
                    "descripcion": "Arroz integral",
                    "cantidad_kg": 250.50,
                    "valor_unitario_rd": Decimal("15.00"),
                    "cantidad": 250.50  # Kilos
                }, ...]
            
            fecha_donacion: datetime de la donación
            uuid_fiscal: UUID para trazabilidad (autogenera si es None)
            ncf: Número e-NCF (autogenera si es None)
        
        Returns:
            BinaryIO: Buffer con PDF listo para guardar/enviar
        
        Ejemplo de Uso:
        ```python
        pdf_gen = CertificacionFiscalPDF()
        
        buffer_pdf = pdf_gen.crear_certificacion(
            donante={
                "razon_social": "Supermercado Principal",
                "rnc": "101234567",
                "direccion": "Avenida 27 de Febrero",
                "telefono": "+1-809-555-5555"
            },
            detalles_alimentos=[
                {
                    "descripcion": "Arroz integral",
                    "cantidad_kg": 250.50,
                    "valor_unitario_rd": Decimal("15.00")
                },
                {
                    "descripcion": "Frijoles rojos",
                    "cantidad_kg": 100.00,
                    "valor_unitario_rd": Decimal("25.00")
                }
            ],
            fecha_donacion=datetime.now()
        )
        
        # Guardar
        with open("certificacion_fiscal.pdf", "wb") as f:
            f.write(buffer_pdf.getvalue())
        ```
        """
        # Autogenerar si no se proporciona
        if not uuid_fiscal:
            uuid_fiscal = self.generar_uuid_fiscal()
        if not ncf:
            ncf = self.generar_ncf()
        
        # Crear buffer
        buffer = io.BytesIO()
        
        # Crear documento PDF
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=self.MARGEN,
            leftMargin=self.MARGEN,
            topMargin=self.MARGEN,
            bottomMargin=self.MARGEN,
            title="Certificación de Donación"
        )
        
        # Elementos del PDF
        elementos = []
        
        # 1. ENCABEZADO CON DATOS DE LA INSTITUCIÓN
        elementos.append(Spacer(1, 0.2 * inch))
        
        titulo_inst = Paragraph(
            f"<b>{self.INSTITUCION['nombre']}</b>",
            self.stylesheet['Titulo']
        )
        elementos.append(titulo_inst)
        
        datos_inst = f"""
        <font size=9>
        RNC: {self.INSTITUCION['rnc']} | Teléfono: {self.INSTITUCION['telefono']}<br/>
        {self.INSTITUCION['direccion']}<br/>
        Email: {self.INSTITUCION['email']}
        </font>
        """
        elementos.append(Paragraph(datos_inst, self.stylesheet['Normal']))
        elementos.append(Spacer(1, 0.15 * inch))
        
        # Línea divisoria
        elementos.append(Paragraph("<hr/>", self.stylesheet['Normal']))
        elementos.append(Spacer(1, 0.15 * inch))
        
        # 2. TÍTULO
        titulo = Paragraph(
            "<b>CERTIFICACIÓN DE DONACIÓN EN ESPECIE</b><br/>"
            "<font size=10>Ley 11-92 del Régimen Tributario Dominicano</font>",
            ParagraphStyle(
                'titulo_cert',
                parent=self.stylesheet['Normal'],
                fontSize=12,
                textColor=colors.HexColor('#1a472a'),
                alignment=TA_CENTER,
                spaceAfter=12
            )
        )
        elementos.append(titulo)
        elementos.append(Spacer(1, 0.1 * inch))
        
        # 3. DATOS FISCALES (NCF, UUID, Fecha)
        datos_fiscales = f"""
        <font size=9>
        <b>e-NCF (Comprobante Fiscal):</b> {ncf}<br/>
        <b>Fecha de Emisión:</b> {fecha_donacion.strftime('%d/%m/%Y')}<br/>
        <b>Trazabilidad UUID:</b> {uuid_fiscal}<br/>
        <b>Hora de Emisión:</b> {fecha_donacion.strftime('%H:%M:%S')} (Zona EST)
        </font>
        """
        elementos.append(Paragraph(datos_fiscales, self.stylesheet['Normal']))
        elementos.append(Spacer(1, 0.15 * inch))
        
        # 4. SECCIÓN: DONANTE
        elementos.append(Paragraph(
            "<b>1. DATOS DEL DONANTE:</b>",
            ParagraphStyle('section', parent=self.stylesheet['Normal'], fontSize=10, fontName='Helvetica-Bold')
        ))
        
        datos_donante = f"""
        <font size=9>
        <b>Razón Social:</b> {donante['razon_social']}<br/>
        <b>RNC:</b> {donante['rnc']}<br/>
        <b>Dirección:</b> {donante['direccion']}<br/>
        <b>Teléfono:</b> {donante['telefono']}
        </font>
        """
        elementos.append(Paragraph(datos_donante, self.stylesheet['Normal']))
        elementos.append(Spacer(1, 0.15 * inch))
        
        # 5. SECCIÓN: RECEPTOR
        elementos.append(Paragraph(
            "<b>2. DATOS DE LA INSTITUCIÓN RECEPTORA:</b>",
            ParagraphStyle('section', parent=self.stylesheet['Normal'], fontSize=10, fontName='Helvetica-Bold')
        ))
        
        datos_receptor = f"""
        <font size=9>
        <b>Institución:</b> {self.INSTITUCION['nombre']}<br/>
        <b>RNC:</b> {self.INSTITUCION['rnc']}<br/>
        <b>Dirección:</b> {self.INSTITUCION['direccion']}<br/>
        <b>Autorización DGII:</b> Resolución 07-17
        </font>
        """
        elementos.append(Paragraph(datos_receptor, self.stylesheet['Normal']))
        elementos.append(Spacer(1, 0.15 * inch))
        
        # 6. TABLA DE DESGLOSE DE ALIMENTOS
        elementos.append(Paragraph(
            "<b>3. DESCRIPCIÓN DE ALIMENTOS DONADOS:</b>",
            ParagraphStyle('section', parent=self.stylesheet['Normal'], fontSize=10, fontName='Helvetica-Bold')
        ))
        
        datos_tabla = [
            ['Descripción del Alimento', 'Cantidad (kg)', 'Valor Unitario (RD$)', 'Valor Total (RD$)']
        ]
        
        total_kg = Decimal("0")
        total_rd = Decimal("0")
        
        for item in detalles_alimentos:
            cantidad = Decimal(str(item.get('cantidad_kg', 0)))
            valor_unitario = Decimal(str(item.get('valor_unitario_rd', 0)))
            valor_total = cantidad * valor_unitario
            
            total_kg += cantidad
            total_rd += valor_total
            
            datos_tabla.append([
                item.get('descripcion', ''),
                f"{cantidad:.2f}",
                f"{valor_unitario:.2f}",
                f"{valor_total:.2f}"
            ])
        
        # Fila de totales
        datos_tabla.append([
            '<b>TOTALES</b>',
            f'<b>{total_kg:.2f}</b>',
            '',
            f'<b>RD$ {total_rd:.2f}</b>'
        ])
        
        tabla_estilos = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a472a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8f5e9')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f5f5f5')])
        ])
        
        tabla = Table(datos_tabla, colWidths=[2.0*inch, 1.2*inch, 1.3*inch, 1.5*inch])
        tabla.setStyle(tabla_estilos)
        elementos.append(tabla)
        elementos.append(Spacer(1, 0.15 * inch))
        
        # 7. RESUMEN
        resumen = f"""
        <font size=10>
        <b>Resumen de Donación:</b><br/>
        • Cantidad Total: <b>{total_kg:.2f} kg</b><br/>
        • Valor Total Estimado: <b>RD$ {total_rd:,.2f}</b><br/>
        • Fecha: <b>{fecha_donacion.strftime('%d de %B de %Y')}</b>
        </font>
        """
        elementos.append(Paragraph(resumen, self.stylesheet['Normal']))
        elementos.append(Spacer(1, 0.2 * inch))
        
        # 8. PIE DE PÁGINA LEGAL
        pie_legal = f"""
        <font size=8 color="darkred">
        <b>NOTA LEGAL - Artículo 287 del Código Tributario Dominicano:</b><br/>
        Esta certificación acredita una donación en especie realizada a {self.INSTITUCION['nombre']},
        entidad autorizada para recibir donaciones deducibles del ISR según la Ley 11-92.
        El donante puede deducir hasta el 5% de su renta bruta por concepto de donaciones.
        Este documento tiene validez fiscal y debe conservarse por un período mínimo de 4 años.
        <br/><br/>
        <b>Certificamos bajo juramento que los datos contenidos en este documento son veraces y
        corresponden a la donación en especie realizada en la fecha y hora indicadas.</b>
        </font>
        """
        elementos.append(Paragraph(pie_legal, self.stylesheet['Normal']))
        elementos.append(Spacer(1, 0.2 * inch))
        
        # 9. ÁREAS DE FIRMA
        firma_html = """
        <table width="100%">
        <tr>
            <td width="50%" align="center" valign="bottom">
                <font size=8><u>_________________________________</u><br/>
                Firma del Donante<br/>
                Cédula/RNC: ________________________<br/>
                Fecha: ________________________</font>
            </td>
            <td width="50%" align="center" valign="bottom">
                <font size=8><u>_________________________________</u><br/>
                Autorizado por Banco de Alimentos<br/>
                Nombre y Cargo:<br/>
                Fecha: ________________________</font>
            </td>
        </tr>
        </table>
        """
        elementos.append(Paragraph(firma_html, self.stylesheet['Normal']))
        elementos.append(Spacer(1, 0.2 * inch))
        
        # Línea final de referencia
        referencia = f"""
        <font size=7 color="gray">
        Referencia del Sistema: {uuid_fiscal[:8]}... | Documento Generado: {datetime.now().isoformat()}
        </font>
        """
        elementos.append(Paragraph(referencia, self.stylesheet['Normal']))
        
        # Construir PDF
        doc.build(elementos)
        buffer.seek(0)
        
        return buffer


# Ejemplo de uso
if __name__ == "__main__":
    pdf_gen = CertificacionFiscalPDF()
    
    # Datos de ejemplo
    donante = {
        "razon_social": "SUPERMERCADO PRINCIPAL S.A.",
        "rnc": "101234567",
        "direccion": "Avenida 27 de Febrero #123, Santo Domingo",
        "telefono": "+1-809-555-5555"
    }
    
    alimentos = [
        {"descripcion": "Arroz integral premium", "cantidad_kg": Decimal("250.50"), "valor_unitario_rd": Decimal("15.00")},
        {"descripcion": "Frijoles rojos", "cantidad_kg": Decimal("100.00"), "valor_unitario_rd": Decimal("25.00")},
        {"descripcion": "Aceite de oliva", "cantidad_kg": Decimal("50.00"), "valor_unitario_rd": Decimal("45.00")},
    ]
    
    # Generar
    buffer = pdf_gen.crear_certificacion(
        donante=donante,
        detalles_alimentos=alimentos,
        fecha_donacion=datetime.now()
    )
    
    # Guardar
    with open("certificacion_demo.pdf", "wb") as f:
        f.write(buffer.getvalue())
    
    print(f"✓ PDF generado: certificacion_demo.pdf")
    print(f"✓ Tamaño: {len(buffer.getvalue()) / 1024:.2f} KB")
