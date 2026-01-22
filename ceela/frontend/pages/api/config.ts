import { NextApiRequest, NextApiResponse } from "next";

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  res.json({ apiEndpoint: process.env.NEXT_PUBLIC_API_ENDPOINT });
}
