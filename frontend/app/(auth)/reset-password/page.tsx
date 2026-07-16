import { Metadata } from "next"
import { ResetPasswordForm } from "@/components/auth/ResetPasswordForm"

export const metadata: Metadata = {
  title: "Reset Password | Job Finder AI",
  description: "Reset your Job Finder AI password using the link sent to your email",
}

export default function ResetPasswordPage() {
  return (
    <div className="space-y-6">
      <div className="space-y-2 text-center">
        <h1 className="text-2xl font-bold tracking-tight">Reset your password</h1>
        <p className="text-sm text-muted-foreground">
          Use the link from your email to choose a new password.
        </p>
      </div>
      <ResetPasswordForm />
    </div>
  )
}
