import { redirect } from "next/navigation"

export default function HomePage() {
  // Root redirects to login by default
  redirect("/login")
}
