"use client"

import { useState } from "react"
import { Controller, useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Label, Select, Slider } from "radix-ui"
import { Input } from "@/components/ui/input"
import { useEnumChoices } from "@/services/enum.service"
import { useGenerateSong, useSongById, GenerationStatus } from "@/services/song.service"
import { useCreatorId } from "@/services/creator.service"

const schema = z.object({
    title: z
        .string()
        .min(1, "Title is required")
        .max(256, "Title must be at most 256 characters"),
    occasion: z.string().min(1, "Occasion is required"),
    duration: z.number().min(120).max(360),
    moodTone: z.string().min(1, "moodTone. is required"),
    voiceType: z.string().min(1, "voiceType is required"),
})

type FormValues = z.infer<typeof schema>

export default function GenerationPage() {
    const [songId, setSongId] = useState<string | null>(null)

    const {
        register,
        handleSubmit,
        control,
        watch,
        formState: { errors },
    } = useForm<FormValues>({
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        resolver: zodResolver(schema as any),
        defaultValues: {
            duration: 120,
        },
    })

    const creatorId = useCreatorId()
    const { data: enums } = useEnumChoices()
    const { mutate: generate, isPending, error: generateError } = useGenerateSong()
    const { data: song } = useSongById(songId)

    const duration = watch("duration")

    function onSubmit(data: FormValues) {
        if (!creatorId) return
        generate(
            {
                title: data.title,
                occasion: data.occasion,
                mood_tone: Number(data.moodTone),
                voice_type: Number(data.voiceType),
                duration: data.duration,
                creator_id: creatorId,
            },
            {
                onSuccess: (created) => setSongId(created.song_id),
            }
        )
    }

    const isGenerating =
        isPending || song?.generation_status === GenerationStatus.GENERATING
    const isGenerated = song?.generation_status === GenerationStatus.GENERATED
    const isError = song?.generation_status === GenerationStatus.ERROR

    return (
        <div className="flex min-h-screen items-center justify-center p-6">
            <div className="w-full max-w-lg">
                <h1 className="mb-6 text-2xl font-semibold">Generate Song</h1>

                <form
                    onSubmit={handleSubmit(onSubmit)}
                    className="flex flex-col gap-5"
                >
                    {/* Title */}
                    <div className="flex flex-col gap-1.5">
                        <Label.Root
                            htmlFor="title"
                            className="text-sm font-medium"
                        >
                            Title
                        </Label.Root>
                        <Input
                            id="title"
                            placeholder="Enter song title"
                            aria-invalid={!!errors.title}
                            {...register("title")}
                        />
                        {errors.title && (
                            <p className="text-xs text-destructive">
                                {errors.title.message}
                            </p>
                        )}
                    </div>

                    {/* Occasion */}
                    <div className="flex flex-col gap-1.5">
                        <Label.Root
                            htmlFor="occasion"
                            className="text-sm font-medium"
                        >
                            Occasion
                        </Label.Root>
                        <Input
                            id="occasion"
                            placeholder="e.g. Birthday, Wedding, Graduation"
                            aria-invalid={!!errors.occasion}
                            {...register("occasion")}
                        />
                        {errors.occasion && (
                            <p className="text-xs text-destructive">
                                {errors.occasion.message}
                            </p>
                        )}
                    </div>

                    {/* Duration */}
                    <div className="flex flex-col gap-3">
                        <div className="flex items-center justify-between">
                            <Label.Root className="text-sm font-medium">
                                Duration
                            </Label.Root>
                            <span className="text-sm text-muted-foreground tabular-nums">
                                {duration}s
                            </span>
                        </div>
                        <Controller
                            name="duration"
                            control={control}
                            render={({ field }) => (
                                <Slider.Root
                                    min={120}
                                    max={360}
                                    step={1}
                                    value={[field.value]}
                                    onValueChange={([val]) =>
                                        field.onChange(val)
                                    }
                                    className="relative flex h-5 w-full touch-none items-center select-none"
                                >
                                    <Slider.Track className="relative h-1.5 grow rounded-full bg-input">
                                        <Slider.Range className="absolute h-full rounded-full bg-primary" />
                                    </Slider.Track>
                                    <Slider.Thumb
                                        className="block h-4 w-4 rounded-full bg-primary shadow focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:outline-none disabled:pointer-events-none disabled:opacity-50"
                                        aria-label="Duration"
                                    />
                                </Slider.Root>
                            )}
                        />
                        <div className="flex justify-between text-xs text-muted-foreground">
                            <span>120s</span>
                            <span>360s</span>
                        </div>
                    </div>

                    {/* Mood Tone */}
                    <div className="flex flex-col gap-1.5">
                        <Label.Root className="text-sm font-medium">
                            Mood Tone
                        </Label.Root>
                        <Controller
                            name="moodTone"
                            control={control}
                            render={({ field }) => (
                                <Select.Root
                                    value={field.value}
                                    onValueChange={field.onChange}
                                >
                                    <Select.Trigger
                                        className="flex h-8 w-full items-center justify-between rounded-lg border border-input bg-transparent px-2.5 py-1 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 aria-invalid:border-destructive data-placeholder:text-muted-foreground"
                                        aria-invalid={!!errors.moodTone}
                                    >
                                        <Select.Value placeholder="Select mood tone" />
                                        <Select.Icon className="ml-2 text-muted-foreground">
                                            <svg
                                                width="12"
                                                height="12"
                                                viewBox="0 0 12 12"
                                                fill="none"
                                            >
                                                <path
                                                    d="M2 4l4 4 4-4"
                                                    stroke="currentColor"
                                                    strokeWidth="1.5"
                                                    strokeLinecap="round"
                                                    strokeLinejoin="round"
                                                />
                                            </svg>
                                        </Select.Icon>
                                    </Select.Trigger>
                                    <Select.Portal>
                                        <Select.Content
                                            className="z-50 min-w-32 overflow-hidden rounded-lg border border-border bg-popover text-popover-foreground shadow-md"
                                            position="popper"
                                            sideOffset={4}
                                        >
                                            <Select.Viewport className="p-1">
                                                {enums?.mood_tones.map(
                                                    ({ value, label }) => (
                                                        <Select.Item
                                                            key={value}
                                                            value={String(
                                                                value
                                                            )}
                                                            className="relative flex cursor-pointer items-center rounded-md px-2.5 py-1.5 text-sm outline-none select-none data-highlighted:bg-accent data-highlighted:text-accent-foreground"
                                                        >
                                                            <Select.ItemText>
                                                                {label}
                                                            </Select.ItemText>
                                                        </Select.Item>
                                                    )
                                                )}
                                            </Select.Viewport>
                                        </Select.Content>
                                    </Select.Portal>
                                </Select.Root>
                            )}
                        />
                        {errors.moodTone && (
                            <p className="text-xs text-destructive">
                                {errors.moodTone.message}
                            </p>
                        )}
                    </div>

                    {/* Voice Type */}
                    <div className="flex flex-col gap-1.5">
                        <Label.Root className="text-sm font-medium">
                            Voice Type
                        </Label.Root>
                        <Controller
                            name="voiceType"
                            control={control}
                            render={({ field }) => (
                                <Select.Root
                                    value={field.value}
                                    onValueChange={field.onChange}
                                >
                                    <Select.Trigger
                                        className="flex h-8 w-full items-center justify-between rounded-lg border border-input bg-transparent px-2.5 py-1 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 aria-invalid:border-destructive data-placeholder:text-muted-foreground"
                                        aria-invalid={!!errors.voiceType}
                                    >
                                        <Select.Value placeholder="Select voice type" />
                                        <Select.Icon className="ml-2 text-muted-foreground">
                                            <svg
                                                width="12"
                                                height="12"
                                                viewBox="0 0 12 12"
                                                fill="none"
                                            >
                                                <path
                                                    d="M2 4l4 4 4-4"
                                                    stroke="currentColor"
                                                    strokeWidth="1.5"
                                                    strokeLinecap="round"
                                                    strokeLinejoin="round"
                                                />
                                            </svg>
                                        </Select.Icon>
                                    </Select.Trigger>
                                    <Select.Portal>
                                        <Select.Content
                                            className="z-50 min-w-32 overflow-hidden rounded-lg border border-border bg-popover text-popover-foreground shadow-md"
                                            position="popper"
                                            sideOffset={4}
                                        >
                                            <Select.Viewport className="p-1">
                                                {enums?.voice_types.map(
                                                    ({ value, label }) => (
                                                        <Select.Item
                                                            key={value}
                                                            value={String(
                                                                value
                                                            )}
                                                            className="relative flex cursor-pointer items-center rounded-md px-2.5 py-1.5 text-sm outline-none select-none data-highlighted:bg-accent data-highlighted:text-accent-foreground"
                                                        >
                                                            <Select.ItemText>
                                                                {label}
                                                            </Select.ItemText>
                                                        </Select.Item>
                                                    )
                                                )}
                                            </Select.Viewport>
                                        </Select.Content>
                                    </Select.Portal>
                                </Select.Root>
                            )}
                        />
                        {errors.voiceType && (
                            <p className="text-xs text-destructive">
                                {errors.voiceType.message}
                            </p>
                        )}
                    </div>

                    <button
                        type="submit"
                        disabled={isGenerating}
                        className="mt-2 h-9 rounded-lg bg-primary px-4 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90 focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none disabled:pointer-events-none disabled:opacity-50"
                    >
                        {isGenerating ? "Generating..." : "Generate"}
                    </button>
                </form>

                {generateError && (
                    <p className="mt-4 text-sm text-destructive">
                        Failed to start generation. Please try again.
                    </p>
                )}

                {isGenerating && songId && (
                    <div className="mt-6 rounded-lg border border-border p-4 text-sm text-muted-foreground">
                        Generating your song — this may take 1–2 minutes...
                    </div>
                )}

                {isError && (
                    <div className="mt-6 rounded-lg border border-destructive/50 bg-destructive/10 p-4 text-sm text-destructive">
                        Generation failed. Please try again.
                    </div>
                )}

                {isGenerated && song && (
                    <div className="mt-6 flex flex-col gap-3 rounded-lg border border-border p-4">
                        <p className="font-medium">{song.title}</p>
                        {song.audio_file_url && (
                            <audio controls src={song.audio_file_url} className="w-full" />
                        )}
                        {song.share_url && (
                            <a
                                href={song.share_url}
                                target="_blank"
                                rel="noreferrer"
                                className="text-xs text-primary underline underline-offset-2"
                            >
                                Open source audio
                            </a>
                        )}
                    </div>
                )}
            </div>
        </div>
    )
}
