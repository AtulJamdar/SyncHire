import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

/**
 * Merges Tailwind CSS classes with clsx and tailwind-merge logic.
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Returns the user's prefers-reduced-motion media query status.
 */
export function getMotionPreference(): "no-preference" | "reduce" {
  if (typeof window === "undefined") return "no-preference"
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches
    ? "reduce"
    : "no-preference"
}

/**
 * Converts an ISO date string into a relative time string (e.g. "2 hours ago").
 */
export function formatPostedAt(isoString: string): string {
  const date = new Date(isoString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  
  if (isNaN(diffMs) || diffMs < 0) return "Posted recently"
  
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMins / 60)
  const diffDays = Math.floor(diffHours / 24)

  if (diffMins < 1) {
    return "just now"
  } else if (diffMins < 60) {
    return `${diffMins} ${diffMins === 1 ? "minute" : "minutes"} ago`
  } else if (diffHours < 24) {
    return `${diffHours} ${diffHours === 1 ? "hour" : "hours"} ago`
  } else if (diffDays < 7) {
    return `${diffDays} ${diffDays === 1 ? "day" : "days"} ago`
  } else {
    const diffWeeks = Math.floor(diffDays / 7)
    return `${diffWeeks} ${diffWeeks === 1 ? "week" : "weeks"} ago`
  }
}

/**
 * Formats an ISO date string into a human-readable date format (e.g. "Jul 9, 2026").
 */
export function formatDate(isoString: string): string {
  const date = new Date(isoString)
  if (isNaN(date.getTime())) return ""
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  })
}

/**
 * Returns true if there are active query filter keys in the filters object.
 */
export function hasActiveFilters(filters: any): boolean {
  if (!filters) return false
  return Object.entries(filters).some(([key, val]) => {
    if (key === "page" || key === "limit") return false
    if (val === undefined || val === null || val === "") return false
    if (typeof val === "boolean" && val === false) return false
    return true
  })
}
