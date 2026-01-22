import axios from 'axios';
import { NextApiRequest, NextApiResponse } from 'next';
import { getBackendUrl } from '../lib/backend-url';

interface Project {
  id: number;
  status?: string;
  name_project?: string;
  owner_name?: string;
  designer_name?: string;
  director_name?: string;
  address?: string;
  country?: string;
  divisions?: {
    department?: string;
    province?: string;
    district?: string;
  };
  owner_lastname?: string;
  building_type?: string;
  main_use_type?: string;
  number_levels?: number;
  number_homes_per_level?: number;
  built_surface?: number;
  latitude?: number;
  longitude?: number;
  created_at?: string;
  updated_at?: string;
}

interface ProjectsResponse {
  projects: Project[];
}

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
    const backendUrl = getBackendUrl();
    const url = `${backendUrl}/user/projects/`;
    console.log('[API] 🚀 Calling user/projects:', { url, backendUrl });

    const response = await axios.get<ProjectsResponse>(
      url,
      {
        params: { limit: 999999, num_pag: 1 },
        headers: {
          Authorization: token,
        },
      }
    );

    console.log('[API] ✅ user/projects success:', { projectsCount: response.data.projects.length });
    return res.status(200).json(response.data);
  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error('[API] ❌ Error in user/projects:', {
        message: error.message,
        status: error.response?.status,
        url: error.config?.url,
        responseData: error.response?.data
      });

      return res.status(error.response?.status || 500).json({
        error: error.response?.data?.detail || 'Error fetching projects',
        details: error.response?.data
      });
    }
    console.error('[API] ❌ Error in user/projects:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
}
