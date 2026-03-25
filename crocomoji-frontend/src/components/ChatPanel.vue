<script setup lang="ts">
import { ref, nextTick, onMounted, watch } from 'vue'
import { useGameStore } from '@/stores/game'
import { storeToRefs } from 'pinia'

const game = useGameStore()
const { guesses, isNarrator, phase, players } = storeToRefs(game)

const newMessage = ref('')
const chatBody = ref<HTMLElement | null>(null)
const visible = ref(false)

onMounted(() => {
  scrollToBottom()
  setTimeout(() => {
    visible.value = true
  }, 200)
})

watch(
  () => guesses.value.length,
  () => scrollToBottom(),
)

function scrollToBottom() {
  nextTick(() => {
    if (chatBody.value) {
      chatBody.value.scrollTop = chatBody.value.scrollHeight
    }
  })
}

function sendGuess() {
  if (!newMessage.value.trim() || isNarrator.value) return
  game.addGuess(newMessage.value)
  newMessage.value = ''
}
</script>

<template>
  <aside
    class="w-[340px] min-w-[340px] h-screen flex flex-col bg-murk border-l border-moss relative transition-all duration-600 ease-out"
    :class="visible ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-5'"
  >
    <!-- Amber accent line -->
    <div
      class="absolute top-0 left-0 bottom-0 w-px bg-linear-to-b from-transparent via-amber-dim to-transparent opacity-30"
    ></div>

    <!-- Header -->
    <div
      class="px-5 py-4 border-b border-moss flex items-center justify-between bg-linear-to-b from-[rgba(42,90,58,0.15)] to-transparent"
    >
      <div class="flex items-center gap-2 font-display font-bold text-[1.1rem] text-tooth">
        <span class="text-[1.1rem]">&#x1F4AC;</span>
        <span>Guesses</span>
      </div>
      <div
        class="flex items-center gap-1.5 text-[0.7rem] text-tooth-dim opacity-60 tracking-wide font-mono"
      >
        <span
          class="w-1.5 h-1.5 rounded-full bg-bright shadow-[0_0_6px_rgba(74,140,92,0.6)] animate-pulse"
        ></span>
        <span>{{ players.length }} players</span>
      </div>
    </div>

    <!-- Scoreboard -->
    <div class="px-4 py-3 border-b border-moss/50 flex gap-2 overflow-x-auto">
      <div
        v-for="player in players"
        :key="player.id"
        class="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[0.7rem] font-mono shrink-0 transition-colors duration-200"
        :class="
          player.id === game.narratorId
            ? 'bg-amber-dim/20 border border-amber-dim/30 text-amber'
            : 'bg-swamp/50 border border-moss/30 text-tooth-dim'
        "
      >
        <span>{{ player.avatar }}</span>
        <span class="font-medium">{{ player.score }}</span>
      </div>
    </div>

    <!-- Guesses list -->
    <div ref="chatBody" class="flex-1 overflow-y-auto p-4 flex flex-col gap-1">
      <div
        v-for="guess in guesses"
        :key="guess.id"
        class="group flex gap-2.5 px-2 py-2.5 rounded-lg transition-all duration-200 animate-[msgIn_0.3s_ease_backwards]"
        :class="[
          game.chosenGuess?.id === guess.id
            ? 'bg-amber-dim/15 border border-amber-dim/30'
            : 'hover:bg-white/[0.02]',
        ]"
      >
        <div
          class="w-8 h-8 shrink-0 flex items-center justify-center text-[1.15rem] bg-swamp rounded-full border border-moss"
        >
          {{ guess.playerAvatar }}
        </div>
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2 mb-0.5">
            <span class="font-medium text-[0.8rem] text-bright">{{ guess.playerName }}</span>
            <span class="text-[0.65rem] text-tooth-dim opacity-35">{{ guess.time }}</span>

            <!-- Chosen badge -->
            <span
              v-if="game.chosenGuess?.id === guess.id"
              class="ml-auto text-[0.6rem] uppercase tracking-wider text-amber font-mono px-1.5 py-0.5 bg-amber/10 rounded"
            >
              chosen
            </span>

            <!-- Pick button for narrator -->
            <button
              v-else-if="isNarrator && phase === 'playing'"
              class="ml-auto text-[0.6rem] uppercase tracking-wider font-mono px-2 py-1 rounded border cursor-pointer transition-all duration-200 opacity-0 group-hover:opacity-100 bg-leaf/20 border-leaf/30 text-bright hover:bg-leaf/40 hover:text-tooth"
              @click="game.chooseGuess(guess)"
            >
              pick
            </button>
          </div>
          <div class="text-[0.85rem] text-tooth-dim leading-snug break-words">
            {{ guess.text }}
          </div>
        </div>
      </div>

      <div
        v-if="guesses.length === 0"
        class="flex-1 flex items-center justify-center text-sm text-tooth-dim opacity-30 font-mono"
      >
        No guesses yet...
      </div>
    </div>

    <!-- Input (only for non-narrators during playing phase) -->
    <div
      v-if="!isNarrator && phase === 'playing'"
      class="px-5 py-4 border-t border-moss flex gap-2.5 bg-linear-to-t from-[rgba(42,90,58,0.1)] to-transparent"
    >
      <input
        v-model="newMessage"
        type="text"
        class="flex-1 bg-swamp border border-moss rounded-md px-3.5 py-2.5 text-tooth font-mono text-[0.8rem] outline-none transition-colors duration-200 focus:border-leaf placeholder:text-tooth-dim placeholder:opacity-30"
        placeholder="Type your guess..."
        @keydown.enter="sendGuess"
        spellcheck="false"
      />
      <button
        class="w-9 h-9 shrink-0 flex items-center justify-center bg-moss text-tooth-dim border-none rounded-md cursor-pointer transition-all duration-200 hover:not-disabled:bg-leaf hover:not-disabled:text-tooth disabled:opacity-40 disabled:cursor-default"
        @click="sendGuess"
        :disabled="!newMessage.trim()"
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <line x1="22" y1="2" x2="11" y2="13"></line>
          <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
        </svg>
      </button>
    </div>

    <!-- Narrator hint -->
    <div
      v-if="isNarrator && phase === 'playing'"
      class="px-5 py-3 border-t border-moss text-center text-[0.7rem] text-tooth-dim opacity-40 font-mono"
    >
      Click a guess to choose it as the best one
    </div>
  </aside>
</template>

<style>
@keyframes msgIn {
  from {
    opacity: 0;
    transform: translateY(6px);
  }
}
</style>
