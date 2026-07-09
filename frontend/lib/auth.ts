// In-memory storage for JWT access token to protect against XSS attacks.
let accessToken: string | null = null

export const getAccessToken = () => accessToken

export const setAccessToken = (token: string) => {
  accessToken = token
}

export const clearAccessToken = () => {
  accessToken = null
}
