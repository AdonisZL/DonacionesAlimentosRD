#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
MÓDULO DE SCORING FEFO (First Expired, First Out)

Requisito de Negocio: OE3 - Deterministic Matching with PostGIS + FEFO

Algoritmo FEFO:
✓ Prioriza alimentos cercanos a vencimiento (urgencia)
✓ Combina distancia geográfica (PostGIS) con fecha de vencimiento
✓ Genera score numérico para ranking de emparejamientos
✓ Integrable con IA para justificación automática

Criterios de Scoring:
1. VENCIMIENTO (peso: 60%) - Urgencia
   • 0 días restantes = score 100 (máxima urgencia)
   • 30+ días restantes = score 0 (baja urgencia)
2. DISTANCIA (peso: 25%) - Logística
   • 0 km = score 0 (misma ubicación)
   • 75 km = score 100 (límite máximo, score malo)
3. CAPACIDAD (peso: 15%) - Compatibilidad
   • Receptor puede aceptar cantidad = score 100
   • Receptor con capacidad limitada = ajuste proporcional

Score Final = (vencimiento_ponderado * 0.6) + 
              (distancia_ponderada * 0.25) + 
              (capacidad_ponderada * 0.15)

Rango: 0-100 (100 = emparejamiento EXCELENTE)

Casos de Uso:
→ Emparejamiento automático de lotes
→ Ranking de sugerencias al operador
→ Optimización logística de distribución

=============================================================================
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple, List
from decimal import Decimal
import math


class FEFOScoringEngine:
    """
    Motor de puntuación FEFO para emparejamientos de donaciones.
    
    Calcula prioridad de distribución basada en:
    • Proximidad a vencimiento
    • Distancia geográfica
    • Capacidad del receptor
    
    Salida: Puntuación 0-100 (100 = mejor emparejamiento)
    """
    
    # Constantes de configuración
    DIAS_VENTANA_MAXIMA = 30  # Días máximos antes de vencimiento para considerar
    DISTANCIA_MAXIMA_KM = 75  # Límite máximo según RN-14
    DIAS_CRITICOS_PERECEDERO = 1  # Días para considerar crítico
    
    @staticmethod
    def calcular_score_vencimiento(
        dias_para_vencer: int,
        es_perecedero: bool = False
    ) -> float:
        """
        Calcula score basado en proxim idad a vencimiento.
        
        Args:
            dias_para_vencer: Días restantes hasta vencimiento (negativo = ya vencido)
            es_perecedero: Si es perecedero (Ley RN-05)
        
        Returns:
            Score 0-100 (100 = urgente, 0 = no urgente)
        
        Lógica:
        • Si días ≤ 0 → score 100 (CRÍTICO, actuar inmediatamente)
        • Si días 1-7 → score 85-100 (URGENTE)
        • Si días 8-15 → score 60-85 (IMPORTANTE)
        • Si días 16-30 → score 30-60 (NORMAL)
        • Si días > 30 → score 0-30 (BAJO)
        
        Para perecederos, reducir los rangos (más urgencia):
        • Críticos si ≤ 1 día (vs 3 días para no perecederos)
        """
        # Casos especiales
        if dias_para_vencer <= 0:
            return 100.0  # YA VENCIDO O CRÍTICO
        
        if es_perecedero:
            # Para perecederos, es más urgente
            if dias_para_vencer <= 1:
                return 100.0
            elif dias_para_vencer <= 3:
                return 90.0
            elif dias_para_vencer <= 7:
                return 75.0
            elif dias_para_vencer <= 14:
                return 50.0
            else:
                return 25.0
        else:
            # Para no perecederos, más tolerancia
            if dias_para_vencer <= 3:
                return 90.0
            elif dias_para_vencer <= 7:
                return 75.0
            elif dias_para_vencer <= 14:
                return 60.0
            elif dias_para_vencer <= 30:
                return 40.0
            else:
                return 10.0
    
    @staticmethod
    def calcular_score_distancia(distancia_km: float) -> float:
        """
        Calcula score basado en distancia geográfica.
        
        Args:
            distancia_km: Distancia en kilómetros
        
        Returns:
            Score 0-100 (100 = cercano, 0 = muy lejano)
        
        Lógica:
        • 0 km → 100 (Mismo lugar)
        • 5 km → 95 (Muy cercano)
        • 25 km → 60 (Medio)
        • 50 km → 25 (Lejano)
        • 75 km → 0 (Límite máximo, rechazar)
        • > 75 km → -infinito (NO VÁLIDO)
        
        Fórmula: score = max(0, 100 - (distancia / 75 * 100))
        """
        if distancia_km > FEFOScoringEngine.DISTANCIA_MAXIMA_KM:
            return 0.0  # Fuera del alcance
        
        if distancia_km < 0:
            return 0.0  # Distancia inválida
        
        # Fórmula lineal: decae a medida que aumenta distancia
        score = 100.0 * (1 - (distancia_km / FEFOScoringEngine.DISTANCIA_MAXIMA_KM))
        return max(0.0, min(100.0, score))
    
    @staticmethod
    def calcular_score_capacidad(
        cantidad_kg: Decimal,
        capacidad_disponible_kg: Decimal,
        tiene_cadena_frio_requerida: bool = True
    ) -> float:
        """
        Calcula score basado en compatibilidad de capacidad.
        
        Args:
            cantidad_kg: Kilos del lote de donación
            capacidad_disponible_kg: Capacidad disponible del receptor
            tiene_cadena_frio_requerida: Si el lote requiere cadena frío
        
        Returns:
            Score 0-100
        
        Lógica:
        • Si el receptor NO tiene capacidad = 0
        • Si cantidad > capacidad disponible = 50 (parcial)
        • Si cantidad <= capacidad disponible = 100 (completo)
        • Si falta cadena frío pero se requiere = 25 (incompatible)
        
        Nota:
        La capacidad se evalúa diariamente:
        capacidad_disponible = capacidad_diaria_kg - ya_asignado_hoy
        """
        # Validación de cadena frío
        if tiene_cadena_frio_requerida and not tiene_cadena_frio_requerida:
            return 25.0  # Incompatible pero posible (con precaución)
        
        # Validación de cantidad
        if cantidad_kg <= 0:
            return 0.0
        
        if capacidad_disponible_kg <= 0:
            return 0.0
        
        # Cálculo de compatibilidad
        if cantidad_kg <= capacidad_disponible_kg:
            return 100.0  # Cabe perfectamente
        elif cantidad_kg <= (capacidad_disponible_kg * Decimal("1.5")):
            return 60.0  # Cabe parcialmente
        else:
            return 20.0  # No cabe, riesgo muy alto
    
    @staticmethod
    def calcular_score_final(
        dias_para_vencer: int,
        distancia_km: float,
        cantidad_kg: Decimal,
        capacidad_disponible_kg: Decimal,
        es_perecedero: bool = False,
        tiene_cadena_frio_requerida: bool = False
    ) -> Dict[str, float]:
        """
        Calcula el score FEFO final ponderado.
        
        Args:
            dias_para_vencer: Días restantes antes de vencimiento
            distancia_km: Distancia en km
            cantidad_kg: Kilos del lote
            capacidad_disponible_kg: Capacidad del receptor
            es_perecedero: Si es perecedero
            tiene_cadena_frio_requerida: Si requiere cadena frío
        
        Returns:
            Dict con desglose de scores y score final
        
        Ejemplo:
        ```python
        engine = FEFOScoringEngine()
        resultado = engine.calcular_score_final(
            dias_para_vencer=5,        # Vence en 5 días
            distancia_km=15.5,         # 15.5 km de distancia
            cantidad_kg=Decimal("500"), # 500 kg de alimento
            capacidad_disponible_kg=Decimal("1000"),  # Receptor con 1000kg disponibles
            es_perecedero=True,
            tiene_cadena_frio_requerida=True
        )
        # resultado = {
        #    "score_vencimiento": 90.0,
        #    "score_distancia": 79.3,
        #    "score_capacidad": 100.0,
        #    "score_final": 86.5  # Ponderado
        # }
        ```
        """
        # Calcular componentes individuales
        score_vencimiento = FEFOScoringEngine.calcular_score_vencimiento(
            dias_para_vencer,
            es_perecedero
        )
        score_distancia = FEFOScoringEngine.calcular_score_distancia(distancia_km)
        score_capacidad = FEFOScoringEngine.calcular_score_capacidad(
            cantidad_kg,
            capacidad_disponible_kg,
            tiene_cadena_frio_requerida
        )
        
        # Ponderación: 60% vencimiento, 25% distancia, 15% capacidad
        score_final = (
            (score_vencimiento * 0.60) +
            (score_distancia * 0.25) +
            (score_capacidad * 0.15)
        )
        
        # Normalizar a 0-100
        score_final = max(0.0, min(100.0, score_final))
        
        return {
            "score_vencimiento": round(score_vencimiento, 2),
            "score_distancia": round(score_distancia, 2),
            "score_capacidad": round(score_capacidad, 2),
            "score_final": round(score_final, 2),
            "peso_vencimiento": 0.60,
            "peso_distancia": 0.25,
            "peso_capacidad": 0.15
        }
    
    @staticmethod
    def generar_justificacion_ia(scores: Dict[str, float], metadata: Dict = None) -> str:
        """
        Genera una justificación en lenguaje natural del scoring.
        
        Args:
            scores: Dict retornado por calcular_score_final()
            metadata: Dict con info adicional (es_perecedero, dias_vencimiento, etc)
        
        Returns:
            String con justificación en español
        
        Uso:
        ```python
        engine = FEFOScoringEngine()
        scores = engine.calcular_score_final(...)
        justificacion = engine.generar_justificacion_ia(
            scores,
            metadata={
                "dias_vencimiento": 5,
                "distancia": 15.5,
                "es_perecedero": True
            }
        )
        # Retorna:
        # "Emparejamiento de ALTA PRIORIDAD (Score 86.5/100). 
        #  Producto perecedero que vence en 5 días (Urgencia: CRÍTICA). 
        #  Distancia a receptor: 15.5 km (Próximo). 
        #  Capacidad compatible (500kg de 1000kg disponibles).
        #  Recomendación: CONFIRMAR para distribución hoy."
        ```
        """
        score = scores.get("score_final", 0)
        
        # Determinar nivel de prioridad
        if score >= 85:
            prioridad = "CRÍTICA"
            recomendacion = "CONFIRMAR INMEDIATAMENTE"
        elif score >= 70:
            prioridad = "ALTA"
            recomendacion = "CONFIRMAR"
        elif score >= 50:
            prioridad = "NORMAL"
            recomendacion = "CONSIDERAR"
        else:
            prioridad = "BAJA"
            recomendacion = "EVALUAR OTRAS OPCIONES"
        
        # Construir justificación
        justificacion = f"Emparejamiento de PRIORIDAD {prioridad} (Score: {score:.1f}/100). "
        
        if metadata:
            dias = metadata.get("dias_vencimiento")
            distancia = metadata.get("distancia")
            es_perecedero = metadata.get("es_perecedero")
            
            if dias is not None:
                if dias <= 0:
                    justificacion += f"⚠️ ALERTA: Producto ya vencido o vence HOY. "
                elif dias <= 3:
                    justificacion += f"🔴 Producto perecedero vence en {dias} día(s) (URGENTE). "
                elif dias <= 7:
                    justificacion += f"🟡 Producto vence en {dias} días. "
                else:
                    justificacion += f"🟢 Producto con {dias} días restantes. "
            
            if distancia is not None:
                if distancia <= 5:
                    justificacion += f"✓ Receptor muy cercano ({distancia:.1f} km). "
                elif distancia <= 25:
                    justificacion += f"✓ Distancia moderada ({distancia:.1f} km). "
                else:
                    justificacion += f"⚠️ Distancia considerable ({distancia:.1f} km). "
        
        justificacion += f"Recomendación: {recomendacion}."
        
        return justificacion
    
    @staticmethod
    def rankear_emparejamientos(emparejamientos: List[Dict]) -> List[Dict]:
        """
        Rankea una lista de emparejamientos posibles de mayor a menor score.
        
        Args:
            emparejamientos: Lista de dicts con datos de lote y receptor
            [{
                "id_emparejamiento": "...",
                "dias_para_vencer": 5,
                "distancia_km": 15.5,
                "cantidad_kg": 500,
                "capacidad_disponible_kg": 1000,
                "es_perecedero": True
            }, ...]
        
        Returns:
            Lista ordenada por score_final descendente
        
        Uso Típico:
        ```python
        # Obtener todos los emparejamientos posibles para un lote
        candidatos = session.query(Emparejamiento).filter(
            Emparejamiento.id_lote == lote_id,
            Emparejamiento.estado == "sugerido"
        ).all()
        
        # Convertir a dicts
        dicts = [{
            "id_emparejamiento": str(e.id_emparejamiento),
            "dias_para_vencer": (e.fecha_limite_retiro - datetime.now()).days,
            ...
        } for e in candidatos]
        
        # Rankear
        engine = FEFOScoringEngine()
        ranking = engine.rankear_emparejamientos(dicts)
        
        # El primero es la mejor opción
        mejor_opcion = ranking[0]
        ```
        """
        engine = FEFOScoringEngine()
        
        # Calcular scores
        for emparejamiento in emparejamientos:
            scores = engine.calcular_score_final(
                dias_para_vencer=emparejamiento.get("dias_para_vencer", 0),
                distancia_km=float(emparejamiento.get("distancia_km", 0)),
                cantidad_kg=Decimal(str(emparejamiento.get("cantidad_kg", 0))),
                capacidad_disponible_kg=Decimal(str(emparejamiento.get("capacidad_disponible_kg", 0))),
                es_perecedero=emparejamiento.get("es_perecedero", False),
                tiene_cadena_frio_requerida=emparejamiento.get("tiene_cadena_frio_requerida", False)
            )
            emparejamiento["scores"] = scores
            emparejamiento["score_final"] = scores["score_final"]
            
            # Agregar justificación
            emparejamiento["justificacion"] = engine.generar_justificacion_ia(
                scores,
                metadata={
                    "dias_vencimiento": emparejamiento.get("dias_para_vencer"),
                    "distancia": emparejamiento.get("distancia_km"),
                    "es_perecedero": emparejamiento.get("es_perecedero")
                }
            )
        
        # Ordenar por score final (descendente)
        emparejamientos.sort(
            key=lambda x: x.get("score_final", 0),
            reverse=True
        )
        
        return emparejamientos


# =============================================================================
# INTEGRACIÓN CON SERVICIOS DE EMPAREJAMIENTO
# =============================================================================

"""
En app/services/servicio_emparejamiento.py:

def buscar_emparejamientos_para_lote(lote_id):
    lote = session.query(Lote).get(lote_id)
    
    # Obtener sedes receptoras activas
    sedes_receptoras = session.query(DireccionesSedes).filter(
        DireccionesSedes.estado == 'activa'
    ).all()
    
    engine = FEFOScoringEngine()
    candidatos = []
    
    for sede in sedes_receptoras:
        # Calcular métrica
        distancia = calcular_distancia_postgis(
            lote.coordenadas,
            sede.coordenadas
        )
        
        dias_vencer = (lote.fecha_limite_vencimiento - datetime.now()).days
        
        candidatos.append({
            "id_sede": str(sede.id_sede),
            "dias_para_vencer": dias_vencer,
            "distancia_km": float(distancia),
            "cantidad_kg": lote.cantidad_total_kg,
            "capacidad_disponible_kg": calcular_capacidad_disponible(sede),
            "es_perecedero": lote.es_perecedero,
            "tiene_cadena_frio_requerida": lote.requiere_cadena_frio
        })
    
    # Rankear
    ranking = engine.rankear_emparejamientos(candidatos)
    
    # Guardar en BD
    for idx, opcion in enumerate(ranking):
        emparejamiento = Emparejamiento(
            id_lote=lote_id,
            id_sede=opcion["id_sede"],
            distancia_km=opcion["distancia_km"],
            prioridad_fefo_score=Decimal(str(opcion["score_final"])),
            justificacion_ia=opcion["justificacion"],
            estado_tramite="sugerido"
        )
        session.add(emparejamiento)
    
    session.commit()
    return ranking
"""

if __name__ == "__main__":
    # Prueba rápida
    print("🎯 PRUEBA DE FEFO SCORING ENGINE")
    print("=" * 60)
    
    engine = FEFOScoringEngine()
    
    # Escenario 1: Excelente emparejamiento
    print("\n📊 ESCENARIO 1: Emparejamiento EXCELENTE")
    print("-" * 60)
    scores1 = engine.calcular_score_final(
        dias_para_vencer=5,
        distancia_km=10.0,
        cantidad_kg=Decimal("500"),
        capacidad_disponible_kg=Decimal("1000"),
        es_perecedero=True,
        tiene_cadena_frio_requerida=True
    )
    print(f"Vencimiento: {scores1['score_vencimiento']}/100")
    print(f"Distancia:   {scores1['score_distancia']}/100")
    print(f"Capacidad:   {scores1['score_capacidad']}/100")
    print(f"SCORE FINAL: {scores1['score_final']}/100 ✓")
    
    # Escenario 2: Emparejamiento pobre
    print("\n📊 ESCENARIO 2: Emparejamiento POBRE")
    print("-" * 60)
    scores2 = engine.calcular_score_final(
        dias_para_vencer=35,  # Vence en más de 30 días
        distancia_km=70.0,    # Muy lejano
        cantidad_kg=Decimal("500"),
        capacidad_disponible_kg=Decimal("100"),  # Poca capacidad
        es_perecedero=False,
        tiene_cadena_frio_requerida=False
    )
    print(f"Vencimiento: {scores2['score_vencimiento']}/100")
    print(f"Distancia:   {scores2['score_distancia']}/100")
    print(f"Capacidad:   {scores2['score_capacidad']}/100")
    print(f"SCORE FINAL: {scores2['score_final']}/100 ✗")
    
    # Justificación
    print("\n💬 JUSTIFICACIÓN IA")
    print("-" * 60)
    justificacion = engine.generar_justificacion_ia(
        scores1,
        metadata={
            "dias_vencimiento": 5,
            "distancia": 10.0,
            "es_perecedero": True
        }
    )
    print(justificacion)
