import type { NextApiRequest, NextApiResponse } from 'next';
import axios from 'axios';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { lat, lon } = req.query;

  if (!lat || !lon) {
    return res.status(400).json({ error: 'Latitude and longitude are required' });
  }

  try {
    // Hacer la petición a Nominatim desde el servidor (backend)
    const response = await axios.get('https://nominatim.openstreetmap.org/reverse', {
      params: {
        format: 'jsonv2',
        lat,
        lon,
      },
      headers: {
        'User-Agent': 'CeelaApp/1.0', // Nominatim requiere un User-Agent
      },
    });

    // Devolver la respuesta al frontend
    res.status(200).json(response.data);
  } catch (error) {
    console.error('Error en geocodificación inversa:', error);
    res.status(500).json({
      error: 'Error al obtener datos de geocodificación',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
}
