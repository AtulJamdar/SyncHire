"use client"

import { useEffect, useState } from "react"
import { useSearchParams } from "next/navigation"
import { useResetPassword } from "@/hooks/useResetPassword"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import Link from "next/link"

const validatePassword = (value: string): string | null => {
  if (!value) return "Password is required"
  if (value.length < 8) return "Password must be at least 8 characters"
  if (!/[a-zA-Z]/.test(value)) return "Password must contain at least one letter"
  if (!/[0-9]/.test(value)) return "Password must contain at least one number"
  return null
}

export function ResetPasswordForm() {
  const searchParams = useSearchParams()
  const token = searchParams.get("token")

  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [passwordError, setPasswordError] = useState("")
  const [confirmPasswordError, setConfirmPasswordError] = useState("")
  const [tokenError, setTokenError] = useState("")
  const [submitted, setSubmitted] = useState(false)

  const resetPasswordMutation = useResetPassword()

  useEffect(() => {
    if (!token) {
      setTokenError("Reset token is missing from the link.")
    }
  }, [token])

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setPassword(value)
    setPasswordError(validatePassword(value) || "")
    if (confirmPassword && value !== confirmPassword) {
      setConfirmPasswordError("Passwords do not match")
    } else if (confirmPassword) {
      setConfirmPasswordError("")
    }
  }

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

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()

    if (!token) {
      setTokenError("Reset token is missing from the link.")
      return
    }

    const passwordValidationError = validatePassword(password)
    if (passwordValidationError) {
      setPasswordError(passwordValidationError)
    }

    if (!confirmPassword) {
      setConfirmPasswordError("Please confirm your password")
    } else if (password !== confirmPassword) {
      setConfirmPasswordError("Passwords do not match")
    }

    if (passwordValidationError || !confirmPassword || password !== confirmPassword) {
      return
    }

    resetPasswordMutation.mutate(
      { token, password },
      {
        onSuccess: () => {
          setSubmitted(true)
        },
        onError: (error: any) => {
          const status = error?.response?.status
          if (status === 410) {
            setTokenError("This reset link has expired. Please request a new password reset.")
          } else if (status === 400) {
            setTokenError(error?.response?.data?.detail || "Reset token is invalid or expired.")
          } else {
            setTokenError("Unable to reset password. Please try again.")
          }
        },
      }
    )
  }

  if (tokenError && !token) {
    return (
      <div className="space-y-6 text-center">
        <div className="space-y-2">
          <div className="text-4xl mb-4">❌</div>
          <h2 className="text-xl font-semibold">Invalid reset link</h2>
          <p className="text-sm text-muted-foreground">The reset link is missing or malformed.</p>
        </div>
        <Link href="/forgot-password">
          <Button className="w-full">Request a new reset link</Button>
        </Link>
      </div>
    )
  }

  if (submitted) {
    return (
      <div className="space-y-6 text-center">
        <div className="space-y-2">
          <div className="text-4xl mb-4">✅</div>
          <h2 className="text-xl font-semibold">Password reset successful</h2>
          <p className="text-sm text-muted-foreground">
            You can now sign in with your new password.
          </p>
        </div>
        <Link href="/login">
          <Button className="w-full">Go to Sign In</Button>
        </Link>
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="password">New password</Label>
        <Input
          id="password"
          type="password"
          placeholder="Enter a new password"
          value={password}
          onChange={handlePasswordChange}
          disabled={resetPasswordMutation.isPending}
          className={passwordError ? "border-destructive" : ""}
          aria-describedby={passwordError ? "password-error" : undefined}
        />
        {passwordError && (
          <p id="password-error" className="text-sm text-destructive" role="alert" aria-live="polite">
            {passwordError}
          </p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="confirmPassword">Confirm password</Label>
        <Input
          id="confirmPassword"
          type="password"
          placeholder="Confirm your new password"
          value={confirmPassword}
          onChange={handleConfirmPasswordChange}
          disabled={resetPasswordMutation.isPending}
          className={confirmPasswordError ? "border-destructive" : ""}
          aria-describedby={confirmPasswordError ? "confirm-password-error" : undefined}
        />
        {confirmPasswordError && (
          <p id="confirm-password-error" className="text-sm text-destructive" role="alert" aria-live="polite">
            {confirmPasswordError}
          </p>
        )}
      </div>

      {tokenError && (
        <p className="text-sm text-destructive" role="alert" aria-live="polite">
          {tokenError}
        </p>
      )}

      <Button type="submit" className="w-full" disabled={resetPasswordMutation.isPending} aria-busy={resetPasswordMutation.isPending}>
        {resetPasswordMutation.isPending ? "Resetting password..." : "Reset password"}
      </Button>

      <div className="flex flex-col gap-2 text-center text-sm">
        <Link href="/login" className="text-primary hover:underline">
          Back to Sign In
        </Link>
        <Link href="/forgot-password" className="text-muted-foreground hover:text-foreground">
          Request a new reset link
        </Link>
      </div>
    </form>
  )
}
