import { Metadata } from "next"
import { ForgotPasswordForm } from "@/components/auth/ForgotPasswordForm"

export const metadata: Metadata = {
  title: "Forgot Password | Job Finder AI",
  description: "Request a password reset link for your Job Finder AI account",
}

export default function ForgotPasswordPage() {
  return (
    <div className="space-y-6">
      <div className="space-y-2 text-center">
        <h1 className="text-2xl font-bold tracking-tight">Forgot your password?</h1>
        <p className="text-sm text-muted-foreground">
          Enter your email and we&apos;ll send a secure password reset link.
        </p>
      </div>
      <ForgotPasswordForm />
    </div>
  )
}
