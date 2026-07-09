"use client"

import { useToast } from "@/hooks/useToast"

export function Toaster() {
  const { toasts, dismiss } = useToast()

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 w-full max-w-sm pointer-events-none">
      {toasts.map((t) => (
        <div
          key={t.id}
          className={`pointer-events-auto flex w-full items-start justify-between gap-4 p-4 rounded-lg border shadow-lg transition-all duration-300 animate-in fade-in slide-in-from-bottom-5 ${
            t.variant === "destructive"
              ? "bg-destructive text-destructive-foreground border-destructive/50"
              : "bg-background text-foreground border-border"
          }`}
        >
          <div className="grid gap-1">
            {t.title && <h4 className="font-semibold text-sm">{t.title}</h4>}
            {t.description && <p className="text-xs opacity-90">{t.description}</p>}
          </div>
          <button
            onClick={() => dismiss(t.id)}
            className="text-xs font-semibold opacity-70 hover:opacity-100 cursor-pointer transition-opacity"
          >
            ✕
          </button>
        </div>
      ))}
    </div>
  )
}
