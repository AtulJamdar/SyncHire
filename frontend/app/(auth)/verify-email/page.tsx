import { Metadata } from "next"
import { VerifyEmailForm } from "@/components/auth/VerifyEmailForm"

export const metadata: Metadata = {
  title: "Verify Email | Job Finder AI",
  description: "Verify your email address to complete registration",
}

export default function VerifyEmailPage() {
  return (
    <div className="space-y-6">
      <div className="space-y-2 text-center">
        <h1 className="text-2xl font-bold tracking-tight">Verify Your Email</h1>
        <p className="text-sm text-muted-foreground">
          We&apos;re verifying your email address
        </p>
      </div>

      <VerifyEmailForm />
    </div>
  )
}
