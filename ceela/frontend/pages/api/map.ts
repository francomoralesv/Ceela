
import axios from 'axios'
import type { NextApiRequest, NextApiResponse } from 'next'

type ResponseData = {
    message?: string
    query?: string
    results?: any
    error?: string
}

export default async function handler(
    req: NextApiRequest,
    res: NextApiResponse<ResponseData>
) {
    if (req.method !== 'GET') {
        return res.status(405).json({ message: 'Method not allowed' })
    }

    try {
        // Extract the query parameter 'q' from the request
        const { q, lat, long } = req.query

        // Validate the query parameter
        if (!q || typeof q !== 'string') {
            return res.status(400).json({ message: 'Query parameter "q" is required and must be a string' })
        }
        const placesApiKey = process.env?.PLACES_API_KEY || ''
        const region = process.env?.AWS_REGION || ''
        if (!q) return []
        const response = await axios.post(
            `https://places.geo.${region}.amazonaws.com/v2/search-text?key=${placesApiKey}`,
            {
                QueryText: q,
                BiasPosition: [lat, long],
            },
            {
                headers: {
                    'Content-Type': 'application/json'
                }
            }
        )

        if (response.status !== 200) {
            return res.status(response.status).json({
                error: 'Error from Places API',
                results: response.data
            })
        }

        res.status(200).json({
            results: response.data
        })
    } catch (error) {
        console.error('Error in map API:', error)
        res.status(500).json({ message: 'Internal Server Error' })
    }
}
