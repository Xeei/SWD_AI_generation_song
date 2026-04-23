"use client"
import {
    Sidebar,
    SidebarContent,
    SidebarFooter,
    SidebarGroup,
    SidebarGroupLabel,
    SidebarHeader,
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
} from "@/components/ui/sidebar"
import { Disc, Library, ListMusic, Music } from "lucide-react"
import AuthButton from "@/components/AuthButton"
import Link from "next/link"

const menuItems = [
    { title: "Generation", icon: Music, href: "/generation" },
    { title: "Library", icon: Library, href: "/library" },
    { title: "Playlists", icon: ListMusic, href: "/playlists" },
]

export function AppSidebar() {
    return (
        <Sidebar>
            <SidebarHeader>
                <SidebarMenu>
                    <SidebarMenuItem>
                        <SidebarMenuButton>
                            <Link
                                href={"/"}
                                className="flex h-auto items-center gap-3 py-3"
                            >
                                <Disc size={72} />
                                <span className="text-lg font-bold">
                                    SongGen
                                </span>
                            </Link>
                        </SidebarMenuButton>
                    </SidebarMenuItem>
                </SidebarMenu>
            </SidebarHeader>
            <SidebarContent>
                <SidebarGroup>
                    <SidebarGroupLabel>Menu</SidebarGroupLabel>
                    <SidebarMenu>
                        {menuItems.map((item) => (
                            <SidebarMenuItem key={item.title}>
                                <SidebarMenuButton asChild>
                                    <Link href={item.href}>
                                        <item.icon />
                                        <span>{item.title}</span>
                                    </Link>
                                </SidebarMenuButton>
                            </SidebarMenuItem>
                        ))}
                    </SidebarMenu>
                </SidebarGroup>
            </SidebarContent>
            <SidebarFooter className="p-3">
                <AuthButton />
            </SidebarFooter>
        </Sidebar>
    )
}
