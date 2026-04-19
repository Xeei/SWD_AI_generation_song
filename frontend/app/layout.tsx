import { Geist_Mono, Inter } from "next/font/google"

import "./globals.css"
import { ThemeProvider } from "@/components/theme-provider"
import { cn } from "@/lib/utils"
import { SidebarProvider } from "@/components/ui/sidebar"
import { AppSidebar } from "@/components/AppSidebar"
import TanstackQueryProvider from "@/components/Provider/TanstackQuery"
import SessionProvider from "@/components/Provider/SessionProvider"

const inter = Inter({ subsets: ["latin"], variable: "--font-sans" })

const fontMono = Geist_Mono({
    subsets: ["latin"],
    variable: "--font-mono",
})

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode
}>) {
    return (
        <html
            lang="en"
            suppressHydrationWarning
            className={cn(
                "antialiased",
                fontMono.variable,
                "font-sans",
                inter.variable
            )}
        >
            <body>
                <SessionProvider>
                    <TanstackQueryProvider>
                        <ThemeProvider>
                            <SidebarProvider>
                                <AppSidebar />
                                <main className="flex-1">{children}</main>
                            </SidebarProvider>
                        </ThemeProvider>
                    </TanstackQueryProvider>
                </SessionProvider>
            </body>
        </html>
    )
}
