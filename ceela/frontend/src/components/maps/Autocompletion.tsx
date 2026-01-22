import { FC, useRef, useEffect } from 'react';

interface AutocompletionProps {
  locationSearch: string;
  setLocationSearch: (value: string) => void;
  completionList: Array<{
    Title: string;
    Position: [number, number];
  }>;
  setCompletionList: (list: Array<any>) => void;
  handleFormInputChange: (field: any, value: string | number) => void;
}

export const Autocompletion: FC<AutocompletionProps> = ({
  locationSearch,
  setLocationSearch,
  completionList,
  setCompletionList,
  handleFormInputChange
}) => {
  const containerRef = useRef<HTMLDivElement>(null);

  // Cierra la lista al hacer clic fuera del componente
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setCompletionList([]);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [setCompletionList]);

  // Cierra la lista si el campo de búsqueda está vacío
  useEffect(() => {
    if (!locationSearch.trim()) {
      setCompletionList([]);
    }
  }, [locationSearch, setCompletionList]);

  return (
    <div style={{ position: "relative" }} ref={containerRef}>
      <input
        type="text"
        className="form-control"
        value={locationSearch}
        onChange={(e) => {
          const value = e.target.value;
          setLocationSearch(value);
          if (!value.trim()) {
            setCompletionList([]);
          }
        }}
        onKeyDown={(e) => {
          if (e.key === 'Enter') {
            e.preventDefault();
          }
        }}
        style={{ paddingLeft: "40px" }}
      />
      <span
        className="material-icons"
        style={{
          position: "absolute",
          left: "10px",
          top: "50%",
          transform: "translateY(-50%)",
          color: "#ccc",
        }}
      >
        search
      </span>
      {completionList.length > 0 && locationSearch.trim() !== "" && (
        <div
          style={{
            position: 'absolute',
            top: '100%',
            left: 0,
            right: 0,
            backgroundColor: 'white',
            border: '1px solid #ccc',
            borderRadius: '4px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            zIndex: 1100,
            maxHeight: '200px',
            overflowY: 'auto'
          }}
        >
          {completionList.map((item, index) => (
            <div
              key={index}
              style={{
                padding: '8px 12px',
                cursor: 'pointer',
                borderBottom: '1px solid #eee',
              }}
              onClick={() => {
                // Al seleccionar se actualizan latitud y longitud, se setea el valor en el input y se cierra la lista
                handleFormInputChange("latitude", item.Position[1]);
                handleFormInputChange("longitude", item.Position[0]);
                setLocationSearch(item.Title);
                setCompletionList([]);
              }}
            >
              {item.Title}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
