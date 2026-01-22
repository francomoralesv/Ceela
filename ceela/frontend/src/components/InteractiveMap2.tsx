import axios from "axios";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import React, { useEffect, useRef } from "react";

interface InteractiveMapProps {
  initialLat?: number;
  initialLng?: number;
  onLocationSelect?: (latlng: { lat: number; lng: number }) => void;
  handleFormInputChange?: (field: any, value: any) => void;
}

const InteractiveMap2: React.FC<InteractiveMapProps> = ({
  initialLat = -16.419167000391106,
  initialLng = -71.52432686007376,
  handleFormInputChange,
}) => {
  L.Icon.Default.imagePath = "https://unpkg.com/leaflet@1.7.1/dist/images/";
  const mapRef = useRef<L.Map | null>(null);
  const markerRef = useRef<L.Marker | null>(null);
  const zoomRef = useRef<number>(13);
  const coordinates: { lat: number; lng: number } = {
    lat: initialLat,
    lng: initialLng,
  };
  useEffect(() => {
    mapRef.current = L.map("map2").setView([initialLat, initialLng], 13);
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution:
        '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    }).addTo(mapRef.current!);
  }, []);

  useEffect(() => {
    console.log("coordinates:", initialLat, initialLng);
    const currentZoom = mapRef.current!.getZoom();
    if (mapRef.current) {
      // Use flyTo to smoothly move the map to the new coordinates
      mapRef.current.flyTo(
        [initialLat, initialLng],
        currentZoom < 13 ? 13 : currentZoom,
        {
          animate: true,
          duration: 1.5,
        }
      );

      // Update the marker position
      if (markerRef.current) {
        markerRef.current.setLatLng([initialLat, initialLng]);
      } else {
        markerRef.current = L.marker([initialLat, initialLng], {
          draggable: true,
          autoPan: true,
        }).addTo(mapRef.current!);

        // Add dragend event to update coordinates
        markerRef.current.on("dragend", () => {
          const { lat, lng } = markerRef.current!.getLatLng();
          coordinates.lat = lat;
          coordinates.lng = lng;
          mapRef.current!.flyTo(
            [lat, lng],
            currentZoom < 13 ? 13 : currentZoom,
            {
              animate: true,
              duration: 1.5,
            }
          );
          if (handleFormInputChange) {
            handleFormInputChange("latitude", lat);
            handleFormInputChange("longitude", lng);
          }
          console.log("Marker dragged to:", lat, lng);
        });
      }
      if (handleFormInputChange) {
        handleFormInputChange("latitude", initialLat);
        handleFormInputChange("longitude", initialLng);
      }
    }
  }, [initialLat, initialLng]);

  return (
    <div
      id="map2"
      style={{
        height: "400px",
        width: "100%",
        position: "relative",
        overflow: "hidden",
      }}
    ></div>
  );
};

export default InteractiveMap2;
