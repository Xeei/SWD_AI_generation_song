import { SongResponse, GenerationStatus } from '@/services/song.service'

const MOOD_LABEL: Record<number, string> = {
    1: 'Happy',
    2: 'Sad',
    3: 'Upbeat',
    4: 'Romantic',
    5: 'Chill',
    6: 'Epic',
}

const MOOD_CLASS: Record<number, string> = {
    1: 'bg-yellow-500/20 text-yellow-300',
    2: 'bg-blue-500/20 text-blue-300',
    3: 'bg-green-500/20 text-green-300',
    4: 'bg-pink-500/20 text-pink-300',
    5: 'bg-cyan-500/20 text-cyan-300',
    6: 'bg-orange-500/20 text-orange-300',
}

function formatDuration(seconds: number): string {
    const m = Math.floor(seconds / 60)
    const s = seconds % 60
    return `${m}:${String(s).padStart(2, '0')}`
}

interface Props {
    songs: SongResponse[]
    currentSongId: string | null
    onPlay: (song: SongResponse) => void
    onFavorite: (song: SongResponse) => void
}

export default function SongList({ songs, currentSongId, onPlay, onFavorite }: Props) {
    if (songs.length === 0) {
        return (
            <div className="flex min-h-40 items-center justify-center text-sm text-muted-foreground">
                No songs found
            </div>
        )
    }

    return (
        <div className="flex flex-col gap-1">
            {/* Header */}
            <div className="grid grid-cols-[32px_1fr_100px_60px_90px_32px] gap-3 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                <span />
                <span>Title</span>
                <span>Mood</span>
                <span>Duration</span>
                <span>Status</span>
                <span />
            </div>

            {/* Rows */}
            {songs.map((song) => {
                const isPlaying = song.song_id === currentSongId
                const isPlayable = song.generation_status === GenerationStatus.GENERATED
                const statusLabel =
                    song.generation_status === GenerationStatus.GENERATED
                        ? 'Generated'
                        : song.generation_status === GenerationStatus.GENERATING
                          ? 'Generating'
                          : 'Error'
                const statusClass =
                    song.generation_status === GenerationStatus.GENERATED
                        ? 'bg-green-500/20 text-green-400'
                        : song.generation_status === GenerationStatus.GENERATING
                          ? 'bg-amber-500/20 text-amber-400'
                          : 'bg-red-500/20 text-red-400'

                return (
                    <div
                        key={song.song_id}
                        className={[
                            'grid grid-cols-[32px_1fr_100px_60px_90px_32px] gap-3 items-center rounded-lg border px-3 py-2 transition-colors',
                            isPlaying
                                ? 'border-primary bg-primary/10'
                                : 'border-border bg-card',
                            !isPlayable && 'opacity-50',
                        ]
                            .filter(Boolean)
                            .join(' ')}
                    >
                        <button
                            onClick={() => isPlayable && onPlay(song)}
                            disabled={!isPlayable}
                            className="flex items-center justify-center text-primary disabled:cursor-not-allowed disabled:text-muted-foreground"
                            aria-label={isPlaying ? 'Pause' : 'Play'}
                        >
                            {isPlaying ? '⏸' : '▶'}
                        </button>

                        <div className="min-w-0">
                            <div className="truncate text-sm font-semibold">{song.title}</div>
                            <div className="truncate text-xs text-muted-foreground">
                                {song.occasion}
                            </div>
                        </div>

                        <span
                            className={`w-fit rounded-full px-2 py-0.5 text-xs ${MOOD_CLASS[song.mood_tone] ?? 'bg-muted text-muted-foreground'}`}
                        >
                            {MOOD_LABEL[song.mood_tone] ?? '—'}
                        </span>

                        <span className="text-xs text-muted-foreground">
                            {isPlayable ? formatDuration(song.duration) : '—'}
                        </span>

                        <span className={`w-fit rounded-full px-2 py-0.5 text-xs ${statusClass}`}>
                            {statusLabel}
                        </span>

                        <button
                            onClick={() => onFavorite(song)}
                            className={
                                song.is_favorite
                                    ? 'text-amber-400'
                                    : 'text-muted-foreground hover:text-amber-400'
                            }
                            aria-label={song.is_favorite ? 'Unfavorite' : 'Favorite'}
                        >
                            {song.is_favorite ? '♥' : '♡'}
                        </button>
                    </div>
                )
            })}
        </div>
    )
}
