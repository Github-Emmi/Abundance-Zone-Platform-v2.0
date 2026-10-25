import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

// Middleware in Next.js cannot access localStorage (client-side only)
// So we'll skip server-side auth checks and handle protection on client-side
// This middleware now only handles static redirects

export function middleware(request: NextRequest) {
  // Let all routes through - auth protection is handled client-side
  return NextResponse.next()
}

export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public files (public folder)
     */
    "/((?!api|_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
}
