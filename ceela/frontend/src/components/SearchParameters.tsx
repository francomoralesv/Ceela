import React from 'react';

interface SearchParametersProps {
    onSearch: (searchTerm: string) => void;
}

const SearchParameters: React.FC<SearchParametersProps> = ({ onSearch }) => {
    return (
        <div className="mb-3">
            <div className="row">
                <div className="col-md-12">
                    <input
                        type="text"
                        className="form-control"
                        placeholder="Buscar por país, ciudad, distrito o zona..."
                        onChange={(e) => onSearch(e.target.value)}
                        style={{ height: "40px" }}
                    />
                </div>
            </div>
        </div>
    );
};

export default SearchParameters;
