"use client"

import { useMutation } from "@tanstack/react-query"
import { api } from "@/lib/api"

export interface VerifyEmailResponse {
  message: string
}

export const useVerifyEmail = () => {
  return useMutation({
    mutationFn: async (token: string) => {
      const response = await api.auth.verifyEmail(token)
      return response
    },
  })
}
