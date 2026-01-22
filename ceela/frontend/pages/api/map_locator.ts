// First install the AWS SDK Location package:
// npm install @aws-sdk/client-location
import { LocationClient, SearchPlaceIndexForPositionCommand } from "@aws-sdk/client-location";
import type { NextApiRequest, NextApiResponse } from 'next';


type ResponseData = {
    message?: string
    query?: string
    results?: any
    error?: string
}

const client = new LocationClient({
    region: "us-east-1",
    credentials: {
        accessKeyId: process.env.AWS_ACCESS_KEY_ID || '',
        secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY || ''
    }
});

export default async function handler(
    req: NextApiRequest,
    res: NextApiResponse<ResponseData>
) {
    if (req.method !== 'GET') {
        return res.status(405).json({ message: 'Method not allowed' })
    }

    try {
        // Extract the query parameters from the request
        const { lat, long } = req.query

        // Validate the latitude and longitude parameters
        if (!lat || !long || typeof lat !== 'string' || typeof long !== 'string') {
            return res.status(400).json({ message: 'Latitude and longitude parameters are required and must be strings' })
        }

        const command = new SearchPlaceIndexForPositionCommand({
            IndexName: process.env?.AWS_PLACE_INDEX_NAME || "CeelaIndex",  
            Position: [parseFloat(long), parseFloat(lat)] ,
            Key: process.env?.PLACES_API_KEY,
        });

        const response = await client.send(command);

        if (response.Results && response.Results.length > 0) {
            res.status(200).json({
                results: response.Results[0].Place
            })
        } else {
            res.status(404).json({
                message: 'No location found for these coordinates'
            })
        }
    } catch (error) {
        console.error('Error in reverse geocoding:', error)
        res.status(500).json({ message: 'Internal Server Error' })
    }
}
