import { useMutation } from "@tanstack/react-query"
import { api } from "@/lib/api"
import { setAccessToken } from "@/lib/auth"

interface RegisterRequest {
  name: string
  email: string
  password: string
}

interface RegisterResponse {
  access_token: string
  token_type: string
}

export function useRegister() {
  return useMutation({
    mutationFn: async (credentials: RegisterRequest) => {
      const response = await api.auth.register(
        credentials.email,
        credentials.password
      )
      // Store access token in memory (though user is not yet verified)
      setAccessToken(response.access_token)
      return response
    },
  })
}
