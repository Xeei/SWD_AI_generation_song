import axios from 'axios'
import { useMutation, useQuery } from '@tanstack/react-query'
import { queryClient } from '@/lib/queryClient'
import { SongResponse } from './song.service'

const instance = axios.create({
    baseURL: 'http://localhost:8000/api',
})

export interface PlaylistResponse {
    playlist_id: string
    name: string
    create_at: string
    song_count: number
    songs: SongResponse[]
}

export const playlistKeys = {
    all: ['playlists'] as const,
    byCreator: (creatorId: string) => ['playlists', creatorId] as const,
    detail: (id: string) => ['playlists', 'detail', id] as const,
}

export const getPlaylists = (creatorId: string): Promise<PlaylistResponse[]> =>
    instance
        .get<{ playlist_list: PlaylistResponse[] }>('/playlists/', { params: { creator_id: creatorId } })
        .then((res) => res.data.playlist_list)

export const getPlaylist = (playlistId: string): Promise<PlaylistResponse> =>
    instance
        .get<{ playlist: PlaylistResponse }>(`/playlists/${playlistId}/`)
        .then((res) => res.data.playlist)

export const createPlaylist = (name: string, creatorId: string): Promise<PlaylistResponse> =>
    instance
        .post<{ playlist: PlaylistResponse }>('/playlists/create/', { name, creator_id: creatorId })
        .then((res) => res.data.playlist)

export const updatePlaylist = (playlistId: string, name: string): Promise<PlaylistResponse> =>
    instance
        .put<{ playlist: PlaylistResponse }>(`/playlists/${playlistId}/update/`, { name })
        .then((res) => res.data.playlist)

export const deletePlaylist = (playlistId: string): Promise<void> =>
    instance.delete(`/playlists/${playlistId}/delete/`).then(() => undefined)

export const addSongToPlaylist = (playlistId: string, songId: string): Promise<PlaylistResponse> =>
    instance
        .post<{ playlist: PlaylistResponse }>(`/playlists/${playlistId}/songs/${songId}/`)
        .then((res) => res.data.playlist)

export const removeSongFromPlaylist = (playlistId: string, songId: string): Promise<PlaylistResponse> =>
    instance
        .delete<{ playlist: PlaylistResponse }>(`/playlists/${playlistId}/songs/${songId}/`)
        .then((res) => res.data.playlist)

export const usePlaylists = (creatorId: string | null) =>
    useQuery({
        queryKey: playlistKeys.byCreator(creatorId!),
        queryFn: () => getPlaylists(creatorId!),
        enabled: !!creatorId,
    })

export const usePlaylist = (playlistId: string | null) =>
    useQuery({
        queryKey: playlistKeys.detail(playlistId!),
        queryFn: () => getPlaylist(playlistId!),
        enabled: !!playlistId,
    })

export const useCreatePlaylist = () =>
    useMutation({
        mutationFn: ({ name, creatorId }: { name: string; creatorId: string }) =>
            createPlaylist(name, creatorId),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: playlistKeys.all }),
    })

export const useUpdatePlaylist = () =>
    useMutation({
        mutationFn: ({ playlistId, name }: { playlistId: string; name: string }) =>
            updatePlaylist(playlistId, name),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: playlistKeys.all }),
    })

export const useDeletePlaylist = () =>
    useMutation({
        mutationFn: (playlistId: string) => deletePlaylist(playlistId),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: playlistKeys.all }),
    })

export const useAddSongToPlaylist = () =>
    useMutation({
        mutationFn: ({ playlistId, songId }: { playlistId: string; songId: string }) =>
            addSongToPlaylist(playlistId, songId),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: playlistKeys.all }),
    })

export const useRemoveSongFromPlaylist = () =>
    useMutation({
        mutationFn: ({ playlistId, songId }: { playlistId: string; songId: string }) =>
            removeSongFromPlaylist(playlistId, songId),
        onSuccess: (_data, { playlistId }) =>
            queryClient.invalidateQueries({ queryKey: playlistKeys.detail(playlistId) }),
    })
