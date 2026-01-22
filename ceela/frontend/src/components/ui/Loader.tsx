
interface LoaderProps {
  isLoading?: boolean;
}

export const Loader = ({ isLoading = true }: LoaderProps) => {
  return (
    <div className={`loader-wrapper ${isLoading ? 'active' : ''}`}>
      <div className="theme-loader">    
        <div className="loader-p"></div>
      </div>
    </div>
  );
};
