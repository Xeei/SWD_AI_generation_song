import { useQuery } from "@tanstack/react-query"
import axios from "axios"

export interface EnumChoice {
    value: number
    label: string
}

export interface EnumChoicesResponse {
    mood_tones: EnumChoice[]
    voice_types: EnumChoice[]
}

const instance = axios.create({
    baseURL: "http://localhost:8000/api",
})

export const enumKeys = {
    all: ["enums"] as const,
    choices: () => [...enumKeys.all, "choices"] as const,
}

export const getEnumChoices = (): Promise<EnumChoicesResponse> =>
    instance.get<EnumChoicesResponse>("/enums/").then((res) => res.data)

export const useEnumChoices = () =>
    useQuery({
        queryKey: enumKeys.choices(),
        queryFn: getEnumChoices,
    })
