import { getBackendUrl } from '../lib/backend-url';
import { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(
    req: NextApiRequest,
    res: NextApiResponse
) {
    if (req.method !== 'GET') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    const token = req.headers.authorization;
    if (!token) {
        return res.status(401).json({ error: 'No authentication token provided' });
    }

    try {
        const { code } = req.query;

        if (!code || typeof code !== 'string') {
            return res.status(400).json({ error: 'Material code is required' });
        }

        const url = `${getBackendUrl()}/constants-code_ifc?code_ifc=${code}`;
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                Authorization: token,
            },
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
        console.error('Error fetching material by code:', error);
        return res.status(500).json({ error: 'Internal server error' });
    }
}
