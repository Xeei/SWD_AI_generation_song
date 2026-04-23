"use client"

import { useSession, signIn, signOut } from "next-auth/react"

export default function AuthButton() {
    const { data: session, status } = useSession()

    if (status === "loading") {
        return <div className="h-9 w-full animate-pulse rounded-lg bg-muted" />
    }

    if (!session) {
        return (
            <button
                onClick={() => signIn("google", { callbackUrl: "/" })}
                className="flex w-full items-center justify-center gap-2 rounded-lg border border-input px-3 py-2 text-sm font-medium hover:bg-accent"
            >
                Sign in with Google
            </button>
        )
    }

    return (
        <div className="flex items-center gap-3">
            {session.user?.image && (
                <img
                    src={session.user.image}
                    alt={session.user.name ?? "User"}
                    className="h-8 w-8 rounded-full"
                />
            )}
            <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium">{session.user?.name}</p>
                <p className="truncate text-xs text-muted-foreground">{session.user?.email}</p>
            </div>
            <button
                onClick={() => signOut({ callbackUrl: "/login" })}
                className="shrink-0 rounded-md px-2 py-1 text-xs text-muted-foreground hover:bg-accent hover:text-foreground"
            >
                Sign out
            </button>
        </div>
    )
}
