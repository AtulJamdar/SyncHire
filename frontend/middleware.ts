import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

const PUBLIC_PATHS = ["/login", "/register", "/verify-email", "/unsubscribe"]

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  const hasRefreshToken = request.cookies.has("refresh_token")

  // Public paths — allow unauthenticated
  if (PUBLIC_PATHS.some((p) => pathname.startsWith(p))) {
    if (hasRefreshToken) {
      // Already logged in → redirect to jobs feed
      return NextResponse.redirect(new URL("/jobs", request.url))
    }
    return NextResponse.next()
  }

  // All other private paths require refresh token presence
  if (!hasRefreshToken) {
    // Redirect to login with original URL as next parameter
    const loginUrl = new URL("/login", request.url)
    loginUrl.searchParams.set("next", pathname)
    return NextResponse.redirect(loginUrl)
  }

  return NextResponse.next()
}

// Matching paths — protect everything except static files, public API, and image assets
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes, backend handles auth)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - company-logos (uploaded logo assets)
     */
    "/((?!api|_next/static|_next/image|favicon.ico|company-logos|.*\\..*).*)",
  ],
}
