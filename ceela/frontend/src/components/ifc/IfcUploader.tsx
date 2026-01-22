import axios from 'axios';
import { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { toast } from 'react-toastify';

interface IfcUploaderProps {
  onFileUpload: (data: any) => void;
}

const IFCUploader = ({ onFileUpload }: IfcUploaderProps) => {
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [uploadProgress, setUploadProgress] = useState(0);

    const { getRootProps, getInputProps } = useDropzone({
        maxFiles: 1,
        validator: (file) => {
            if (file.size > 104857600) {
                return {
                    code: 'file-too-large',
                    message: 'El archivo es demasiado grande. El tamaño máximo permitido es 100 MB.'
                };
            }
            if (!file.name?.endsWith('.ifc')) {
                return {
                    code: 'file-invalid-type',
                    message: 'Solo se permiten archivos con extensión .ifc'
                };
            }
            return null;
        },
        multiple: false,
        onDrop: (acceptedFiles) => {
            if (acceptedFiles.length && acceptedFiles[0].name?.endsWith('.ifc')) {
                setSelectedFile(acceptedFiles[0]);
                handleFileUpload(acceptedFiles[0]);
            } else {
                toast.error('Solo se permiten archivos con extensión .ifc')
            }
        }
    });

    const handleFileUpload = async (file: string | Blob) => {
        const formData = new FormData();
        formData.append('file', file);

        toast.info('Subiendo archivo IFC...');
        setUploadProgress(0);

        try {
            const response = await axios.post('/api/ifc', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                },
                onUploadProgress: (progressEvent) => {
                    if (progressEvent.total) {
                        const progress = Math.round((progressEvent.loaded / progressEvent.total) * 100);
                        setUploadProgress(progress);
                    }
                }
            });
            onFileUpload(response.data);
        } catch (error:any) {
            const errorMessage = error.response?.data?.message ||
                error.message ||
                'Error desconocido';
            console.error('Error details :', error);
            toast.error(`Error al subir el archivo: ${errorMessage}`);
            return; // Return early to prevent showing success message
        }
        toast.success('Archivo subido correctamente');

    };

    return (
        <section className="container">
            <div
                {...getRootProps({ className: 'dropzone' })}
                style={{
                    border: '2px dashed #ccc',
                    padding: 20,
                    textAlign: 'center',
                    cursor: 'pointer',
                    borderRadius: '4px',
                    backgroundColor: '#fafafa',
                    marginBottom: '10px'
                }}
            >
                <input {...getInputProps()} />
                <p>Arrastra y suelta un archivo .ifc aquí o haz clic para seleccionar uno</p>
            </div>
            {selectedFile && (
                <aside style={{
                    padding: '10px',
                    backgroundColor: '#e9ecef',
                    borderRadius: '4px'
                }}>
                    <h4>Archivo seleccionado:</h4>
                    <ul>
                        <li>{selectedFile.name} - {Math.round(selectedFile.size / 1024)} KB</li>
                    </ul>
                    <div style={{ width: '100%', backgroundColor: '#ccc' }}>
                        <div style={{
                            width: `${uploadProgress}%`,
                            height: '10px',
                            backgroundColor: '#4caf50'
                        }} />
                    </div>
                </aside>
            )}
        </section>
    );
};

export default IFCUploader;
