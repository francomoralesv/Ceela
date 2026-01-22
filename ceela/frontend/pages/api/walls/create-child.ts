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
            masterNodeId,
            scantilonLocation,
            name,
            materialId,
            layerThickness
        } = req.body;

        if (!masterNodeId || !name || materialId === undefined || layerThickness === undefined) {
            return res.status(400).json({ error: 'Missing required parameters' });
        }

        const url = `${getBackendUrl()}/user/detail-create/${masterNodeId}`;
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Authorization: token,
            },
            body: JSON.stringify({
                scantilon_location: scantilonLocation || 'Muro',
                name_detail: name,
                material_id: materialId,
                layer_thickness: layerThickness
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
        console.error('Error creating wall child node:', error);
        return res.status(500).json({ error: 'Internal server error' });
    }
}
