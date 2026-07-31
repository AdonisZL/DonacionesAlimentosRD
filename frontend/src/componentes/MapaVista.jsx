/**
 * MapaVista — Mapa de solo lectura para ver una ubicación.
 * MapaVista — 只读地图组件，用于查看位置。
 *
 * Props:
 *   lat, lng — coordenadas a mostrar / 要显示的坐标
 *   direccion — texto de la dirección (opcional) / 地址文本（可选）
 *   altura — altura del mapa (default: "h-48") / 地图高度
 */

import { useEffect, useRef, useState } from "react";

export default function MapaVista({
  lat,
  lng,
  direccion = "",
  altura = "h-48",
}) {
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState(null);
  const refMapa = useRef(null);
  const mapaRef = useRef(null);

  const tieneCoordenadas =
    lat != null && lng != null && !isNaN(lat) && !isNaN(lng);

  useEffect(() => {
    if (!tieneCoordenadas) {
      setCargando(false);
      return;
    }

    let cancelado = false;

    function inicializarMapa() {
      if (cancelado) return;

      try {
        const centro = { lat: parseFloat(lat), lng: parseFloat(lng) };

        const mapa = new window.google.maps.Map(refMapa.current, {
        center: centro,
        zoom: 16,
        mapTypeControl: false,
        streetViewControl: false,
        fullscreenControl: false,
        zoomControl: true,
        styles: [
          {
            featureType: "poi.business",
            stylers: [{ visibility: "off" }],
          },
          {
            featureType: "transit",
            stylers: [{ visibility: "off" }],
          },
        ],
      });

      // Marcador en la ubicación / 在位置上放置标记
      new window.google.maps.Marker({
        position: centro,
        map: mapa,
        animation: window.google.maps.Animation.DROP,
        icon: {
          path: window.google.maps.SymbolPath.CIRCLE,
          scale: 10,
          fillColor: "#006e2f",
          fillOpacity: 1,
          strokeColor: "#ffffff",
          strokeWeight: 3,
        },
      });

      mapaRef.current = mapa;
      setCargando(false);
      } catch (err) {
        console.error("Error en inicializarMapa (MapaVista):", err);
        if (!cancelado) {
          setError("No se pudo cargar el mapa. Verifica tu API Key.");
          setCargando(false);
        }
      }
    }

    // Esperar a Google Maps / 等待 Google Maps 加载
    let intentos = 0;
    const MAX_INTENTOS = 50; // ~5 segundos
    const intervalo = setInterval(() => {
      if (
        window.google &&
        window.google.maps &&
        typeof window.google.maps.Map === "function"
      ) {
        clearInterval(intervalo);
        try {
          inicializarMapa();
        } catch (err) {
          console.error("Error al inicializar MapaVista:", err);
          if (!cancelado) {
            setError("No se pudo cargar el mapa.");
            setCargando(false);
          }
        }
        return;
      }
      intentos++;
      if (intentos >= MAX_INTENTOS) {
        clearInterval(intervalo);
        if (!cancelado) {
          setError("No se pudo cargar el mapa.");
          setCargando(false);
        }
      }
    }, 100);

    return () => {
      cancelado = true;
      clearInterval(intervalo);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lat, lng]);

  if (!tieneCoordenadas) {
    return (
      <div className="flex flex-col items-center justify-center gap-sm py-lg px-md bg-surface-container-low rounded-xl border border-outline-variant/20 text-on-surface-variant">
        <span className="material-symbols-outlined text-3xl">location_off</span>
        <p className="font-body-md text-sm text-center">
          No hay ubicación registrada.
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-sm">
      {direccion && (
        <p className="font-body-md text-body-md text-on-surface flex items-center gap-xs">
          <span className="material-symbols-outlined text-on-surface-variant text-sm">
            location_on
          </span>
          {direccion}
        </p>
      )}
      {error && (
        <div className="text-error text-sm flex items-center gap-xs">
          <span className="material-symbols-outlined text-sm">error</span>
          {error}
        </div>
      )}
      {cargando && (
        <div className="flex items-center gap-sm text-on-surface-variant py-lg">
          <span className="material-symbols-outlined animate-spin text-sm">progress_activity</span>
          <span className="font-body-md text-sm">Cargando mapa…</span>
        </div>
      )}
      <div
        ref={refMapa}
        className={`w-full ${altura} rounded-xl border border-outline-variant/30 overflow-hidden ${
          cargando ? "bg-surface-container-low" : ""
        }`}
      />
    </div>
  );
}
