/**
 * MapaEmparejamiento — Visualiza el lote de origen, el radio de búsqueda
 * (RN-10, PostGIS ST_DWithin) y los receptores candidatos (RF-17).
 * MapaEmparejamiento — 显示批次原点、搜索半径（RN-10）与候选接收方（RF-17）。
 *
 * Props:
 *   origen — { lat, lng } del lote de origen / 批次原点坐标
 *   radioKm — radio de búsqueda en km, dibuja un círculo / 搜索半径（km），绘制圆圈
 *   candidatos — [{ id_sede, nombre_sede, latitud, longitud, compatible, distancia_km }]
 *   seleccionado — id_sede resaltado actualmente / 当前高亮的 id_sede
 *   onSeleccionar(idSede) — callback al hacer clic en un marcador / 点击标记的回调
 *   altura — clase Tailwind de altura (default "h-80") / 高度类
 */

import { useEffect, useRef, useState } from "react";

export default function MapaEmparejamiento({
  origen,
  radioKm = 10,
  candidatos = [],
  seleccionado = null,
  onSeleccionar,
  altura = "h-80",
}) {
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState(null);
  const refMapa = useRef(null);
  const mapaRef = useRef(null);
  const marcadoresRef = useRef([]);
  const circuloRef = useRef(null);
  const infoRef = useRef(null);

  const tieneOrigen =
    origen && origen.lat != null && origen.lng != null && !isNaN(origen.lat);

  useEffect(() => {
    if (!tieneOrigen) {
      setCargando(false);
      return;
    }
    let cancelado = false;

    function crearIcono(color, escala = 10) {
      return {
        path: window.google.maps.SymbolPath.CIRCLE,
        scale: escala,
        fillColor: color,
        fillOpacity: 1,
        strokeColor: "#ffffff",
        strokeWeight: 2,
      };
    }

    function dibujar() {
      if (cancelado || !refMapa.current) return;
      try {
        const centro = { lat: parseFloat(origen.lat), lng: parseFloat(origen.lng) };

        const mapa =
          mapaRef.current ||
          new window.google.maps.Map(refMapa.current, {
            center: centro,
            zoom: 12,
            mapTypeControl: false,
            streetViewControl: false,
            fullscreenControl: false,
            zoomControl: true,
          });
        mapaRef.current = mapa;

        // Limpiar marcadores y círculo previos / 清除旧标记与圆圈
        marcadoresRef.current.forEach((m) => m.setMap(null));
        marcadoresRef.current = [];
        if (circuloRef.current) circuloRef.current.setMap(null);
        if (infoRef.current) infoRef.current.close();

        // Marcador del origen (lote) / 批次原点标记
        const marcadorOrigen = new window.google.maps.Marker({
          position: centro,
          map: mapa,
          title: "Origen del lote",
          icon: crearIcono("#006e2f", 11),
          zIndex: 999,
        });
        marcadoresRef.current.push(marcadorOrigen);

        // Círculo del radio de búsqueda (RN-10) / 搜索半径圆圈
        circuloRef.current = new window.google.maps.Circle({
          map: mapa,
          center: centro,
          radius: radioKm * 1000,
          fillColor: "#006e2f",
          fillOpacity: 0.08,
          strokeColor: "#006e2f",
          strokeOpacity: 0.4,
          strokeWeight: 1.5,
        });

        const bounds = new window.google.maps.LatLngBounds();
        bounds.extend(centro);
        bounds.extend(circuloRef.current.getBounds().getNorthEast());
        bounds.extend(circuloRef.current.getBounds().getSouthWest());

        const info = infoRef.current || new window.google.maps.InfoWindow();
        infoRef.current = info;

        // Marcadores de candidatos / 候选接收方标记
        candidatos
          .filter((c) => c.latitud != null && c.longitud != null)
          .forEach((c) => {
            const posicion = { lat: c.latitud, lng: c.longitud };
            const esSeleccionado = c.id_sede === seleccionado;
            const color = !c.compatible ? "#ba1a1a" : esSeleccionado ? "#855300" : "#4059aa";
            const marcador = new window.google.maps.Marker({
              position: posicion,
              map: mapa,
              title: c.nombre_sede || "Receptor",
              icon: crearIcono(color, esSeleccionado ? 11 : 9),
            });
            marcador.addListener("click", () => {
              info.setContent(
                `<div style="font-family:Inter,sans-serif;padding:2px 4px;">
                  <strong>${c.nombre_sede || "Sede receptora"}</strong><br/>
                  ${c.distancia_km} km ${c.compatible ? "" : "· No compatible"}
                </div>`,
              );
              info.open(mapa, marcador);
              if (onSeleccionar) onSeleccionar(c.id_sede);
            });
            marcadoresRef.current.push(marcador);
            bounds.extend(posicion);
          });

        mapa.fitBounds(bounds);
        setCargando(false);
      } catch (err) {
        console.error("Error en MapaEmparejamiento:", err);
        if (!cancelado) {
          setError("No se pudo cargar el mapa. Verifica tu API Key.");
          setCargando(false);
        }
      }
    }

    function mapsListo() {
      return window.google && window.google.maps && typeof window.google.maps.Map === "function";
    }

    if (mapsListo()) {
      dibujar();
      return () => {
        cancelado = true;
      };
    }

    if (window.__googleMapsError) {
      setError("No se pudo cargar Google Maps (verifica la conexión o la API Key).");
      setCargando(false);
      return () => {
        cancelado = true;
      };
    }

    const intervalo = setInterval(() => {
      if (mapsListo()) {
        clearInterval(intervalo);
        dibujar();
      } else if (window.__googleMapsError) {
        clearInterval(intervalo);
        if (!cancelado) {
          setError("No se pudo cargar Google Maps (verifica la conexión o la API Key).");
          setCargando(false);
        }
      }
    }, 150);

    return () => {
      cancelado = true;
      clearInterval(intervalo);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [origen?.lat, origen?.lng, radioKm, candidatos, seleccionado]);

  if (!tieneOrigen) {
    return (
      <div className="flex flex-col items-center justify-center gap-sm py-lg px-md bg-surface-container-low rounded-xl border border-outline-variant/20 text-on-surface-variant">
        <span className="material-symbols-outlined text-3xl">location_off</span>
        <span className="font-body-md text-sm text-center">
          El lote no tiene una sede con coordenadas registradas.
        </span>
      </div>
    );
  }

  return (
    <div className={`relative w-full ${altura} rounded-xl overflow-hidden border border-outline-variant/30`}>
      {cargando && (
        <div className="absolute inset-0 flex items-center justify-center bg-surface-container-low z-10">
          <span className="font-body-md text-sm text-on-surface-variant">Cargando mapa…</span>
        </div>
      )}
      {error && (
        <div className="absolute inset-0 flex flex-col items-center justify-center gap-xs bg-surface-container-low z-10 px-md text-center">
          <span className="material-symbols-outlined text-2xl text-error">error</span>
          <span className="font-body-md text-sm text-on-surface-variant">{error}</span>
        </div>
      )}
      <div ref={refMapa} className="w-full h-full" />
    </div>
  );
}
