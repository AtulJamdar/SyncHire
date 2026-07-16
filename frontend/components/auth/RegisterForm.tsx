"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useRegister } from "@/hooks/useRegister"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { cn } from "@/lib/utils"
import Link from "next/link"

// Password strength indicator thresholds
const calculatePasswordStrength = (password: string): "weak" | "fair" | "strong" => {
  if (!password) return "weak"

  let score = 0

  // Length
  if (password.length >= 8) score++
  if (password.length >= 12) score++

  // Character variety
  if (/[a-z]/.test(password)) score++
  if (/[A-Z]/.test(password)) score++
  if (/[0-9]/.test(password)) score++
  if (/[^a-zA-Z0-9]/.test(password)) score++

  if (score <= 2) return "weak"
  if (score <= 4) return "fair"
  return "strong"
}

const getStrengthColor = (strength: "weak" | "fair" | "strong") => {
  switch (strength) {
    case "weak":
      return "bg-destructive"
    case "fair":
      return "bg-amber-500"
    case "strong":
      return "bg-emerald-500"
  }
}

const getStrengthLabel = (strength: "weak" | "fair" | "strong") => {
  switch (strength) {
    case "weak":
      return "Weak"
    case "fair":
      return "Fair"
    case "strong":
      return "Strong"
  }
}

interface ConfirmationState {
  email: string
}

export function RegisterForm() {
  const router = useRouter()

  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")

  const [nameError, setNameError] = useState("")
  const [emailError, setEmailError] = useState("")
  const [passwordError, setPasswordError] = useState("")
  const [confirmPasswordError, setConfirmPasswordError] = useState("")

  const [confirmationState, setConfirmationState] = useState<ConfirmationState | null>(null)

  const registerMutation = useRegister()

  // Email validation regex
  const validateEmail = (value: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(value)
  }

  // Password validation per security policy
  const validatePassword = (value: string): string | null => {
    if (!value) return "Password is required"
    if (value.length < 8) return "Password must be at least 8 characters"
    if (value.length > 128) return "Password must be under 128 characters"
    if (!/[a-zA-Z]/.test(value)) return "Password must contain at least one letter"
    if (!/[0-9]/.test(value)) return "Password must contain at least one number"
    return null
  }

  // Handle name change
  const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setName(value)

    if (!value) {
      setNameError("Name is required")
    } else {
      setNameError("")
    }
  }

  // Handle email change
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

  // Handle password change
  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setPassword(value)

    const error = validatePassword(value)
    setPasswordError(error || "")

    // Clear confirm password error if password changes
    if (confirmPassword && value !== confirmPassword) {
      setConfirmPasswordError("Passwords do not match")
    } else if (confirmPassword) {
      setConfirmPasswordError("")
    }
  }

  // Handle confirm password change
  const handleConfirmPasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setConfirmPassword(value)

    if (!value) {
      setConfirmPasswordError("Please confirm your password")
    } else if (value !== password) {
      setConfirmPasswordError("Passwords do not match")
    } else {
      setConfirmPasswordError("")
    }
  }

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()

    // Validate all fields
    let hasErrors = false

    if (!name) {
      setNameError("Name is required")
      hasErrors = true
    }

    if (!email) {
      setEmailError("Email is required")
      hasErrors = true
    } else if (!validateEmail(email)) {
      setEmailError("Please enter a valid email address")
      hasErrors = true
    }

    const passwordErr = validatePassword(password)
    if (passwordErr) {
      setPasswordError(passwordErr)
      hasErrors = true
    }

    if (!confirmPassword) {
      setConfirmPasswordError("Please confirm your password")
      hasErrors = true
    } else if (confirmPassword !== password) {
      setConfirmPasswordError("Passwords do not match")
      hasErrors = true
    }

    if (hasErrors) return

    // Attempt registration
    registerMutation.mutate(
      { name, email, password },
      {
        onSuccess: () => {
          // Show confirmation screen
          setConfirmationState({ email })
        },
        onError: (error: any) => {
          // Handle registration error
          const message =
            error?.response?.data?.detail || "Registration failed. Please try again."
          setEmailError(message)
        },
      }
    )
  }

  // If registration was successful, show confirmation screen
  if (confirmationState) {
    return (
      <div className="space-y-6 text-center">
        <div className="space-y-2">
          <div className="text-4xl mb-4">📧</div>
          <h2 className="text-xl font-semibold">Check your email</h2>
          <p className="text-sm text-muted-foreground">
            We've sent a verification link to{" "}
            <span className="font-medium text-foreground">{confirmationState.email}</span>
          </p>
        </div>

        <div className="bg-muted/50 border border-border rounded-lg p-4 space-y-2 text-sm">
          <p className="text-muted-foreground">
            Click the link in your email to verify your account. If you don't see it in a few
            minutes, check your spam folder.
          </p>
        </div>

        <Link
          href="/login"
          className="inline-flex h-10 items-center justify-center rounded-md bg-primary px-8 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
        >
          Back to Login
        </Link>
      </div>
    )
  }

  // Regular registration form
  const passwordStrength = calculatePasswordStrength(password)

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Name Input */}
      <div className="space-y-2">
        <Label htmlFor="name">Full Name</Label>
        <Input
          id="name"
          type="text"
          placeholder="John Doe"
          value={name}
          onChange={handleNameChange}
          onBlur={() => {
            if (!name) setNameError("Name is required")
          }}
          disabled={registerMutation.isPending}
          className={nameError ? "border-destructive" : ""}
          aria-describedby={nameError ? "name-error" : undefined}
        />
        {nameError && (
          <p
            id="name-error"
            className="text-sm text-destructive"
            role="alert"
            aria-live="polite"
          >
            {nameError}
          </p>
        )}
      </div>

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
            } else if (!validateEmail(email)) {
              setEmailError("Please enter a valid email address")
            }
          }}
          disabled={registerMutation.isPending}
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
            const error = validatePassword(password)
            if (error) setPasswordError(error)
          }}
          disabled={registerMutation.isPending}
          className={passwordError ? "border-destructive" : ""}
          aria-describedby={passwordError ? "password-error" : "password-strength"}
        />

        {/* Password Strength Indicator */}
        {password && (
          <div className="space-y-1.5">
            <div className="flex gap-1">
              <div
                className={cn(
                  "flex-1 h-1 rounded-full transition-colors",
                  getStrengthColor(passwordStrength)
                )}
              />
              <div
                className={cn(
                  "flex-1 h-1 rounded-full transition-colors",
                  passwordStrength === "strong" ? getStrengthColor("strong") : "bg-muted"
                )}
              />
              <div
                className={cn(
                  "flex-1 h-1 rounded-full transition-colors",
                  passwordStrength === "strong" ? getStrengthColor("strong") : "bg-muted"
                )}
              />
            </div>
            <p
              id="password-strength"
              className="text-xs text-muted-foreground"
              aria-live="polite"
            >
              Password strength: <span className="font-medium">{getStrengthLabel(passwordStrength)}</span>
            </p>
          </div>
        )}

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

      {/* Confirm Password Input */}
      <div className="space-y-2">
        <Label htmlFor="confirmPassword">Confirm Password</Label>
        <Input
          id="confirmPassword"
          type="password"
          placeholder="••••••••"
          value={confirmPassword}
          onChange={handleConfirmPasswordChange}
          onBlur={() => {
            if (!confirmPassword) {
              setConfirmPasswordError("Please confirm your password")
            } else if (confirmPassword !== password) {
              setConfirmPasswordError("Passwords do not match")
            }
          }}
          disabled={registerMutation.isPending}
          className={confirmPasswordError ? "border-destructive" : ""}
          aria-describedby={confirmPasswordError ? "confirm-password-error" : undefined}
        />
        {confirmPasswordError && (
          <p
            id="confirm-password-error"
            className="text-sm text-destructive"
            role="alert"
            aria-live="polite"
          >
            {confirmPasswordError}
          </p>
        )}
      </div>

      {/* Sign Up Button */}
      <Button
        type="submit"
        className="w-full"
        disabled={registerMutation.isPending}
        aria-busy={registerMutation.isPending}
      >
        {registerMutation.isPending ? "Creating account..." : "Sign Up"}
      </Button>

      {/* Continue with Google */}
      <Button
        type="button"
        variant="outline"
        className="w-full"
        disabled={registerMutation.isPending}
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
      <div className="text-center text-sm">
        Already have an account?{" "}
        <Link href="/login" className="text-primary hover:underline">
          Sign in
        </Link>
      </div>
    </form>
  )
}
