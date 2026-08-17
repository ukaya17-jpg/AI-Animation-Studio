import { apiClient } from './api'

export type Project = {
  id: string
  owner_id: string
  name: string
  created_at: string
}

export async function createProject(name: string): Promise<Project> {
  const response = await apiClient.post<Project>('/projects', { name })
  return response.data
}

export async function fetchProjects(): Promise<Project[]> {
  const response = await apiClient.get<Project[]>('/projects')
  return response.data
}
