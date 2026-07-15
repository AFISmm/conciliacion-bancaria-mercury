import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// Optimistic check only (cookie presence, not DB validity) — the real,
// secure check happens in lib/auth/dal.ts's verifySession() on every
// server-rendered page/action. See Next.js authentication guide.
const PUBLIC_ROUTES = ["/login", "/register", "/verify"];

export function proxy(req: NextRequest) {
  const { pathname } = req.nextUrl;
  const hasSession = Boolean(req.cookies.get("session")?.value);
  const isPublicRoute = PUBLIC_ROUTES.includes(pathname);

  if (!isPublicRoute && !hasSession) {
    return NextResponse.redirect(new URL("/login", req.url));
  }
  if (isPublicRoute && hasSession) {
    return NextResponse.redirect(new URL("/", req.url));
  }
  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
