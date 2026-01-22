'use client'
import { useRouter } from 'next/router';
import React, { useEffect, useState } from 'react';
import Card from './common/Card';

const WelcomeCard: React.FC = () => {
  const router = useRouter();
  const [lastname, setLastname] = useState<string>('');
  const [name, setName] = useState<string>('');

  useEffect(() => {
    const userProfile = localStorage.getItem("userProfile");
    if (userProfile) {
      const profile = JSON.parse(userProfile);
      setLastname(profile.lastname);
      setName(profile.name);
    }
  }, []);

  const handleViewProfile = () => {
    console.log('Ver perfil');
    router.push('/edit-profile'); 
  };


  return (
    <Card
    >
      <div
        className="card-body"
        style={{
          backgroundColor: 'white',
          backgroundSize: 'cover',
          backgroundRepeat: 'no-repeat',
          backgroundPosition: 'center',
          padding: '1rem',
          position: 'relative',
          zIndex: 1,
          height: '200px',
          minHeight: '230px'
        }}
      >
        <div className="d-flex align-items-center justify-content-center" style={{ height: '100%' }}>
          <div className="text-start" style={{ textAlign: 'center' }}>
            <h1 style={{ color: '#3ca7b7', fontSize: '1.8rem', fontWeight: 600, marginBottom: '0.5rem', textShadow: '1px 1px 2px rgba(0,0,0,0.1)' }}>Hola 👋, {name} {lastname}</h1>
            <p style={{ color: '#3ca7b7', fontSize: '1.1rem', opacity: 0.9, marginBottom: '0.25rem' }}>¡Bienvenidos de nuevo! 🎉</p>
            <p style={{ color: '#3ca7b7', fontSize: '1.1rem', opacity: 0.9, marginBottom: '0.75rem' }}>Empecemos desde donde lo dejaste.</p>
            <button
              className="btn profile-btn"
              onClick={handleViewProfile}
              style={{
                border: '2px solid #3ca7b7',
                color: '#3ca7b7',
                background: 'white',
                padding: '6px 16px',
                borderRadius: '20px',
                fontSize: '0.85rem',
                fontWeight: 500,
                letterSpacing: '0.2px',
                transition: 'all 0.3s ease'
              }}
            >
              Ver perfil 👤
              <style jsx>{`
                .profile-btn {
                  transition: all 0.3s ease;
                  cursor: pointer;
                }
                .profile-btn:hover {
                  transform: scale(1.05);
                  opacity: 0.9; 
                  background-color: rgba(255, 255, 255, 0.1);
                  box-shadow: 0 0 10px rgba(255, 255, 255, 0.2);
                }
              `}</style>
            </button>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default WelcomeCard;