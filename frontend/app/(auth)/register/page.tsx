import { Metadata } from "next"
import { RegisterForm } from "@/components/auth/RegisterForm"

export const metadata: Metadata = {
  title: "Sign Up | Job Finder AI",
  description: "Create a new Job Finder AI account",
}

export default function RegisterPage() {
  return (
    <div className="space-y-6">
      <div className="space-y-2 text-center">
        <h1 className="text-2xl font-bold tracking-tight">Create your account</h1>
        <p className="text-sm text-muted-foreground">
          Join thousands of students finding matched jobs
        </p>
      </div>

      <RegisterForm />
    </div>
  )
}
