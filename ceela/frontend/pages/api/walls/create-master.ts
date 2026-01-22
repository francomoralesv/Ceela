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
        const { projectId, name, interiorColor, exteriorColor } = req.body;

        if (!projectId || !name) {
            return res.status(400).json({ error: 'Missing required parameters' });
        }

        const url = `${getBackendUrl()}/user/Muro/detail-part-create?project_id=${projectId}`;
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Authorization: token,
            },
            body: JSON.stringify({
                name_detail: name,
                info: {
                    surface_color: {
                        interior: { name: interiorColor || 'Claro' },
                        exterior: { name: exteriorColor || 'Claro' }
                    }
                }
            }),
        });

        if (!response.ok) {
            return res.status(response.status).json({
                error: `Error from API: ${response.status}`,
                details: await response.text()
            });
        }

        const data = await response.json();
        return res.status(200).json(data);
    } catch (error) {
        console.error('Error creating wall master node:', error);
        return res.status(500).json({ error: 'Internal server error' });
    }
}
