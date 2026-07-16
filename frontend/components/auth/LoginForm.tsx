"use client"

import { useState } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { useLogin } from "@/hooks/useLogin"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import Link from "next/link"

export function LoginForm() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const nextUrl = searchParams.get("next") || "/jobs"

  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [emailError, setEmailError] = useState("")
  const [passwordError, setPasswordError] = useState("")

  const loginMutation = useLogin()

  // Simple email validation
  const validateEmail = (value: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(value)
  }

  // Handle email field change with inline validation
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

  // Handle password field change with inline validation
  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setPassword(value)

    if (!value) {
      setPasswordError("Password is required")
    } else {
      setPasswordError("")
    }
  }

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()

    // Validate before submission
    let hasErrors = false
    if (!email) {
      setEmailError("Email is required")
      hasErrors = true
    } else if (!validateEmail(email)) {
      setEmailError("Please enter a valid email address")
      hasErrors = true
    }

    if (!password) {
      setPasswordError("Password is required")
      hasErrors = true
    }

    if (hasErrors) return

    // Attempt login
    loginMutation.mutate(
      { email, password },
      {
        onSuccess: () => {
          // Redirect to next URL or jobs page
          router.push(nextUrl)
        },
        onError: (error: any) => {
          // Handle login error
          const message =
            error?.response?.data?.detail || "Login failed. Please try again."
          setPasswordError(message)
        },
      }
    )
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Email Input */}
      <div className="space-y-2">
        <Label htmlFor="email">Email</Label>
        <Input
          id="email"
          type="email"
          placeholder="you@example.com"
          value={email}
          onChange={handleEmailChange}
          onBlur={() => {
            if (!email) {
              setEmailError("Email is required")
            }
          }}
          disabled={loginMutation.isPending}
          className={emailError ? "border-destructive" : ""}
          aria-describedby={emailError ? "email-error" : undefined}
        />
        {emailError && (
          <p
            id="email-error"
            className="text-sm text-destructive"
            role="alert"
            aria-live="polite"
          >
            {emailError}
          </p>
        )}
      </div>

      {/* Password Input */}
      <div className="space-y-2">
        <Label htmlFor="password">Password</Label>
        <Input
          id="password"
          type="password"
          placeholder="••••••••"
          value={password}
          onChange={handlePasswordChange}
          onBlur={() => {
            if (!password) {
              setPasswordError("Password is required")
            }
          }}
          disabled={loginMutation.isPending}
          className={passwordError ? "border-destructive" : ""}
          aria-describedby={passwordError ? "password-error" : undefined}
        />
        {passwordError && (
          <p
            id="password-error"
            className="text-sm text-destructive"
            role="alert"
            aria-live="polite"
          >
            {passwordError}
          </p>
        )}
      </div>

      {/* Sign In Button */}
      <Button
        type="submit"
        className="w-full"
        disabled={loginMutation.isPending}
        aria-busy={loginMutation.isPending}
      >
        {loginMutation.isPending ? "Signing in..." : "Sign In"}
      </Button>

      {/* Continue with Google */}
      <Button
        type="button"
        variant="outline"
        className="w-full"
        disabled={loginMutation.isPending}
        onClick={() => {
          // TODO: Implement Google OAuth flow
          // For now, this is a placeholder
          const redirectUri = `${window.location.origin}/api/auth/oauth/google/callback`
          const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID
          if (clientId) {
            window.location.href = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code&scope=openid%20email%20profile`
          }
        }}
        aria-label="Continue with Google"
      >
        Continue with Google
      </Button>

      {/* Links */}
      <div className="flex flex-col gap-2 text-center text-sm">
        <Link
          href="/register"
          className="text-primary hover:underline"
        >
          Don't have an account? Register
        </Link>
        <Link
          href="/forgot-password"
          className="text-muted-foreground hover:text-foreground"
        >
          Forgot your password?
        </Link>
      </div>
    </form>
  )
}
