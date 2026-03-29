<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePlayerStore } from '@/stores/player'
import { useGameStore } from '@/stores/game'
import { useRoundStore } from '@/stores/round'
import { storeToRefs } from 'pinia'
import { connect, send, connected } from '@/services/socket'

const route = useRoute()
const router = useRouter()
const playerStore = usePlayerStore()
const game = useGameStore()
const round = useRoundStore()

const { phase, setup, submittedCount, totalPlayers, submissions, myVote, votedCount, results, index, totalRounds } =
  storeToRefs(round)
const { playerList, status } = storeToRefs(game)

const roomName = route.params.name as string
const endingText = ref('')
const hasSubmitted = computed(() => round.mySubmission !== '')

onMounted(() => {
  if (!playerStore.isLoaded || playerStore.roomName !== roomName) {
    router.replace('/')
    return
  }
  if (!connected.value) {
    connect(roomName, playerStore.playerId)
  }
})

function submitEnding() {
  if (!endingText.value.trim() || hasSubmitted.value) return
  round.mySubmission = endingText.value.trim()
  send('submit_ending', { text: endingText.value.trim() })
}

function castVote(playerId: string) {
  if (myVote.value || playerId === playerStore.playerId) return
  round.myVote = playerId
  send('submit_vote', { player_id: playerId })
}

const submissionList = computed(() => Object.values(submissions.value))
const canVoteFor = (playerId: string) => playerId !== playerStore.playerId
</script>

<template>
  <div class="min-h-screen bg-swamp flex flex-col">

    <!-- Top bar -->
    <header class="px-6 py-3 border-b border-moss flex items-center justify-between bg-murk">
      <div class="flex items-center gap-3">
        <span class="font-display text-tooth font-bold text-lg">⭐ Jokestar</span>
        <span class="font-mono text-xs text-tooth-dim opacity-50">
          Round {{ index + 1 }} / {{ totalRounds }}
        </span>
        <span
          class="font-mono text-[0.65rem] px-2 py-0.5 rounded-full border"
          :class="{
            'text-amber border-amber/30 bg-amber/10': phase === 'submitting',
            'text-bright border-bright/30 bg-bright/10': phase === 'voting',
            'text-tooth-dim border-moss': phase === 'reveal',
          }"
        >
          {{ phase }}
        </span>
      </div>

      <!-- Mini scoreboard -->
      <div class="flex gap-2">
        <div
          v-for="player in playerList"
          :key="player.id"
          class="flex items-center gap-1 px-2 py-1 rounded-full text-[0.65rem] font-mono"
          :class="player.id === playerStore.playerId ? 'bg-amber/10 border border-amber/30 text-amber' : 'bg-swamp/50 border border-moss/30 text-tooth-dim'"
        >
          <span>{{ player.display_name[0] }}</span>
          <span>{{ player.stars % 1 === 0.5 ? player.stars : Math.floor(player.stars) }}⭐</span>
        </div>
      </div>
    </header>

    <!-- Main content -->
    <main class="flex-1 flex flex-col items-center justify-center px-4 py-8 max-w-2xl mx-auto w-full">

      <!-- SUBMITTING phase -->
      <template v-if="phase === 'submitting'">
        <div class="w-full text-center mb-8">
          <div class="text-[0.65rem] uppercase tracking-[0.2em] text-tooth-dim font-mono opacity-60 mb-3">
            Finish the joke
          </div>
          <div class="bg-murk border border-amber-dim/30 rounded-2xl px-8 py-6 mb-2">
            <p class="font-display text-2xl text-tooth leading-relaxed">"{{ setup }}"</p>
          </div>
          <p class="text-tooth-dim opacity-40 font-mono text-xs">
            {{ submittedCount }} / {{ totalPlayers }} submitted
          </p>
        </div>

        <div v-if="!hasSubmitted" class="w-full flex flex-col gap-3">
          <textarea
            v-model="endingText"
            rows="3"
            placeholder="Your punchline..."
            class="w-full bg-murk border border-moss rounded-xl px-4 py-3 text-tooth font-mono text-sm outline-none focus:border-amber-dim resize-none transition-colors placeholder:text-tooth-dim placeholder:opacity-30"
            spellcheck="false"
            @keydown.ctrl.enter="submitEnding"
            @keydown.meta.enter="submitEnding"
          />
          <button
            class="w-full py-3 bg-amber text-swamp font-mono text-sm font-medium rounded-xl hover:bg-amber-glow transition-colors cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
            :disabled="!endingText.trim()"
            @click="submitEnding"
          >
            Submit punchline
          </button>
          <p class="text-center text-tooth-dim opacity-30 font-mono text-xs">Ctrl+Enter to submit</p>
        </div>

        <div v-else class="text-center">
          <div class="text-4xl mb-3">✅</div>
          <p class="text-tooth font-mono text-sm">Submitted! Waiting for others...</p>
          <p class="text-tooth-dim opacity-40 font-mono text-xs mt-1">
            {{ submittedCount }} / {{ totalPlayers }} ready
          </p>
        </div>
      </template>

      <!-- VOTING phase -->
      <template v-else-if="phase === 'voting'">
        <div class="w-full">
          <div class="text-center mb-6">
            <div class="text-[0.65rem] uppercase tracking-[0.2em] text-bright font-mono opacity-70 mb-2">
              Vote for the funniest ending to:
            </div>
            <p class="font-display text-xl text-tooth">"{{ setup }}"</p>
            <p class="text-tooth-dim opacity-40 font-mono text-xs mt-2">
              {{ votedCount }} votes cast
              <span v-if="myVote"> · your vote is in</span>
            </p>
          </div>

          <div class="flex flex-col gap-3">
            <button
              v-for="sub in submissionList"
              :key="sub.player_id"
              class="w-full text-left px-5 py-4 rounded-xl border transition-all duration-200 font-mono text-sm"
              :class="{
                'bg-amber/15 border-amber/40 text-tooth': myVote === sub.player_id,
                'bg-murk border-moss text-tooth-dim hover:border-leaf hover:bg-moss/30 cursor-pointer': !myVote && canVoteFor(sub.player_id),
                'bg-swamp/30 border-moss/30 text-tooth-dim opacity-40 cursor-not-allowed': !myVote && !canVoteFor(sub.player_id),
                'bg-murk border-moss text-tooth-dim opacity-60 cursor-not-allowed': myVote && myVote !== sub.player_id,
              }"
              :disabled="!!myVote || !canVoteFor(sub.player_id)"
              @click="castVote(sub.player_id)"
            >
              <span class="text-base leading-relaxed">{{ sub.text }}</span>
              <span
                v-if="!canVoteFor(sub.player_id)"
                class="block text-[0.65rem] text-tooth-dim opacity-50 mt-1"
              >
                (your entry)
              </span>
              <span
                v-if="myVote === sub.player_id"
                class="block text-[0.65rem] text-amber mt-1"
              >
                ⭐ you voted for this
              </span>
            </button>
          </div>
        </div>
      </template>

      <!-- REVEAL phase -->
      <template v-else-if="phase === 'reveal'">
        <div class="w-full">
          <div class="text-center mb-6">
            <div class="text-4xl mb-2">🎤</div>
            <p class="font-display text-xl text-tooth">"{{ setup }}"</p>
          </div>

          <div class="flex flex-col gap-3">
            <div
              v-for="(result, i) in results"
              :key="result.player_id"
              class="flex items-start gap-4 px-5 py-4 rounded-xl border transition-all"
              :class="i === 0 ? 'bg-amber/10 border-amber/30' : 'bg-murk border-moss'"
            >
              <div class="text-2xl font-mono font-bold min-w-[2rem] text-center" :class="i === 0 ? 'text-amber' : 'text-tooth-dim opacity-40'">
                {{ i + 1 }}
              </div>
              <div class="flex-1">
                <div class="flex items-center gap-2 mb-1">
                  <span class="text-tooth font-mono text-sm font-medium">{{ result.display_name }}</span>
                  <span class="text-xs font-mono text-bright">
                    +{{ result.stars_earned % 1 ? result.stars_earned : Math.floor(result.stars_earned) }}⭐
                  </span>
                  <span v-if="result.stars_earned > result.votes" class="text-[0.6rem] font-mono text-amber bg-amber/10 px-1.5 py-0.5 rounded">
                    unanimous bonus!
                  </span>
                </div>
                <p class="text-tooth-dim font-mono text-sm">"{{ result.text }}"</p>
                <p class="text-tooth-dim opacity-40 font-mono text-xs mt-1">
                  {{ result.votes }} vote{{ result.votes !== 1 ? 's' : '' }}
                </p>
              </div>
            </div>
          </div>

          <p class="text-center text-tooth-dim opacity-30 font-mono text-xs mt-6">
            Next round starting soon...
          </p>
        </div>
      </template>

    </main>

    <!-- Game over overlay -->
    <div
      v-if="status === 'finished'"
      class="fixed inset-0 bg-swamp/95 flex flex-col items-center justify-center px-4 z-50"
    >
      <div class="text-5xl mb-4">🏆</div>
      <p class="font-display text-3xl text-tooth mb-8">Game over!</p>
      <div class="bg-murk border border-moss rounded-xl p-6 w-full max-w-sm mb-8">
        <h3 class="font-mono text-xs uppercase tracking-[0.2em] text-tooth-dim opacity-60 mb-4 text-center">
          Final stars
        </h3>
        <div class="flex flex-col gap-2">
          <div
            v-for="(player, i) in playerList.slice().sort((a, b) => b.stars - a.stars)"
            :key="player.id"
            class="flex items-center justify-between px-3 py-2 rounded-lg"
            :class="i === 0 ? 'bg-amber/10 border border-amber/20' : 'bg-swamp/50'"
          >
            <div class="flex items-center gap-2">
              <span class="text-tooth-dim font-mono text-xs opacity-50">{{ i + 1 }}</span>
              <span class="text-tooth font-mono text-sm">{{ player.display_name }}</span>
            </div>
            <span class="text-amber font-mono text-sm font-medium">
              {{ player.stars % 1 ? player.stars : Math.floor(player.stars) }} ⭐
            </span>
          </div>
        </div>
      </div>
      <button
        class="px-8 py-3 bg-amber text-swamp font-mono text-sm font-medium rounded-xl hover:bg-amber-glow transition-colors cursor-pointer"
        @click="$router.push('/')"
      >
        Back to lobby
      </button>
    </div>
  </div>
</template>
