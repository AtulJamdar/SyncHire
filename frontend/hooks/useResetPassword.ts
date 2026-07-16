"use client"

import { useMutation } from "@tanstack/react-query"
import { api } from "@/lib/api"

interface ResetPasswordRequest {
  token: string
  password: string
}

export const useResetPassword = () => {
  return useMutation({
    mutationFn: async (payload: ResetPasswordRequest) => {
      const response = await api.auth.resetPassword(payload.token, payload.password)
      return response
    },
  })
}
