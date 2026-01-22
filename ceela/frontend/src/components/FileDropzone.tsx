import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';

interface FileDropzoneProps {
  onFileAccepted: (files: File[]) => void;
  accept?: string[];
}

const FileDropzone: React.FC<FileDropzoneProps> = ({ onFileAccepted, accept = ['.txt', '.xlsx'] }) => {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      onFileAccepted(acceptedFiles);
    }
  }, [onFileAccepted]);

  const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
    onDrop,
    accept: accept.reduce((acc, ext) => {
      acc[ext] = [];
      return acc;
    }, {} as Record<string, string[]>),
    multiple: true,
    maxFiles: 20,
  });

  return (
    <div {...getRootProps()} style={{
      border: '2px dashed #888',
      borderRadius: 8,
      padding: 24,
      textAlign: 'center',
      background: isDragActive ? '#f0f8ff' : '#fafafa',
      color: '#333',
      cursor: 'pointer',
      margin: '16px 0',
    }}>
      <input {...getInputProps()} />
      {isDragActive ? (
        <p>Suelta el archivo aquí...</p>
      ) : (
        <p>Arrastra y suelta un archivo .txt o .xlsx aquí, o haz clic para seleccionar</p>
      )}
      {fileRejections.length > 0 && (
        <div style={{ color: 'red', marginTop: 8 }}>
          <p>Solo se permiten archivos .txt o .xlsx</p>
        </div>
      )}
    </div>
  );
};

export default FileDropzone;
