import { getBackendUrl } from '../lib/backend-url';
import { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(
    req: NextApiRequest,
    res: NextApiResponse
) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    const token = req.headers.authorization;
    if (!token) {
        return res.status(401).json({ error: 'No authentication token provided' });
    }

    try {
        const {
            wall_id,
            po1_length,
            po1_id_element,
            po2_length,
            po2_id_element,
            po3_length,
            po3_id_element,
            po4_length,
            po4_e_aislacion,
            po4_id_element
        } = req.body;

        if (!wall_id) {
            return res.status(400).json({ error: 'wall_id is required' });
        }

        const url = `${getBackendUrl()}/thermal-bridge-create`;
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Authorization: token,
            },
            body: JSON.stringify({
                wall_id,
                po1_length: po1_length || 0,
                po1_id_element: po1_id_element || 0,
                po2_length: po2_length || 0,
                po2_id_element: po2_id_element || 0,
                po3_length: po3_length || 0,
                po3_id_element: po3_id_element || 0,
                po4_length: po4_length || 0,
                po4_e_aislacion: po4_e_aislacion || 0,
                po4_id_element: po4_id_element || 0
            }),
        });

        if (!response.ok) {
            const errorText = await response.text();
            return res.status(response.status).json({
                error: `Error from API: ${response.status}`,
                details: errorText
            });
        }

        const data = await response.json();
        return res.status(200).json(data);
    } catch (error) {
        console.error('Error creating thermal bridge:', error);
        return res.status(500).json({ error: 'Internal server error' });
    }
}