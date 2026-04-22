"use client"

import { useEffect, useState } from 'react'
import { SongResponse, RegeneratePayload, useRegenerateSong } from '@/services/song.service'
import { useCreatorId } from '@/services/creator.service'

const MOOD_OPTIONS = [
    { value: 1, label: 'Happy' },
    { value: 2, label: 'Sad' },
    { value: 3, label: 'Upbeat' },
    { value: 4, label: 'Romantic' },
    { value: 5, label: 'Chill' },
    { value: 6, label: 'Epic' },
]

const VOICE_OPTIONS = [
    { value: 1, label: 'Male' },
    { value: 2, label: 'Female' },
]

function formatDuration(seconds: number): string {
    const m = Math.floor(seconds / 60)
    const s = seconds % 60
    return `${m}:${String(s).padStart(2, '0')}`
}

interface Props {
    song: SongResponse | null
    onClose: () => void
}

export default function RegenerateModal({ song, onClose }: Props) {
    const { mutate: regenerate, isPending } = useRegenerateSong()
    const creatorId = useCreatorId()
    const [error, setError] = useState<string | null>(null)

    const [form, setForm] = useState<RegeneratePayload>({
        title: '',
        occasion: '',
        mood_tone: 1,
        voice_type: 1,
        duration: 120,
    })

    useEffect(() => {
        if (song) {
            setError(null)
            setForm({
                title: song.title,
                occasion: song.occasion,
                mood_tone: song.mood_tone,
                voice_type: song.voice_type,
                duration: song.duration,
            })
        }
    }, [song?.song_id])

    if (!song) return null

    function handleSubmit(e: React.FormEvent) {
        e.preventDefault()
        if (!creatorId) return
        setError(null)
        regenerate(
            { songId: song!.song_id, data: { ...form, creator_id: creatorId } },
            {
                onSuccess: onClose,
                onError: () => setError('Regeneration failed. Please try again.'),
            }
        )
    }

    const selectClass = "h-8 w-full rounded-lg border border-input bg-transparent px-2.5 text-sm outline-none focus-visible:border-ring"
    const inputClass = "h-8 w-full rounded-lg border border-input bg-transparent px-2.5 text-sm outline-none focus-visible:border-ring"
    const labelClass = "mb-1 block text-xs font-medium text-muted-foreground"
    const readValueClass = "text-sm"

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
            <div className="w-full max-w-2xl rounded-xl border border-border bg-card p-6 shadow-xl">
                <h2 className="mb-4 text-lg font-semibold">Regenerate Song</h2>

                <form onSubmit={handleSubmit}>
                    <div className="grid grid-cols-2 gap-6">
                        {/* Left: current values */}
                        <div>
                            <h3 className="mb-3 text-sm font-semibold text-muted-foreground uppercase tracking-wide">Current</h3>
                            <div className="flex flex-col gap-3">
                                <div>
                                    <div className={labelClass}>Title</div>
                                    <div className={readValueClass}>{song.title}</div>
                                </div>
                                <div>
                                    <div className={labelClass}>Occasion</div>
                                    <div className={readValueClass}>{song.occasion}</div>
                                </div>
                                <div>
                                    <div className={labelClass}>Mood</div>
                                    <div className={readValueClass}>
                                        {MOOD_OPTIONS.find((o) => o.value === song.mood_tone)?.label ?? '—'}
                                    </div>
                                </div>
                                <div>
                                    <div className={labelClass}>Voice</div>
                                    <div className={readValueClass}>
                                        {VOICE_OPTIONS.find((o) => o.value === song.voice_type)?.label ?? '—'}
                                    </div>
                                </div>
                                <div>
                                    <div className={labelClass}>Duration</div>
                                    <div className={readValueClass}>{formatDuration(song.duration)}</div>
                                </div>
                            </div>
                        </div>

                        {/* Right: editable form */}
                        <div>
                            <h3 className="mb-3 text-sm font-semibold text-muted-foreground uppercase tracking-wide">New</h3>
                            <div className="flex flex-col gap-3">
                                <div>
                                    <label className={labelClass}>Title</label>
                                    <input
                                        className={inputClass}
                                        value={form.title}
                                        onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
                                        required
                                    />
                                </div>
                                <div>
                                    <label className={labelClass}>Occasion</label>
                                    <input
                                        className={inputClass}
                                        value={form.occasion}
                                        onChange={(e) => setForm((f) => ({ ...f, occasion: e.target.value }))}
                                        required
                                    />
                                </div>
                                <div>
                                    <label className={labelClass}>Mood</label>
                                    <select
                                        className={selectClass}
                                        value={form.mood_tone}
                                        onChange={(e) => setForm((f) => ({ ...f, mood_tone: Number(e.target.value) }))}
                                    >
                                        {MOOD_OPTIONS.map((o) => (
                                            <option key={o.value} value={o.value}>{o.label}</option>
                                        ))}
                                    </select>
                                </div>
                                <div>
                                    <label className={labelClass}>Voice</label>
                                    <select
                                        className={selectClass}
                                        value={form.voice_type}
                                        onChange={(e) => setForm((f) => ({ ...f, voice_type: Number(e.target.value) }))}
                                    >
                                        {VOICE_OPTIONS.map((o) => (
                                            <option key={o.value} value={o.value}>{o.label}</option>
                                        ))}
                                    </select>
                                </div>
                                <div>
                                    <label className={labelClass}>Duration — {formatDuration(form.duration)}</label>
                                    <input
                                        type="range"
                                        min={120}
                                        max={360}
                                        step={10}
                                        value={form.duration}
                                        onChange={(e) => setForm((f) => ({ ...f, duration: Number(e.target.value) }))}
                                        className="w-full accent-primary"
                                    />
                                </div>
                            </div>
                        </div>
                    </div>

                    {error && (
                        <p className="mt-4 text-sm text-red-400">{error}</p>
                    )}

                    {/* Footer */}
                    <div className="mt-6 flex justify-end gap-2">
                        <button
                            type="button"
                            onClick={onClose}
                            className="h-8 rounded-lg border border-input px-4 text-sm text-muted-foreground hover:text-foreground"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={isPending}
                            className="h-8 rounded-lg bg-primary px-4 text-sm font-medium text-primary-foreground disabled:opacity-50"
                        >
                            {isPending ? 'Regenerating…' : 'Regenerate'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    )
}
