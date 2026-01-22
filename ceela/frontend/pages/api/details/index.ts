import axios from 'axios';
import { NextApiRequest, NextApiResponse } from 'next';
import { getBackendUrl } from '../lib/backend-url';

interface Detail {
  id: number;
  scantilon_location: string;
  name_detail: string;
  material_id: number;
  layer_thickness: number;
  created_status?: string;
  is_deleted?: boolean;
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  const token = req.headers.authorization;
  if (!token) {
    return res.status(401).json({ error: 'No authentication token provided' });
  }
  
  try {
    if (req.method === 'GET') {
      const url = `${getBackendUrl()}/details/`;
      console.log('Calling API URL:', url); // Add this debug log
      const response = await axios.get<Detail[]>(url, {
        headers: { Authorization: token },
      });
      return res.status(200).json(response.data);
    } else if (req.method === 'POST') {
      // Crea un nuevo detalle constructivo
      const payload = req.body;
      const url = `${getBackendUrl()}/details/create`;
      const response = await axios.post(url, payload, {
        headers: {
          Authorization: token,
          'Content-Type': 'application/json',
        },
      });
      return res.status(200).json(response.data);
    } else {
      return res.status(405).json({ error: 'Method not allowed' });
    }
  } catch (error: any) {
    console.error('[API] Error handling details:', error);
    if (axios.isAxiosError(error)) {
      return res.status(error.response?.status || 500).json({
        error: error.response?.data?.detail || 'Error handling details',
      });
    }
    return res.status(500).json({ error: 'Internal server error' });
  }
}
