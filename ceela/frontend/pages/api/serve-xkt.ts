import { promises as fs } from 'fs';
import path from 'path';
import type { NextApiRequest, NextApiResponse } from 'next';

const handler = async (req: NextApiRequest, res: NextApiResponse) => {
    try {
        const publicPath = path.join(process.cwd(), '/public/output.ifc.xkt');

        // Check if file exists
        try {
            await fs.access(publicPath);
        } catch (error) {
            return res.status(404).json({
                status: 'error',
                message: 'File not found. Please upload an IFC file first.'
            });
        }

        // Read the file
        const fileBuffer = await fs.readFile(publicPath);

        // Set appropriate headers for binary data
        res.setHeader('Content-Type', 'application/octet-stream');
        res.setHeader('Content-Disposition', 'inline; filename="output.ifc.xkt"');
        res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
        res.setHeader('Pragma', 'no-cache');
        res.setHeader('Expires', '0');

        // Send the file
        return res.status(200).send(fileBuffer);
    } catch (error) {
        console.error('Error serving XKT file:', error);
        return res.status(500).json({
            status: 'error',
            message: 'Failed to serve file'
        });
    }
};

export default handler;
