<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useGameStore } from '@/stores/game'
import { storeToRefs } from 'pinia'
import 'emoji-picker-element'

const game = useGameStore()
const { emojiClue, isNarrator, phase } = storeToRefs(game)

// ── Chip state ────────────────────────────────────────────────────────────────

const segmenter = new Intl.Segmenter()

function splitEmoji(str: string): string[] {
  return [...segmenter.segment(str)].map((s) => s.segment)
}

const chips = computed<string[]>(() => splitEmoji(emojiClue.value))

function removeChip(index: number) {
  const next = [...chips.value]
  next.splice(index, 1)
  emojiClue.value = next.join('')
}

// ── Recently used ─────────────────────────────────────────────────────────────

const RECENT_KEY = 'crocomoji_recent_emoji'
const MAX_RECENT = 24

const recentEmoji = ref<string[]>([])

onMounted(() => {
  try {
    recentEmoji.value = JSON.parse(localStorage.getItem(RECENT_KEY) ?? '[]')
  } catch {
    recentEmoji.value = []
  }
})

function recordUsed(emoji: string) {
  const list = [emoji, ...recentEmoji.value.filter((e) => e !== emoji)].slice(0, MAX_RECENT)
  recentEmoji.value = list
  localStorage.setItem(RECENT_KEY, JSON.stringify(list))
}

// ── Picker ────────────────────────────────────────────────────────────────────

const pickerOpen = ref(false)
const pickerRef = ref<HTMLElement | null>(null)
const toggleRef = ref<HTMLElement | null>(null)

function addEmoji(emoji: string) {
  emojiClue.value = emojiClue.value + emoji
  recordUsed(emoji)
}

function onPickerSelect(event: Event) {
  const e = event as CustomEvent<{ unicode: string }>
  addEmoji(e.detail.unicode)
}

function onClickOutside(event: MouseEvent) {
  if (
    pickerOpen.value &&
    pickerRef.value &&
    !pickerRef.value.contains(event.target as Node) &&
    !toggleRef.value?.contains(event.target as Node)
  ) {
    pickerOpen.value = false
  }
}

onMounted(() => document.addEventListener('mousedown', onClickOutside))
onBeforeUnmount(() => document.removeEventListener('mousedown', onClickOutside))

</script>

<template>
  <div class="px-6 py-4 border-t border-moss bg-linear-to-t from-murk to-transparent">

    <!-- Narrator: emoji clue builder -->
    <div v-if="isNarrator && phase === 'playing'" class="flex flex-col gap-3">

      <!-- Label -->
      <div class="flex items-center gap-2 text-[0.7rem] uppercase tracking-[0.15em] text-tooth-dim opacity-60 font-mono">
        <span class="text-base leading-none">&#x1F40A;</span>
        <span>Your emoji clue</span>
      </div>

      <!-- Chip display -->
      <div
        class="min-h-[3.5rem] flex flex-wrap items-center gap-1.5 bg-swamp border border-moss rounded-xl px-3 py-2 transition-colors duration-200 focus-within:border-amber-dim"
        :class="chips.length === 0 ? 'opacity-50' : ''"
      >
        <span
          v-for="(chip, i) in chips"
          :key="i"
          class="group relative flex items-center justify-center w-10 h-10 text-2xl rounded-lg bg-moss/50 hover:bg-leaf/40 transition-colors duration-150 cursor-pointer select-none"
          :title="'Remove ' + chip"
          @click="removeChip(i)"
        >
          {{ chip }}
          <span class="absolute inset-0 flex items-center justify-center rounded-lg bg-swamp/80 text-tooth text-[0.6rem] font-mono opacity-0 group-hover:opacity-100 transition-opacity duration-150">
            ✕
          </span>
        </span>

        <span v-if="chips.length === 0" class="text-sm text-tooth-dim opacity-40 font-mono px-1">
          Pick emoji below to build your clue…
        </span>
      </div>

      <!-- Recently used -->
      <div v-if="recentEmoji.length > 0" class="flex items-center gap-1.5 flex-wrap">
        <span class="text-[0.6rem] uppercase tracking-wider text-tooth-dim opacity-40 font-mono mr-1">Recent</span>
        <button
          v-for="emoji in recentEmoji.slice(0, 12)"
          :key="emoji"
          class="w-8 h-8 text-xl rounded-md hover:bg-moss/50 transition-colors duration-150 flex items-center justify-center"
          @click="addEmoji(emoji)"
        >
          {{ emoji }}
        </button>
      </div>

      <!-- Picker toggle + clear -->
      <div class="flex items-center gap-2">
        <button
          ref="toggleRef"
          class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[0.75rem] font-mono border transition-colors duration-150 cursor-pointer"
          :class="pickerOpen
            ? 'bg-amber/10 border-amber-dim/50 text-amber'
            : 'bg-moss/30 border-moss text-tooth-dim hover:bg-moss/60 hover:text-tooth'"
          @click="pickerOpen = !pickerOpen"
        >
          <span>🔍</span>
          <span>{{ pickerOpen ? 'Close picker' : 'Search emoji' }}</span>
        </button>

        <button
          v-if="chips.length > 0"
          class="px-3 py-1.5 rounded-lg text-[0.75rem] font-mono border border-moss/50 text-tooth-dim opacity-50 hover:opacity-100 hover:border-moss hover:text-tooth transition-all duration-150 cursor-pointer"
          @click="emojiClue = ''"
        >
          Clear
        </button>
      </div>

      <!-- Floating emoji picker -->
      <div
        v-if="pickerOpen"
        ref="pickerRef"
        class="relative z-10"
      >
        <emoji-picker
          class="w-full"
          @emoji-click="onPickerSelect"
        />
      </div>
    </div>

    <!-- Non-narrator: display the clue read-only -->
    <div v-else-if="phase === 'playing'" class="flex flex-col gap-2">
      <div class="flex items-center gap-2 text-[0.7rem] uppercase tracking-[0.15em] text-tooth-dim opacity-60 font-mono">
        <span>{{ game.narrator.avatar }} {{ game.narrator.name }}'s clue</span>
      </div>
      <div class="bg-swamp border border-moss rounded-xl px-4 py-3 text-3xl tracking-[0.2em] min-h-[3.5rem] flex items-center">
        <span v-if="emojiClue">{{ emojiClue }}</span>
        <span v-else class="text-sm text-tooth-dim opacity-30 tracking-normal">Waiting for emoji clue…</span>
      </div>
    </div>

  </div>
</template>
