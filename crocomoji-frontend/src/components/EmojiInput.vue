<script setup lang="ts">
import { useGameStore } from '@/stores/game'
import { storeToRefs } from 'pinia'

const game = useGameStore()
const { emojiClue, isNarrator, phase } = storeToRefs(game)

function filterToEmoji(event: Event) {
  const input = event.target as HTMLInputElement
  const emojiOnly = input.value.replace(
    /[^\p{Emoji_Presentation}\p{Extended_Pictographic}\s]/gu,
    '',
  )
  emojiClue.value = emojiOnly
}
</script>

<template>
  <div class="px-6 py-4 border-t border-moss bg-linear-to-t from-murk to-transparent">
    <!-- Narrator: editable emoji input -->
    <div v-if="isNarrator && phase === 'playing'" class="flex flex-col gap-2">
      <div
        class="flex items-center gap-2 text-[0.7rem] uppercase tracking-[0.15em] text-tooth-dim opacity-60 font-mono"
      >
        <span class="text-base leading-none">&#x1F40A;</span>
        <span>Type your emoji clue</span>
      </div>
      <div
        class="flex items-center gap-3 bg-swamp border border-moss rounded-xl px-3 py-2 transition-all duration-300 focus-within:border-amber-dim focus-within:shadow-[0_0_0_3px_rgba(212,160,74,0.08),inset_0_1px_4px_rgba(0,0,0,0.2)]"
      >
        <input
          :value="emojiClue"
          type="text"
          class="flex-1 bg-transparent border-none outline-none text-tooth text-3xl tracking-[0.15em] font-[system-ui,sans-serif] leading-relaxed placeholder:opacity-25 placeholder:tracking-[0.3em] placeholder:text-xl"
          placeholder="Describe the sentence with emoji..."
          @input="filterToEmoji"
          spellcheck="false"
          autocomplete="off"
        />
      </div>
    </div>

    <!-- Non-narrator: just display the emoji clue -->
    <div v-else-if="phase === 'playing'" class="flex flex-col gap-2">
      <div
        class="flex items-center gap-2 text-[0.7rem] uppercase tracking-[0.15em] text-tooth-dim opacity-60 font-mono"
      >
        <span>{{ game.narrator.avatar }} {{ game.narrator.name }}'s clue</span>
      </div>
      <div
        class="bg-swamp border border-moss rounded-xl px-4 py-3 text-3xl tracking-[0.2em] min-h-[3.5rem] flex items-center"
      >
        <span v-if="emojiClue">{{ emojiClue }}</span>
        <span v-else class="text-sm text-tooth-dim opacity-30 tracking-normal"
          >Waiting for emoji clue...</span
        >
      </div>
    </div>
  </div>
</template>
