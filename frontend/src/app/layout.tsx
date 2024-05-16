import NavBar from "@/components/navbar"
import { ThemeProvider } from "@/components/theme-provider"
import { Toaster } from "@/components/ui/toaster"
import { AuthProvider } from "@/contexts/auth"
import type { Metadata } from "next"
import { Inter } from "next/font/google"

import { ChartJsProvider } from "@/contexts/chartjs"
import { Suspense } from "react"
import "./globals.css"
import Providers from "./providers"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "CantinaCF",
  description: "Cantina Escolar",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="pt-br">
      <head>
        <link rel="icon" href="/img/fantastico.ico" />
      </head>
      <body className={inter.className} suppressHydrationWarning={true}>
        <Providers>
          <ThemeProvider
            attribute="class"
            defaultTheme="system"
            enableSystem
            disableTransitionOnChange
          >
            <ChartJsProvider>
              <AuthProvider>
                <NavBar />
                <Suspense fallback={null}>
                  <Toaster />
                </Suspense>
                {children}
              </AuthProvider>
            </ChartJsProvider>
          </ThemeProvider>
        </Providers>
      </body>
    </html>
  )
}
