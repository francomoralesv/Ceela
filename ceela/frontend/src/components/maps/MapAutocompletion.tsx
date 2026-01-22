import axios from "axios";
import dynamic from "next/dynamic";
import { useEffect, useState } from "react";
import { Autocompletion } from "./Autocompletion";
import { constantUrlApiEndpoint } from "@/utils/constant-url-endpoint";

interface MapAutocompletionProps {
  formData: {
    latitude: number;
    longitude: number;
    address: string;
    zone?: string;
    region?: string;
    country?: string;
  };
  handleFormInputChange: (field: any, value: any) => void;
  onCountryDetected: (country: string) => void;
}
const NoSSRInteractiveMap2 = dynamic(
  () => import("@/components/InteractiveMap2"),
  {
    ssr: false,
  }
);

export const MapAutocompletion: React.FC<MapAutocompletionProps> = ({
  formData,
  handleFormInputChange,
  onCountryDetected,
}) => {
  const [locationSearch, setLocationSearch] = useState("");
  const [completionList, setCompletionList] = useState<
    {
      Title: string;
      Position: [number, number];
    }[]
  >([]);

  useEffect(() => {
    if (!locationSearch.trim()) return;

    const delaySearch = setTimeout(() => {
      console.log("Buscando ubicación:", locationSearch);
      axios
        .get(
          `/api/map?q=${locationSearch}&lat=${formData.latitude}&long=${formData.longitude}`
        )
        .then((response) => {
          const { data } = response;
          console.log("Respuesta de ubicación", data.results.ResultItems);
          setCompletionList(data.results.ResultItems);
        })
        .catch((error) => {
          console.error("Error al buscar la ubicación:", error);
        });
    }, 500);

    return () => clearTimeout(delaySearch);
  }, [locationSearch, formData.latitude, formData.longitude]);

  // Nuevo efecto: geocodificación inversa para actualizar la dirección automáticamente
  useEffect(() => {
    if (formData.latitude && formData.longitude) {
      axios
        .get(`/api/geocode-reverse`, {
          params: {
            lat: formData.latitude,
            lon: formData.longitude,
          },
        })
        .then((response) => {
          const { display_name, address } = response.data;
          // Extraer la región del objeto address
          const region = address?.state || address?.region || "No disponible";
          // Extraer el país del objeto address
          const country = address?.country || "No disponible";
          console.log("Region detected:", region);
          console.log("Country detected:", country);

          // Actualizar el estado del formulario con la región
          handleFormInputChange("region", region);
          handleFormInputChange("department", region);
          
          // Notificar al componente padre sobre el país detectado
          onCountryDetected(country);
          
          if (display_name && display_name !== formData.address) {
            handleFormInputChange("address", display_name);
            const detailsTextArea = document.getElementById(
              "locationDetails"
            ) as HTMLTextAreaElement;
            if (detailsTextArea) {
              detailsTextArea.value = `Dirección: ${display_name}\nRegión: ${region}\nPaís: ${country}`;
            }
          }
        })
        .catch((error) => {
          console.error("Error en la geocodificación inversa:", error);
        });
    }
  }, [formData.latitude, formData.longitude]);

  return (
    <div>
      <div className="row">
        <div className="col-12 mb-3">
          <Autocompletion
            locationSearch={locationSearch}
            setLocationSearch={setLocationSearch}
            completionList={completionList}
            handleFormInputChange={handleFormInputChange}
            setCompletionList={setCompletionList}
          />
        </div>
        <div className="col-12 col-md-8 mb-3">
          <NoSSRInteractiveMap2
            initialLat={formData.latitude}
            initialLng={formData.longitude}
            handleFormInputChange={handleFormInputChange}
            onLocationSelect={(latlng) => {
              handleFormInputChange("latitude", latlng.lat);
              handleFormInputChange("longitude", latlng.lng);
            }}
          ></NoSSRInteractiveMap2>
        </div>
        <div className="col-12 col-md-4">
          <label
            className="form-label"
            style={{
              width: "100%",
              marginBottom: "8px",
            }}
          >
            Datos de ubicaciones encontradas
          </label>
          <textarea
            className="form-control mb-3"
            rows={2}
            value={`Latitud: ${formData.latitude}, Longitud: ${formData.longitude}`}
            readOnly
            style={{
              width: "100%",
              resize: "none",
            }}
          />
          <label className="form-label">Detalles de la ubicación</label>
          <textarea
            id="locationDetails"
            className="form-control"
            rows={6}
            readOnly
            value={`Dirección: ${formData.address}\nRegión: ${formData.region || 'No disponible'}\nPaís: ${formData.country || 'No disponible'}`}
            style={{
              width: "100%",
              resize: "none",
            }}
          />
          {/* Se coloca el componente ZoneSelector justo debajo del recuadro de "Detalles de la ubicación" */}
          <div className="mt-3">
            <ZoneSelector
              initialZone={formData.zone || ""}
              latitude={formData.latitude}
              longitude={formData.longitude}
              handleFormInputChange={handleFormInputChange}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default MapAutocompletion;

interface Zone {
  id: number | string;
  zone: string;
}

interface ZoneSelectorProps {
  latitude: number;
  longitude: number;
  handleFormInputChange: (field: any, value: any) => void;
  initialZone?: string;
}

const ZoneSelector: React.FC<ZoneSelectorProps> = ({
  latitude,
  longitude,
  handleFormInputChange,
  initialZone = "",
}) => {
  const [zones, setZones] = useState<Zone[]>([]);
  const [selectedZone, setSelectedZone] = useState<string>(initialZone);

  useEffect(() => {
    setSelectedZone(initialZone);
  }, [initialZone]);

  useEffect(() => {
    if (latitude && longitude) {
      axios
        .get(
          `${constantUrlApiEndpoint}/zones?latitude=${latitude}&longitude=${longitude}`
        )
        .then((response) => {
          setZones(response.data);
        })
        .catch((error) => {
          console.error("Error al obtener las zonas:", error);
        });
    }
  }, [latitude, longitude]);

  return (
    <div>
      <label className="form-label">Zona climática</label>
      <select
        className="form-control"
        value={selectedZone}
        onChange={(e) => {
          const value = e.target.value;
          setSelectedZone(value);
          handleFormInputChange("zone", value);
        }}
      >
        {zones.length > 0 ? (
          <>
            <option value="">Seleccione una zona</option>
            {zones.map((zone) => (
              <option key={zone.id} value={zone.zone}>
                {zone.zone}
              </option>
            ))}
          </>
        ) : (
          <option value="">No hay datos para zona específica</option>
        )}
      </select>
    </div>
  );
};
