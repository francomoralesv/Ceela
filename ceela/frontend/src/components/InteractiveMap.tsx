import axios from "axios";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import React, { useEffect, useRef } from "react";

interface LocationDetails {
  AddressNumber?: string;
  Categories?: string[];
  Country?: string;
  Label?: string;
  Municipality?: string;
  PostalCode?: string;
  Region?: string;
  SubRegion?: string;
}

interface InteractiveMapProps {
  onLocationSelect: (latlng: { lat: number; lng: number }) => void;
  onLocationDetails?: (details: LocationDetails) => void;
  initialLat?: number;
  initialLng?: number;
}

const InteractiveMap: React.FC<InteractiveMapProps> = ({
  onLocationSelect,
  initialLat,
  initialLng,
  onLocationDetails,
}) => {
  L.Icon.Default.imagePath = "https://unpkg.com/leaflet@1.7.1/dist/images/";
  const mapRef = useRef<L.Map | null>(null);
  const markerRef = useRef<L.Marker | null>(null);
  const zoomRef = useRef<number>(13);

  useEffect(() => {
    if (!mapRef.current) {
      mapRef.current = L.map("map", {
        zoomControl: true,
        attributionControl: true,
      }).setView(
        initialLat && initialLng ? [initialLat, initialLng] : [0, 0],
        zoomRef.current
      );

      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "© OpenStreetMap contributors",
      }).addTo(mapRef.current);

      mapRef.current.on("zoomend", () => {
        if (mapRef.current) {
          zoomRef.current = mapRef.current.getZoom();
        }
      });

      const handleMapClick = async (e: L.LeafletMouseEvent) => {
        const { lat, lng } = e.latlng;
        onLocationSelect({ lat, lng });

        try {
          const response = await axios.get(
            `/api/map_locator?lat=${lat}&long=${lng}`
          );
          if (onLocationDetails) {
            onLocationDetails(response.data?.results);
          }
        } catch (error) {
          console.error("Error al obtener la ubicación:", error);
        }

        if (markerRef.current) {
          markerRef.current.setLatLng([lat, lng]);
        } else {
          markerRef.current = L.marker([lat, lng]).addTo(mapRef.current!);
        }
      };

      mapRef.current.on("click", handleMapClick);
    }

    if (mapRef.current && initialLat && initialLng) {
      if (markerRef.current) {
        markerRef.current.setLatLng([initialLat, initialLng]);
      } else {
        markerRef.current = L.marker([initialLat, initialLng]).addTo(
          mapRef.current
        );
      }
      mapRef.current.setView([initialLat, initialLng], zoomRef.current);
    }

    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
      if (markerRef.current) {
        markerRef.current = null;
      }
    };
  }, [initialLat, initialLng, onLocationSelect, onLocationDetails]);

  return (
    <div
      id="map"
      style={{
        height: "400px",
        width: "100%",
        position: "relative",
        overflow: "hidden",
      }}
    ></div>
  );
};

export default InteractiveMap;
