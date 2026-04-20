import axios from 'axios'
import { useQuery, useMutation } from '@tanstack/react-query'
import { queryClient } from '@/lib/queryClient'

const instance = axios.create({
    baseURL: 'http://localhost:8000/api',
})

export const GenerationStatus = {
    GENERATING: 1,
    GENERATED: 2,
    ERROR: 3,
} as const

export interface SongResponse {
    song_id: string
    title: string
    occasion: string
    generation_status: number
    mood_tone: number
    voice_type: number
    duration: number
    audio_file_url: string
    share_url: string
    is_favorite: boolean
    time_stamp: string
}

export interface GenerateSongRequest {
    title: string
    occasion: string
    mood_tone: number
    voice_type: number
    duration: number
}

export const songKeys = {
    all: ['songs'] as const,
    detail: (id: string) => ['songs', id] as const,
}

export const generateSong = (data: GenerateSongRequest): Promise<SongResponse> =>
    instance
        .post<{ message: string; song: SongResponse }>('/songs/generate/', data)
        .then((res) => res.data.song)

export const getSongById = (songId: string): Promise<SongResponse> =>
    instance
        .get<{ song: SongResponse }>(`/songs/${songId}/`)
        .then((res) => res.data.song)

export const useGenerateSong = () =>
    useMutation({ mutationFn: generateSong })

export const useSongById = (songId: string | null) =>
    useQuery({
        queryKey: songKeys.detail(songId!),
        queryFn: () => getSongById(songId!),
        enabled: !!songId,
        refetchInterval: (query) => {
            const status = query.state.data?.generation_status
            return status === GenerationStatus.GENERATING ? 5000 : false
        },
    })

export const getSongs = (): Promise<SongResponse[]> =>
    instance
        .get<{ song_list: SongResponse[] }>('/songs/')
        .then((res) => res.data.song_list)

export const useSongs = () =>
    useQuery({
        queryKey: songKeys.all,
        queryFn: getSongs,
    })

export const updateSong = (
    songId: string,
    data: Partial<Pick<SongResponse, 'is_favorite' | 'title' | 'occasion'>>
): Promise<SongResponse> =>
    instance
        .put<{ song: SongResponse }>(`/songs/${songId}/update/`, data)
        .then((res) => res.data.song)

export const useUpdateSong = () =>
    useMutation({
        mutationFn: ({
            songId,
            data,
        }: {
            songId: string
            data: Partial<Pick<SongResponse, 'is_favorite' | 'title' | 'occasion'>>
        }) => updateSong(songId, data),
        onSuccess: () =>
            queryClient.invalidateQueries({ queryKey: songKeys.all }),
    })

export type RegeneratePayload = Pick<SongResponse, 'title' | 'occasion' | 'mood_tone' | 'voice_type' | 'duration'>

export const regenerateSong = (songId: string, data: RegeneratePayload): Promise<SongResponse> =>
    instance
        .post<{ song: SongResponse }>(`/songs/${songId}/regenerate/`, data)
        .then((res) => res.data.song)

export const useRegenerateSong = () =>
    useMutation({
        mutationFn: ({ songId, data }: { songId: string; data: RegeneratePayload }) =>
            regenerateSong(songId, data),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: songKeys.all }),
    })
