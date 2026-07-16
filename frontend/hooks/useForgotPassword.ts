"use client"

import { useMutation } from "@tanstack/react-query"
import { api } from "@/lib/api"

interface ForgotPasswordRequest {
  email: string
}

export const useForgotPassword = () => {
  return useMutation({
    mutationFn: async (payload: ForgotPasswordRequest) => {
      const response = await api.auth.forgotPassword(payload.email)
      return response
    },
  })
}
