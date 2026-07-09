import { useState, useEffect } from "react"

export interface ToastProps {
  id: string
  title?: string
  description?: string
  variant?: "default" | "destructive"
}

type ToastListener = (toasts: ToastProps[]) => void
let listeners: ToastListener[] = []
let toasts: ToastProps[] = []

export function toast({ title, description, variant }: Omit<ToastProps, "id">) {
  const id = Math.random().toString(36).substring(2, 9)
  const newToast: ToastProps = { id, title, description, variant }
  toasts = [...toasts, newToast]
  listeners.forEach((listener) => listener(toasts))
  
  // Auto dismiss after 5 seconds
  setTimeout(() => {
    toasts = toasts.filter((t) => t.id !== id)
    listeners.forEach((listener) => listener(toasts))
  }, 5000)
  
  return id
}

export function useToast() {
  const [activeToasts, setActiveToasts] = useState<ToastProps[]>(toasts)

  useEffect(() => {
    const listener = (newToasts: ToastProps[]) => {
      setActiveToasts(newToasts)
    }
    listeners.push(listener)
    return () => {
      listeners = listeners.filter((l) => l !== listener)
    }
  }, [])

  const dismiss = (id: string) => {
    toasts = toasts.filter((t) => t.id !== id)
    listeners.forEach((listener) => listener(toasts))
  }

  return {
    toast,
    toasts: activeToasts,
    dismiss
  }
}
