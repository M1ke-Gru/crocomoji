<script setup lang="ts">
import { useGameStore } from '@/stores/game'
import { storeToRefs } from 'pinia'

const game = useGameStore()
const { phase, hiddenSentence, chosenGuess, isNarrator, round } = storeToRefs(game)
</script>

<template>
  <div class="flex-1 overflow-y-auto flex flex-col">
    <!-- Round indicator -->
    <div class="px-8 pt-6 pb-2 flex items-center justify-between">
      <div class="font-mono text-[0.7rem] uppercase tracking-[0.3em] text-amber">
        Round {{ round }}
      </div>
      <div class="flex items-center gap-2 text-[0.7rem] text-tooth-dim opacity-50 font-mono">
        <span>{{ game.narrator.avatar }}</span>
        <span>{{ isNarrator ? 'You are narrating' : `${game.narrator.name} is narrating` }}</span>
      </div>
    </div>

    <!-- Main game area -->
    <div class="flex-1 flex flex-col items-center justify-center px-8 gap-8">
      <!-- PLAYING: Show sentence to narrator, show "?" to others -->
      <template v-if="phase === 'playing'">
        <!-- Narrator sees the sentence -->
        <div v-if="isNarrator" class="w-full max-w-xl text-center">
          <div
            class="text-[0.65rem] uppercase tracking-[0.2em] text-amber-dim font-mono mb-3 opacity-70"
          >
            Your sentence to convey
          </div>
          <div
            class="relative bg-swamp/60 border border-amber-dim/30 rounded-2xl px-8 py-6 backdrop-blur-sm"
          >
            <div
              class="absolute -top-px left-[10%] right-[10%] h-px bg-linear-to-r from-transparent via-amber/40 to-transparent"
            ></div>
            <p class="font-display text-xl leading-relaxed text-tooth">
              "{{ hiddenSentence }}"
            </p>
          </div>
          <div class="mt-4 text-[0.7rem] text-tooth-dim opacity-40 font-mono">
            Use emoji below to help others guess this sentence
          </div>
        </div>

        <!-- Non-narrator sees a mystery prompt -->
        <div v-else class="w-full max-w-xl text-center">
          <div class="text-6xl mb-4 opacity-30">&#x1F50D;</div>
          <p class="font-display text-xl text-tooth-dim">
            What is {{ game.narrator.name }} trying to say?
          </p>
          <p class="mt-2 text-sm text-tooth-dim opacity-40 font-mono">
            Look at the emoji clue and post your guess in the chat
          </p>
        </div>

        <!-- Chosen guess display -->
        <div v-if="chosenGuess" class="w-full max-w-xl">
          <div
            class="text-[0.65rem] uppercase tracking-[0.2em] text-bright font-mono mb-2 text-center"
          >
            Best guess so far
          </div>
          <div
            class="bg-leaf/10 border border-leaf/30 rounded-xl px-6 py-4 text-center transition-all duration-500"
          >
            <div class="flex items-center justify-center gap-2 mb-2">
              <span class="text-lg">{{ chosenGuess.playerAvatar }}</span>
              <span class="text-sm font-medium text-bright">{{ chosenGuess.playerName }}</span>
            </div>
            <p class="font-display text-lg text-tooth leading-relaxed">
              "{{ chosenGuess.text }}"
            </p>
            <button
              v-if="isNarrator"
              class="mt-4 px-6 py-2 bg-amber text-swamp font-mono text-sm font-medium rounded-lg transition-all duration-200 hover:bg-amber-glow hover:-translate-y-px hover:shadow-[0_4px_16px_rgba(212,160,74,0.3)] cursor-pointer"
              @click="game.submitForReview()"
            >
              Submit for review
            </button>
          </div>
        </div>
      </template>

      <!-- REVEALED: Show the answer -->
      <template v-if="phase === 'revealed'">
        <div class="w-full max-w-xl text-center">
          <div class="text-5xl mb-4">&#x1F389;</div>
          <div
            class="text-[0.65rem] uppercase tracking-[0.2em] text-amber-dim font-mono mb-3 opacity-70"
          >
            The sentence was
          </div>
          <div class="bg-swamp/60 border border-amber-dim/30 rounded-2xl px-8 py-6 mb-6">
            <p class="font-display text-xl leading-relaxed text-tooth">
              "{{ hiddenSentence }}"
            </p>
          </div>

          <div v-if="chosenGuess" class="mb-6">
            <div
              class="text-[0.65rem] uppercase tracking-[0.2em] text-bright font-mono mb-2 opacity-70"
            >
              Winning guess by {{ chosenGuess.playerName }}
              {{ chosenGuess.playerAvatar }}
            </div>
            <div class="bg-leaf/10 border border-leaf/30 rounded-xl px-6 py-3">
              <p class="font-display text-lg text-tooth-dim italic">
                "{{ chosenGuess.text }}"
              </p>
            </div>
          </div>

          <button
            class="px-8 py-3 bg-amber text-swamp font-mono text-sm font-medium rounded-lg transition-all duration-200 hover:bg-amber-glow hover:-translate-y-px hover:shadow-[0_4px_16px_rgba(212,160,74,0.3)] cursor-pointer"
            @click="game.nextRound()"
          >
            Next round
          </button>
        </div>
      </template>
    </div>
  </div>
</template>
