import axios from 'axios'
import { useQuery } from '@tanstack/react-query'
import { useSession } from 'next-auth/react'

const instance = axios.create({
    baseURL: 'http://localhost:8000/api',
})

export interface CreatorResponse {
    creator_id: string
    email: string
}

export const syncCreator = (email: string): Promise<CreatorResponse> =>
    instance
        .post<{ creator: CreatorResponse }>('/creators/sync/', { email })
        .then((res) => res.data.creator)

export const useCreatorId = () => {
    const { data: session } = useSession()
    const email = session?.user?.email ?? null

    const query = useQuery({
        queryKey: ['creator', email],
        queryFn: () => syncCreator(email!),
        enabled: !!email,
        staleTime: Infinity,
    })

    return query.data?.creator_id ?? null
}
