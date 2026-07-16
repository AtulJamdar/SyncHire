import { useMutation } from "@tanstack/react-query"
import { api } from "@/lib/api"
import { setAccessToken } from "@/lib/auth"

interface LoginRequest {
  email: string
  password: string
}

interface LoginResponse {
  access_token: string
  token_type: string
}

export function useLogin() {
  return useMutation({
    mutationFn: async (credentials: LoginRequest) => {
      const response = await api.auth.login(credentials.email, credentials.password)
      // Store access token in memory
      setAccessToken(response.access_token)
      return response
    },
  })
}
