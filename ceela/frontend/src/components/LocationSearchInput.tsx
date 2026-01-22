import axios from "axios";
import React, { useEffect, useState } from "react";

interface LocationSearchInputProps {
    onSelectLocation: (location: any) => void;
}

export const LocationSearchInput: React.FC<LocationSearchInputProps> = ({ onSelectLocation }) => {
    const [searchQuery, setSearchQuery] = useState("");
    const [suggestions, setSuggestions] = useState<any[]>([]);
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        if (!searchQuery.trim()) {
            setSuggestions([]);
            return;
        }

        const fetchSuggestions = async () => {
            setIsLoading(true);
            try {
                const response = await axios.get(`/api/map?q=${searchQuery}`);
                setSuggestions(response.data.results.ResultItems || []);
            } catch (error) {
                console.error("Error fetching location suggestions:", error);
            } finally {
                setIsLoading(false);
            }
        };

        const delayDebounce = setTimeout(fetchSuggestions, 500);
        return () => clearTimeout(delayDebounce);
    }, [searchQuery]);

    return (
        <div style={{ position: "relative" }}>
            <input
                type="text"
                className="form-control"
                placeholder="Buscar ubicación..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
            />
            {isLoading && <div style={{ position: "absolute", top: "100%", left: 0, background: "white", padding: "10px", boxShadow: "0px 4px 6px rgba(0, 0, 0, 0.1)" }}>Cargando...</div>}
            {suggestions.length > 0 && (
                <ul
                    className="list-group"
                    style={{
                        position: "absolute",
                        top: "100%",
                        left: 0,
                        width: "100%",
                        background: "white",
                        boxShadow: "0px 4px 6px rgba(0, 0, 0, 0.1)",
                        zIndex: 1000,
                        marginTop: "5px",
                        borderRadius: "4px",
                        overflow: "hidden",
                    }}
                >
                    {suggestions.map((suggestion, index) => (
                        <li
                            key={index}
                            className="list-group-item"
                            onClick={() => {
                                onSelectLocation(suggestion);
                                setSearchQuery(suggestion.Title);
                                setSuggestions([]);
                            }}
                            style={{
                                cursor: "pointer",
                                padding: "10px",
                                borderBottom: index !== suggestions.length - 1 ? "1px solid #ddd" : "none",
                            }}
                        >
                            {suggestion.Title}
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};
