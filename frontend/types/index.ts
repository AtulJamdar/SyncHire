// Auth Types
export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
}

export interface RegisterRequest {
  email: string
  password: string
}

export interface VerifyEmailResponse {
  message: string
}

export interface Skill {
  id: number
  name: string
  slug: string
  category: "language" | "framework" | "database" | "cloud" | "tool" | "domain"
}

export interface Company {
  name: string
  logo_url: string | null
  ats_type: string
}

export type ExperienceLevel = "fresher" | "0-1yr" | "1-2yr" | "2-3yr" | "3-5yr" | "5+yr"
export type LocationType = "remote" | "hybrid" | "onsite"
export type SavedJobStatus = "saved" | "applied" | "interviewing" | "rejected" | "offer"

export interface JobListItem {
  id: string
  title: string
  company: Company
  location: string | null
  location_type: LocationType | null
  company_posted_at: string | null
  posted_label: string
  required_skills: string[]
  summary_preview: string[] | null
  apply_url: string
  experience_level: ExperienceLevel | null
  is_internship: boolean
  is_remote: boolean
}

export interface SkillWithMatch {
  name: string
  user_has_skill: boolean
}

export interface JobDetail extends JobListItem {
  summary: string[]
  required_skills_with_match: SkillWithMatch[]
  preferred_skills_with_match: SkillWithMatch[]
  salary_range: string | null
  deadline: string | null
  degree_required: boolean | null
  raw_description: string
}

export interface SavedJob {
  saved_job_id: string
  status: SavedJobStatus
  notes: string | null
  saved_at: string
  status_updated_at: string | null
  job: JobListItem
}

export interface SavedJobStats {
  saved: number
  applied: number
  interviewing: number
  offer: number
  rejected: number
}

export interface UserPreferences {
  experience_level: ExperienceLevel
  open_to_remote: boolean
  open_to_relocation: boolean
  role_type_ids: number[]
  city_ids: number[]
}

export interface PreferencesUpdate {
  experience_level: ExperienceLevel
  open_to_remote: boolean
  open_to_relocation: boolean
  role_type_ids: number[]
  city_ids: number[]
}

export interface NotificationPreferences {
  telegram_enabled: boolean
  email_enabled: boolean
  telegram_frequency: "all" | "exact_match"
  email_digest_frequency: "daily" | "weekly" | "off"
  quiet_hours_enabled: boolean
  quiet_start: string | null
  quiet_end: string | null
  quiet_days: string[] | null
  timezone: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  has_more: boolean
}

export interface JobFilters {
  page?: number
  limit?: number
  role_type?: string
  location?: string
  experience_level?: string
  is_remote?: boolean
  q?: string
}

// Admin types
export interface ScraperHealthItem {
  company_id: number
  company_name: string
  ats_type: string
  last_scraped_at: string | null
  consecutive_failures: number
  jobs_new_24h: number
  last_error_message: string | null
  last_error_type: string | null
  status: "healthy" | "warning" | "failed"
}

export interface NewCompany {
  name: string
  career_page_url: string
  ats_type?: "auto" | "workday" | "greenhouse" | "lever" | "icims" | "taleo" | "generic"
}
