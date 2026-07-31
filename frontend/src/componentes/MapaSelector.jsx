/**
 * MapaSelector - Componente de Google Maps con busqueda de direcciones y dibujo de rectangulos.
 * MapaSelector - Google Maps 组件，含地址搜索与矩形绘制功能。
 *
 * Props:
 *   latInicial, lngInicial - coordenadas iniciales
 *   direccionInicial - texto de direccion inicial
 *   alCambiarCoordenadas(lat, lng) - callback al actualizar coordenadas
 *   alCambiarDireccion(texto) - callback al actualizar direccion
 *   soloLectura - si true, oculta busqueda y dibujo
 */

import { useEffect, useRef, useState } from "react";

export default function MapaSelector({
  latInicial = 18.4861,
  lngInicial = -69.9312,
  direccionInicial = "",
  alCambiarCoordenadas,
  alCambiarDireccion,
  soloLectura = false,
}) {
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState(null);
  const [modoDibujo, setModoDibujo] = useState(false);
  const [latActual, setLatActual] = useState(String(latInicial));
  const [lngActual, setLngActual] = useState(String(lngInicial));

  const refMapa = useRef(null);        // div del mapa
  const refInput = useRef(null);       // input de busqueda
  const mapaInst = useRef(null);       // instancia google.maps.Map
  const marcadorInst = useRef(null);    // instancia google.maps.Marker
  const autocompleteInst = useRef(null);// instancia Places Autocomplete
  const dibujoCtrl = useRef(null);     // control de dibujo manual
  const rectActual = useRef(null);     // rectangulo actual
  const inicioRect = useRef(null);     // punto de inicio del rect
  const rectPreview = useRef(null);    // vista previa del rect
  const dibujando = useRef(false);     // estado de dibujo
  const inicializado = useRef(false);  // flag de inicializacion

  // Helper: actualiza coordenadas locales y notifica al padre
  function actualizarCoords(lat, lng) {
    setLatActual(String(lat));
    setLngActual(String(lng));
    if (alCambiarCoordenadas) alCambiarCoordenadas(lat, lng);
  }

  // Inicializar Google Maps
  useEffect(() => {
    if (inicializado.current) return;
    let cancelado = false;

    function crearMapa() {
      if (cancelado || !refMapa.current) return;

      try {
        const centro = { lat: latInicial, lng: lngInicial };

        // Crear mapa
        const mapa = new window.google.maps.Map(refMapa.current, {
          center: centro,
          zoom: 15,
          mapTypeControl: false,
          streetViewControl: false,
          fullscreenControl: false,
          zoomControl: true,
          styles: [
            { featureType: "poi.business", stylers: [{ visibility: "off" }] },
            { featureType: "transit", stylers: [{ visibility: "off" }] },
          ],
        });

        // Crear marcador
        const marcador = new window.google.maps.Marker({
          position: centro,
          map: mapa,
          draggable: !soloLectura,
          animation: window.google.maps.Animation.DROP,
          icon: {
            path: window.google.maps.SymbolPath.CIRCLE,
            scale: 12,
            fillColor: "#006e2f",
            fillOpacity: 1,
            strokeColor: "#ffffff",
            strokeWeight: 3,
          },
        });

        // Marcador arrastrable
        if (!soloLectura) {
          marcador.addListener("dragend", () => {
            const pos = marcador.getPosition();
            if (pos) {
              actualizarCoords(
                parseFloat(pos.lat().toFixed(6)),
                parseFloat(pos.lng().toFixed(6))
              );
            }
          });
        }

        // Places Autocomplete (busca calles Y negocios/establecimientos)
        if (!soloLectura && refInput.current) {
          try {
            if (
              window.google.maps.places &&
              typeof window.google.maps.places.Autocomplete === "function"
            ) {
              const autocomplete = new window.google.maps.places.Autocomplete(
                refInput.current,
                { types: ["geocode"] }  // "geocode" busca direcciones + lugares
              );

              autocomplete.addListener("place_changed", () => {
                const place = autocomplete.getPlace();
                if (place && place.geometry) {
                  const loc = place.geometry.location;
                  const lat = parseFloat(loc.lat().toFixed(6));
                  const lng = parseFloat(loc.lng().toFixed(6));
                  mapa.setCenter(loc);
                  mapa.setZoom(17);
                  marcador.setPosition(loc);
                  actualizarCoords(lat, lng);
                  const texto = place.formatted_address || refInput.current.value || "";
                  if (alCambiarDireccion) alCambiarDireccion(texto);
                }
              });

              autocompleteInst.current = autocomplete;
            } else {
              console.warn("Places Autocomplete no disponible para esta API Key.");
            }
          } catch (err) {
            console.warn("Places Autocomplete error:", err);
          }
        }

        // Dibujo manual de rectangulo (Drawing Library obsoleto en v3.65)
        if (!soloLectura) {
          // Click en mapa: coloca marcador
          mapa.addListener("click", (e) => {
            if (dibujando.current) return;
            if (!e.latLng) return;
            actualizarCoords(
              parseFloat(e.latLng.lat().toFixed(6)),
              parseFloat(e.latLng.lng().toFixed(6))
            );
            marcador.setPosition(e.latLng);
          });

          // Mouse down: inicia dibujo de rectangulo
          mapa.addListener("mousedown", (e) => {
            if (!dibujando.current) return;
            inicioRect.current = e.latLng;
            const bounds = new window.google.maps.LatLngBounds(e.latLng, e.latLng);
            const prev = new window.google.maps.Rectangle({
              map: mapa,
              bounds: bounds,
              fillColor: "#006e2f",
              fillOpacity: 0.15,
              strokeColor: "#006e2f",
              strokeWeight: 2,
              clickable: false,
            });
            rectPreview.current = prev;
            mapa.setOptions({ draggableCursor: "crosshair" });
          });

          // Mouse move: actualiza preview
          mapa.addListener("mousemove", (e) => {
            if (!dibujando.current || !inicioRect.current || !rectPreview.current) return;
            const bounds = new window.google.maps.LatLngBounds(inicioRect.current, e.latLng);
            rectPreview.current.setBounds(bounds);
          });

          // Mouse up: finaliza dibujo
          const onMouseUp = (e) => {
            if (!dibujando.current || !inicioRect.current) return;
            dibujando.current = false;
            mapa.setOptions({ draggableCursor: "" });

            if (rectPreview.current) {
              // Limpiar rectangulo anterior
              if (rectActual.current) rectActual.current.setMap(null);
              rectActual.current = rectPreview.current;

              // Hacer editable
              rectPreview.current.setOptions({
                editable: true, draggable: true, clickable: true, strokeWeight: 2,
              });

              // Calcular centro
              const centroRect = rectPreview.current.getBounds().getCenter();
              const lat = parseFloat(centroRect.lat().toFixed(6));
              const lng = parseFloat(centroRect.lng().toFixed(6));
              marcador.setPosition(centroRect);
              mapa.panTo(centroRect);
              actualizarCoords(lat, lng);

              // Actualizar centro al redimensionar
              window.google.maps.event.addListener(rectPreview.current, "bounds_changed", () => {
                const nb = rectPreview.current.getBounds();
                if (!nb) return;
                const nc = nb.getCenter();
                actualizarCoords(
                  parseFloat(nc.lat().toFixed(6)),
                  parseFloat(nc.lng().toFixed(6))
                );
                marcador.setPosition(nc);
              });

              setModoDibujo(false);
            }
            inicioRect.current = null;
            rectPreview.current = null;
          };

          mapa.addListener("mouseup", onMouseUp);

          // Control de dibujo
          dibujoCtrl.current = {
            activar: () => {
              dibujando.current = true;
              mapa.setOptions({ draggableCursor: "crosshair" });
            },
            cancelar: () => {
              dibujando.current = false;
              inicioRect.current = null;
              if (rectPreview.current) {
                rectPreview.current.setMap(null);
                rectPreview.current = null;
              }
              mapa.setOptions({ draggableCursor: "" });
            },
          };
        }

        mapaInst.current = mapa;
        marcadorInst.current = marcador;
        inicializado.current = true;
        setCargando(false);
      } catch (err) {
        console.error("Error al inicializar Google Maps:", err);
        if (!cancelado) {
          setError("Error al cargar Google Maps. Verifica la API Key.");
          setCargando(false);
        }
      }
    }

    // Esperar a Google Maps
    function mapsListo() {
      return window.google && window.google.maps && typeof window.google.maps.Map === "function";
    }

    // Verificar si ya cargo
    if (mapsListo()) {
      crearMapa();
      return () => { cancelado = true; };
    }

    // Si hubo error de auth
    if (window.__googleMapsError) {
      setError("Error de Google Maps: " + (window.__googleMapsError === "auth_failure" ? "API Key invalida" : "Error de red"));
      setCargando(false);
      return;
    }

    // Polling
    let intentos = 0;
    const intervalo = setInterval(() => {
      intentos++;
      if (window.__googleMapsError) {
        clearInterval(intervalo);
        setError("Error de Google Maps: API Key invalida.");
        setCargando(false);
        return;
      }
      if (mapsListo()) {
        clearInterval(intervalo);
        crearMapa();
        return;
      }
      if (intentos >= 50) {
        clearInterval(intervalo);
        if (!cancelado) {
          setError("No se pudo cargar Google Maps. Verifica tu conexion.");
          setCargando(false);
        }
      }
    }, 100);

    return () => {
      cancelado = true;
      clearInterval(intervalo);
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Toggle dibujo
  function toggleDibujo() {
    if (!dibujoCtrl.current) return;
    if (modoDibujo) {
      dibujoCtrl.current.cancelar();
      setModoDibujo(false);
    } else {
      if (rectActual.current) {
        rectActual.current.setMap(null);
        rectActual.current = null;
      }
      dibujoCtrl.current.activar();
      setModoDibujo(true);
    }
  }

  return (
    <div className="flex flex-col gap-md">
      {/* Busqueda de direccion */}
      {!soloLectura && (
        <>
          <div className="relative">
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant z-10 pointer-events-none">
              search
            </span>
            <input
              ref={refInput}
              type="text"
              defaultValue={direccionInicial}
              placeholder="Buscar direccion o negocio..."
              onKeyDown={(e) => {
                // Fallback: Enter para geocodificar si Autocomplete no esta disponible
                if (e.key === "Enter" && !autocompleteInst.current && mapaInst.current) {
                  e.preventDefault();
                  const texto = e.target.value.trim();
                  if (!texto) return;
                  try {
                    const geocoder = new window.google.maps.Geocoder();
                    geocoder.geocode({ address: texto }, (resultados, estado) => {
                      if (estado === "OK" && resultados[0]) {
                        const loc = resultados[0].geometry.location;
                        const lat = parseFloat(loc.lat().toFixed(6));
                        const lng = parseFloat(loc.lng().toFixed(6));
                        mapaInst.current.setCenter(loc);
                        mapaInst.current.setZoom(17);
                        marcadorInst.current.setPosition(loc);
                        actualizarCoords(lat, lng);
                        if (alCambiarDireccion) alCambiarDireccion(texto);
                      }
                    });
                  } catch (errGeo) {
                    console.warn("Geocoding error:", errGeo);
                  }
                }
              }}
              className="w-full pl-10 pr-3 py-sm bg-surface border border-outline-variant rounded-lg font-body-md text-body-md text-on-surface focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-shadow"
            />
          </div>

          {/* Boton dibujar rectangulo */}
          <div className="flex gap-sm flex-wrap items-center">
            <button
              type="button"
              onClick={toggleDibujo}
              disabled={cargando || !!error}
              className={`py-sm px-md rounded-lg font-label-sm transition-all flex items-center gap-xs ${
                modoDibujo
                  ? "bg-primary text-on-primary shadow-md shadow-primary/20"
                  : "bg-surface-container-high text-on-surface-variant hover:bg-surface-container-highest border border-outline-variant/30"
              } disabled:opacity-40 disabled:cursor-not-allowed`}
            >
              <span className="material-symbols-outlined text-sm">crop_free</span>
              {modoDibujo ? "Dibujando... (clic para cancelar)" : "Dibujar area rectangular"}
            </button>
            {modoDibujo && (
              <span className="font-label-sm text-label-sm text-on-surface-variant animate-pulse">
                Arrastra sobre el mapa para definir el area de cobertura
              </span>
            )}
          </div>
        </>
      )}

      {/* Error */}
      {error && (
        <div className="flex items-start gap-sm rounded-lg bg-error-container px-sm py-sm text-on-error-container">
          <span className="material-symbols-outlined text-sm mt-px">error</span>
          <span className="font-body-md text-sm">{error}</span>
        </div>
      )}

      {/* Cargando */}
      {cargando && !error && (
        <div className="flex items-center gap-sm text-on-surface-variant py-lg">
          <span className="material-symbols-outlined animate-spin text-sm">progress_activity</span>
          <span className="font-body-md text-sm">Cargando mapa...</span>
        </div>
      )}

      {/* Mapa */}
      <div
        ref={refMapa}
        className={`w-full h-72 rounded-xl border border-outline-variant/30 overflow-hidden ${
          cargando && !error ? "bg-surface-container-low" : ""
        }`}
      />

      {/* Coordenadas actuales */}
      <div className="grid grid-cols-2 gap-sm">
        <div className="flex flex-col gap-xs">
          <label className="font-label-sm text-label-sm text-on-surface-variant flex items-center gap-xs">
            <span className="material-symbols-outlined text-sm">my_location</span>
            Latitud
          </label>
          <input
            type="text"
            value={latActual}
            readOnly
            tabIndex={-1}
            className="w-full px-sm py-xs bg-surface-container-low border border-outline-variant/30 rounded-lg font-mono text-sm text-on-surface cursor-default select-all"
          />
        </div>
        <div className="flex flex-col gap-xs">
          <label className="font-label-sm text-label-sm text-on-surface-variant flex items-center gap-xs">
            <span className="material-symbols-outlined text-sm">my_location</span>
            Longitud
          </label>
          <input
            type="text"
            value={lngActual}
            readOnly
            tabIndex={-1}
            className="w-full px-sm py-xs bg-surface-container-low border border-outline-variant/30 rounded-lg font-mono text-sm text-on-surface cursor-default select-all"
          />
        </div>
      </div>

      {/* Pista de uso */}
      {!soloLectura && !cargando && !error && (
        <p className="font-label-sm text-label-sm text-on-surface-variant flex items-center gap-xs">
          <span className="material-symbols-outlined text-sm">touch_app</span>
          Haz clic en el mapa para colocar el marcador, o dibuja un rectangulo para
          calcular el centro del area.
        </p>
      )}
    </div>
  );
}
