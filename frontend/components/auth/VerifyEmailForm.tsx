"use client"

import { useEffect, useState } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { useVerifyEmail } from "@/hooks/useVerifyEmail"
import { Button } from "@/components/ui/button"
import Link from "next/link"

type State = "loading" | "success" | "invalid_token" | "expired_token" | "error"

export function VerifyEmailForm() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const token = searchParams.get("token")
  const [state, setState] = useState<State>("loading")

  const verifyEmailMutation = useVerifyEmail()

  useEffect(() => {
    if (!token) {
      setState("invalid_token")
      return
    }

    const verifyEmail = async () => {
      try {
        await verifyEmailMutation.mutateAsync(token)
        setState("success")
        // Redirect to onboarding after 2 seconds
        const timer = setTimeout(() => {
          router.push("/onboarding/1")
        }, 2000)
        return () => clearTimeout(timer)
      } catch (error: any) {
        const statusCode = error.response?.status
        if (statusCode === 410) {
          setState("expired_token")
        } else if (statusCode === 400) {
          setState("invalid_token")
        } else {
          setState("error")
        }
      }
    }

    verifyEmail()
  }, [token, verifyEmailMutation, router])

  if (state === "loading") {
    return (
      <div className="space-y-6 text-center">
        <div className="flex justify-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-muted border-t-primary" />
        </div>
        <p className="text-sm text-muted-foreground">Verifying your email...</p>
      </div>
    )
  }

  if (state === "success") {
    return (
      <div className="space-y-6 text-center">
        <div className="space-y-2">
          <div className="text-4xl mb-4">✅</div>
          <h2 className="text-xl font-semibold">Email verified successfully!</h2>
          <p className="text-sm text-muted-foreground">
            Your account is now active. Let&apos;s set up your profile.
          </p>
        </div>
        <div className="pt-4">
          <p className="text-xs text-muted-foreground">Redirecting to onboarding...</p>
        </div>
      </div>
    )
  }

  if (state === "invalid_token") {
    return (
      <div className="space-y-6 text-center">
        <div className="space-y-2">
          <div className="text-4xl mb-4">❌</div>
          <h2 className="text-xl font-semibold">Invalid verification link</h2>
          <p className="text-sm text-muted-foreground">
            The verification link is invalid or has already been used.
          </p>
        </div>
        <div className="space-y-3 pt-2">
          <p className="text-sm">Need a new verification email?</p>
          <Link href="/login">
            <Button variant="outline" className="w-full">
              Back to Sign In
            </Button>
          </Link>
        </div>
      </div>
    )
  }

  if (state === "expired_token") {
    return (
      <div className="space-y-6 text-center">
        <div className="space-y-2">
          <div className="text-4xl mb-4">⏰</div>
          <h2 className="text-xl font-semibold">Verification link expired</h2>
          <p className="text-sm text-muted-foreground">
            Verification links expire after 24 hours. Please request a new one.
          </p>
        </div>
        <div className="space-y-3 pt-2">
          <p className="text-sm">Need a new verification email?</p>
          <Link href="/login">
            <Button className="w-full">
              Back to Sign In
            </Button>
          </Link>
        </div>
      </div>
    )
  }

  // error state
  return (
    <div className="space-y-6 text-center">
      <div className="space-y-2">
        <div className="text-4xl mb-4">⚠️</div>
        <h2 className="text-xl font-semibold">Something went wrong</h2>
        <p className="text-sm text-muted-foreground">
          We encountered an error while verifying your email. Please try again.
        </p>
      </div>
      <div className="space-y-3 pt-2">
        <Link href="/login">
          <Button variant="outline" className="w-full">
            Back to Sign In
          </Button>
        </Link>
      </div>
    </div>
  )
}
