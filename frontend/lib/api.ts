import axios from "axios"
import { getAccessToken, setAccessToken, clearAccessToken } from "./auth"
import {
  JobFilters,
  PaginatedResponse,
  JobListItem,
  JobDetail,
  PreferencesUpdate,
  Skill,
  NewCompany,
  ScraperHealthItem
} from "@/types"

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000",
  withCredentials: true, // Required for httpOnly refresh token cookie
})

// Request interceptor — attach access token if present in memory
apiClient.interceptors.request.use((config) => {
  const token = getAccessToken()
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor — catch 401, attempt silent refresh, retry original request
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && original && !original._retry) {
      original._retry = true
      try {
        // Silent token refresh call — relies on httpOnly refresh_token cookie
        const { data } = await apiClient.post<{ access_token: string }>("/api/auth/refresh")
        setAccessToken(data.access_token)
        
        // Update Authorization header on original config and retry
        if (original.headers) {
          original.headers.Authorization = `Bearer ${data.access_token}`
        }
        return apiClient(original)
      } catch (refreshError) {
        // Clear expired/invalid access tokens and redirect to login
        clearAccessToken()
        if (typeof window !== "undefined") {
          window.location.href = "/login"
        }
        return Promise.reject(refreshError)
      }
    }
    return Promise.reject(error)
  }
)

// Domain-grouped API wrappers
export const api = {
  jobs: {
    list: (params: JobFilters) =>
      apiClient.get<PaginatedResponse<JobListItem>>("/api/jobs", { params }).then((r) => r.data),
    getById: (id: string) =>
      apiClient.get<JobDetail>(`/api/jobs/${id}`).then((r) => r.data),
  },
  savedJobs: {
    list: (params?: { status?: string[] }) =>
      apiClient.get<any[]>("/api/saved-jobs", { params }).then((r) => r.data),
    save: (jobId: string) =>
      apiClient.post("/api/saved-jobs", { job_id: jobId }).then((r) => r.data),
    unsave: (jobId: string) =>
      apiClient.delete(`/api/saved-jobs/${jobId}`).then((r) => r.data),
    updateStatus: (jobId: string, status: string, notes?: string) =>
      apiClient.patch(`/api/saved-jobs/${jobId}`, { status, notes }).then((r) => r.data),
    getStats: () =>
      apiClient.get<any>("/api/saved-jobs/stats").then((r) => r.data),
  },
  profile: {
    get: () => apiClient.get<any>("/api/profile/preferences").then((r) => r.data),
    updateSkills: (skill_ids: number[]) =>
      apiClient.put("/api/profile/skills", { skill_ids }).then((r) => r.data),
    updatePreferences: (data: PreferencesUpdate) =>
      apiClient.put("/api/profile/preferences", data).then((r) => r.data),
  },
  skills: {
    search: (q: string) =>
      apiClient.get<Skill[]>("/api/skills", { params: { q } }).then((r) => r.data),
  },
  telegram: {
    generateLinkCode: () =>
      apiClient.post<{ code: string }>("/api/telegram/generate-link-code").then((r) => r.data),
    getStatus: () =>
      apiClient.get<any>("/api/profile/telegram-status").then((r) => r.data),
  },
  admin: {
    getScraperHealth: () =>
      apiClient.get<ScraperHealthItem[]>("/api/admin/scraper-health").then((r) => r.data),
    addCompany: (data: NewCompany) =>
      apiClient.post<any>("/api/admin/companies", data).then((r) => r.data),
    runNow: (companyId: number) =>
      apiClient.post<any>(`/api/admin/companies/${companyId}/run-now`).then((r) => r.data),
    getReviewQueue: () =>
      apiClient.get<JobDetail[]>("/api/admin/review-queue").then((r) => r.data),
    approveJob: (jobId: string, edits?: Partial<JobDetail>) =>
      apiClient.post<any>(`/api/admin/review-queue/${jobId}/approve`, { edited_fields: edits }).then((r) => r.data),
    rejectJob: (jobId: string) =>
      apiClient.post<any>(`/api/admin/review-queue/${jobId}/reject`).then((r) => r.data),
  },
}
