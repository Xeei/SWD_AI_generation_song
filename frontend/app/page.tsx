import Link from 'next/link'
import { Disc, Music, Library, ListMusic, Sparkles } from 'lucide-react'

const features = [
    {
        icon: Music,
        title: 'AI Song Generation',
        description: 'Describe your occasion, pick a mood and voice — get a unique song in minutes.',
    },
    {
        icon: Library,
        title: 'Personal Library',
        description: 'All your generated songs in one place. Filter, favourite, and replay anytime.',
    },
    {
        icon: ListMusic,
        title: 'Playlists',
        description: 'Organize songs into playlists for every event and mood.',
    },
]

export default function LandingPage() {
    return (
        <div className="flex min-h-screen flex-col">
            {/* Hero */}
            <section className="flex flex-1 flex-col items-center justify-center gap-8 px-6 py-24 text-center">
                <div className="flex items-center justify-center rounded-2xl bg-primary/10 p-5">
                    <Disc size={56} className="text-primary" />
                </div>

                <div className="flex flex-col gap-3">
                    <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
                        Create songs with AI
                    </h1>
                    <p className="mx-auto max-w-md text-base text-muted-foreground sm:text-lg">
                        SongGen turns your ideas into real music. Pick an occasion, a mood, a voice — and let AI do the rest.
                    </p>
                </div>

                <div className="flex flex-wrap items-center justify-center gap-3">
                    <Link
                        href="/generation"
                        className="inline-flex items-center gap-2 rounded-lg bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground transition-colors hover:bg-primary/90"
                    >
                        <Sparkles size={16} />
                        Generate a song
                    </Link>
                    <Link
                        href="/library"
                        className="inline-flex items-center gap-2 rounded-lg border border-input px-5 py-2.5 text-sm font-semibold transition-colors hover:bg-accent hover:text-accent-foreground"
                    >
                        <Library size={16} />
                        My Library
                    </Link>
                </div>
            </section>

            {/* Features */}
            <section className="border-t px-6 py-16">
                <div className="mx-auto grid max-w-3xl gap-8 sm:grid-cols-3">
                    {features.map(({ icon: Icon, title, description }) => (
                        <div key={title} className="flex flex-col gap-3">
                            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                                <Icon size={20} className="text-primary" />
                            </div>
                            <div>
                                <h3 className="font-semibold">{title}</h3>
                                <p className="mt-1 text-sm text-muted-foreground">{description}</p>
                            </div>
                        </div>
                    ))}
                </div>
            </section>
        </div>
    )
}
