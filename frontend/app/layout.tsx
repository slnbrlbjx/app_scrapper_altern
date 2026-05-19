import type { Metadata } from "next"
import "./globals.css"

export const metadata: Metadata = {
  title: "Alternance Cyber",
  description: "Agrégateur d'offres alternance cybersécurité",
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr">
      <body>{children}</body>
    </html>
  )
}
