"use client"

import { useState } from "react"
import { useForgotPassword } from "@/hooks/useForgotPassword"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import Link from "next/link"

export function ForgotPasswordForm() {
  const [email, setEmail] = useState("")
  const [emailError, setEmailError] = useState("")
  const [submitted, setSubmitted] = useState(false)
  const forgotPasswordMutation = useForgotPassword()

  const validateEmail = (value: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(value)
  }

  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setEmail(value)
    if (!value) {
      setEmailError("Email is required")
    } else if (!validateEmail(value)) {
      setEmailError("Please enter a valid email address")
    } else {
      setEmailError("")
    }
  }

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()

    if (!email) {
      setEmailError("Email is required")
      return
    }

    if (!validateEmail(email)) {
      setEmailError("Please enter a valid email address")
      return
    }

    forgotPasswordMutation.mutate(
      { email },
      {
        onSuccess: () => {
          setSubmitted(true)
        },
        onError: (error: any) => {
          const message = error?.response?.data?.detail || "Unable to send reset link. Please try again."
          setEmailError(message)
        },
      }
    )
  }

  if (submitted) {
    return (
      <div className="space-y-6 text-center">
        <div className="space-y-2">
          <div className="text-4xl mb-4">📩</div>
          <h2 className="text-xl font-semibold">Check your inbox</h2>
          <p className="text-sm text-muted-foreground">
            If an account exists with that email, we have sent password reset instructions.
          </p>
        </div>

        <div className="space-y-3">
          <Link href="/login">
            <Button className="w-full">Back to Sign In</Button>
          </Link>
        </div>
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="email">Email</Label>
        <Input
          id="email"
          type="email"
          placeholder="you@example.com"
          value={email}
          onChange={handleEmailChange}
          disabled={forgotPasswordMutation.isPending}
          className={emailError ? "border-destructive" : ""}
          aria-describedby={emailError ? "email-error" : undefined}
        />
        {emailError && (
          <p id="email-error" className="text-sm text-destructive" role="alert" aria-live="polite">
            {emailError}
          </p>
        )}
      </div>

      <Button type="submit" className="w-full" disabled={forgotPasswordMutation.isPending} aria-busy={forgotPasswordMutation.isPending}>
        {forgotPasswordMutation.isPending ? "Sending reset link..." : "Send reset link"}
      </Button>

      <div className="flex flex-col gap-2 text-center text-sm">
        <Link href="/login" className="text-primary hover:underline">
          Back to Sign In
        </Link>
        <Link href="/register" className="text-muted-foreground hover:text-foreground">
          Create a new account
        </Link>
      </div>
    </form>
  )
}
