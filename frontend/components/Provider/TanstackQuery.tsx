"use client"
import { QueryClientProvider } from "@tanstack/react-query"
import React from "react"
import { queryClient } from "@/lib/queryClient"

interface Props {
    children: React.ReactNode
}

export default function TanstackQueryProvider({ children }: Props) {
    return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
}
