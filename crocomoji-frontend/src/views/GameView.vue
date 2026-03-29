<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePlayerStore } from '@/stores/player'
import { useGameStore } from '@/stores/game'
import { useRoundStore } from '@/stores/round'
import { storeToRefs } from 'pinia'
import { connect, send, connected } from '@/services/socket'
import { api } from '@/services/api'

const route = useRoute()
const router = useRouter()
const playerStore = usePlayerStore()
const game = useGameStore()
const round = useRoundStore()

const { phase, setup, actualPunchline, submittedCount, totalPlayers, submissions, myVote, votedCount, results, index, totalRounds, timeRemaining, timerFraction } =
  storeToRefs(round)
const { playerList, status } = storeToRefs(game)

const roomName = route.params.name as string
const endingText = computed({
  get: () => round.draftEnding,
  set: (value: string) => round.setDraftEnding(value),
})
const hasSubmitted = computed(() => round.mySubmission !== '')

onMounted(async () => {
  if (!playerStore.isLoaded || playerStore.roomName !== roomName) {
    router.replace('/')
    return
  }
  if (!connected.value) {
    connect(roomName, playerStore.playerId)
  }
  try {
    const room = await api.getRoom(roomName)
    game.setPlayersFromRoom(room.players)
    game.setStatus(room.status as 'waiting' | 'playing' | 'finished')
  } catch {
    // ignore snapshot errors, ws events continue to drive state
  }
})

function submitEnding() {
  const text = endingText.value.trim()
  if (!text || hasSubmitted.value) return
  round.mySubmission = text
  round.clearDraftEnding()
  send('submit_ending', { text })
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

    <!-- Header -->
    <header class="header px-5 py-3 flex items-center justify-between border-b border-moss">
      <div class="flex items-center gap-4">
        <span class="font-display font-bold text-tooth text-lg">⭐ Jokestar</span>
        <span class="font-mono text-xs text-tooth-dim">Round {{ index + 1 }}/{{ totalRounds }}</span>
        <span
          class="font-mono text-xs px-2.5 py-0.5 rounded-full border font-medium"
          :class="{
            'text-amber border-amber/40 bg-amber/8': phase === 'submitting',
            'text-bright border-bright/50 bg-bright/10 font-semibold': phase === 'voting',
            'text-tooth-dim border-moss': phase === 'reveal',
          }"
        >
          {{ phase === 'submitting' ? 'Write' : phase === 'voting' ? 'Vote' : 'Results' }}
        </span>
      </div>

      <!-- Scoreboard -->
      <div class="flex gap-1.5 flex-wrap justify-end">
        <div
          v-for="player in playerList"
          :key="player.id"
          class="flex items-center gap-1.5 px-2.5 py-1 rounded-full font-mono text-xs border"
          :class="player.id === playerStore.playerId
            ? 'bg-amber/8 border-amber/30 text-amber'
            : 'bg-swamp border-moss text-tooth-dim'"
        >
          <span class="font-medium">{{ player.display_name[0]?.toUpperCase() }}</span>
          <span>{{ player.stars % 1 === 0.5 ? player.stars : Math.floor(player.stars) }}⭐</span>
        </div>
      </div>
    </header>

    <!-- Timer bar -->
    <div v-if="phase !== 'reveal'" class="h-1.5 w-full bg-moss/30">
      <div
        class="h-full transition-all duration-1000 ease-linear"
        :class="timerFraction > 0.4 ? 'bg-bright' : timerFraction > 0.2 ? 'bg-amber' : 'bg-red-500'"
        :style="{ width: `${timerFraction * 100}%` }"
      />
    </div>

    <!-- Timer countdown -->
    <div v-if="phase !== 'reveal' && timeRemaining > 0" class="flex justify-center pt-5 pb-1">
      <div
        class="font-mono font-bold tabular-nums leading-none"
        :class="{
          'text-6xl text-tooth': timeRemaining > 10,
          'text-6xl text-amber': timeRemaining > 5 && timeRemaining <= 10,
          'text-7xl text-red-500 animate-pulse': timeRemaining <= 5,
        }"
      >{{ timeRemaining }}</div>
    </div>

    <!-- Main content -->
    <main class="flex-1 flex flex-col items-center px-4 py-8 max-w-2xl mx-auto w-full">

      <!-- SUBMITTING -->
      <template v-if="phase === 'submitting'">
        <div class="setup-card w-full mb-6 px-7 py-6 text-center">
          <p class="font-mono text-xs text-tooth-dim uppercase tracking-widest mb-4">Finish the joke</p>
          <p class="font-display text-2xl sm:text-3xl text-tooth leading-relaxed">"{{ setup }}"</p>
          <p class="font-mono text-xs text-tooth-dim mt-4">{{ submittedCount }}/{{ totalPlayers }} submitted</p>
        </div>

        <div v-if="!hasSubmitted" class="w-full flex flex-col gap-3">
          <textarea
            v-model="endingText"
            rows="3"
            placeholder="Your punchline…"
            class="punchline-input w-full bg-murk border border-moss rounded-2xl px-5 py-4 text-tooth font-mono text-base outline-none resize-none transition-colors placeholder:text-tooth-dim/50"
            spellcheck="false"
            @keydown.ctrl.enter="submitEnding"
            @keydown.meta.enter="submitEnding"
          />
          <button
            class="btn-primary w-full py-4 font-mono text-base font-medium rounded-2xl cursor-pointer disabled:opacity-30"
            :disabled="!endingText.trim()"
            @click="submitEnding"
          >
            Submit punchline
          </button>
          <p class="text-center font-mono text-xs text-tooth-dim">Ctrl+Enter to submit</p>
        </div>

        <div v-else class="text-center py-8">
          <div class="text-4xl mb-3">✅</div>
          <p class="font-mono text-base text-tooth">Submitted!</p>
          <p class="font-mono text-sm text-tooth-dim mt-1">Waiting for {{ totalPlayers - submittedCount }} more…</p>
        </div>
      </template>

      <!-- VOTING -->
      <template v-else-if="phase === 'voting'">
        <div class="w-full mb-6 text-center">
          <p class="font-mono text-xs text-tooth-dim uppercase tracking-widest mb-3">Best ending to:</p>
          <p class="font-display text-2xl sm:text-3xl text-tooth">"{{ setup }}"</p>
          <p class="font-mono text-xs text-tooth-dim mt-3">
            {{ votedCount }} vote{{ votedCount !== 1 ? 's' : '' }} cast
            <span v-if="myVote"> · your vote is locked in</span>
          </p>
        </div>

        <div class="w-full flex flex-col gap-3">
          <button
            v-for="sub in submissionList"
            :key="sub.player_id"
            class="vote-card w-full text-left px-6 py-5 rounded-2xl border font-mono text-base leading-relaxed transition-all duration-150"
            :class="{
              'voted': myVote === sub.player_id,
              'votable': !myVote && canVoteFor(sub.player_id),
              'mine': !myVote && !canVoteFor(sub.player_id),
              'spent': myVote && myVote !== sub.player_id,
            }"
            :disabled="!!myVote || !canVoteFor(sub.player_id)"
            @click="castVote(sub.player_id)"
          >
            {{ sub.text }}
            <span v-if="!canVoteFor(sub.player_id)" class="block font-mono text-[0.65rem] text-tooth-dim mt-2 uppercase tracking-wider">your entry</span>
            <span v-if="myVote === sub.player_id" class="block font-mono text-[0.65rem] text-amber mt-2">⭐ your vote</span>
          </button>
        </div>
      </template>

      <!-- REVEAL -->
      <template v-else-if="phase === 'reveal'">
        <div class="w-full mb-6 text-center">
          <div class="text-4xl mb-3">🎤</div>
          <p class="font-display text-2xl sm:text-3xl text-tooth">"{{ setup }}"</p>
          <p v-if="actualPunchline" class="font-mono text-sm text-tooth-dim mt-2 italic">API: "{{ actualPunchline }}"</p>
        </div>

        <div class="w-full flex flex-col gap-3">
          <div
            v-for="(result, i) in results"
            :key="result.player_id"
            class="result-card flex items-start gap-5 px-6 py-5 rounded-2xl border"
            :class="i === 0 ? 'winner' : 'loser'"
          >
            <div class="font-display text-3xl font-bold min-w-[2rem] text-center pt-0.5" :class="i === 0 ? 'text-amber' : 'text-tooth-dim'">
              {{ i + 1 }}
            </div>
            <div class="flex-1">
              <div class="flex items-baseline gap-2 mb-2 flex-wrap">
                <span class="font-mono text-base font-medium text-tooth">{{ result.display_name }}</span>
                <span class="font-mono text-sm text-bright">+{{ result.stars_earned % 1 ? result.stars_earned : Math.floor(result.stars_earned) }} ⭐</span>
                <span v-if="result.stars_earned > result.votes" class="font-mono text-[0.65rem] text-amber border border-amber/30 px-2 py-0.5 rounded-full uppercase tracking-wider">unanimous!</span>
              </div>
              <p class="font-mono text-base text-tooth-dim">"{{ result.text }}"</p>
              <p class="font-mono text-xs text-tooth-dim mt-1.5">{{ result.votes }} vote{{ result.votes !== 1 ? 's' : '' }}</p>
            </div>
          </div>
        </div>

        <p class="text-center font-mono text-xs text-tooth-dim mt-8">Next round starting soon…</p>
      </template>

    </main>

    <!-- Game over overlay -->
    <div v-if="status === 'finished'" class="fixed inset-0 flex flex-col items-center justify-center px-4 z-50 game-over-bg">
      <div class="text-6xl mb-4">🏆</div>
      <p class="font-display text-4xl text-tooth mb-1">Game over!</p>
      <p class="font-mono text-sm text-tooth-dim mb-10 uppercase tracking-widest">Final standings</p>

      <div class="card w-full max-w-xs p-5 mb-8">
        <div class="flex flex-col gap-2">
          <div
            v-for="(player, i) in playerList.slice().sort((a, b) => b.stars - a.stars)"
            :key="player.id"
            class="flex items-center justify-between px-4 py-3 rounded-xl"
            :class="i === 0 ? 'bg-amber/8 border border-amber/25' : 'bg-swamp border border-moss'"
          >
            <div class="flex items-center gap-3">
              <span class="font-mono text-sm font-bold" :class="i === 0 ? 'text-amber' : 'text-tooth-dim'">{{ i + 1 }}</span>
              <span class="font-mono text-base" :class="i === 0 ? 'text-tooth font-medium' : 'text-tooth-dim'">{{ player.display_name }}</span>
            </div>
            <span class="font-mono text-base font-bold" :class="i === 0 ? 'text-amber' : 'text-tooth-dim'">
              {{ player.stars % 1 ? player.stars : Math.floor(player.stars) }} ⭐
            </span>
          </div>
        </div>
      </div>

      <button class="btn-green px-10 py-4 font-mono text-base font-medium rounded-2xl cursor-pointer" @click="$router.push(`/room/${roomName}`)">
        Play again
      </button>
    </div>

  </div>
</template>

<style scoped>
.header {
  background: rgba(255,255,255,0.9);
  backdrop-filter: blur(8px);
  position: sticky;
  top: 0;
  z-index: 10;
}

.setup-card {
  background: var(--color-murk);
  border: 1px solid var(--color-moss);
  border-radius: 1.25rem;
  box-shadow: 0 2px 16px rgba(17,17,16,0.07);
}

.punchline-input:focus {
  border-color: var(--color-amber);
  box-shadow: 0 0 0 3px rgba(196,98,0,0.1);
}

.btn-primary {
  background: var(--color-amber);
  color: #fff;
  transition: all 0.15s ease;
}
.btn-primary:not(:disabled):hover {
  background: var(--color-amber-glow);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(196,98,0,0.3);
}
.btn-primary:not(:disabled):active { transform: translateY(0); }

/* Voting cards */
.vote-card.votable {
  background: var(--color-murk);
  border-color: var(--color-moss);
  color: var(--color-tooth);
  cursor: pointer;
  box-shadow: 0 1px 6px rgba(17,17,16,0.05);
}
.vote-card.votable:hover {
  border-color: var(--color-bright);
  background: var(--color-swamp);
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(10,122,56,0.12);
}
.vote-card.voted {
  background: rgba(196,98,0,0.06);
  border-color: rgba(196,98,0,0.35);
  color: var(--color-tooth);
  cursor: default;
}
.vote-card.mine {
  background: var(--color-murk);
  border-color: var(--color-moss);
  color: var(--color-tooth-dim);
  opacity: 0.55;
  cursor: default;
}
.vote-card.spent {
  background: var(--color-murk);
  border-color: var(--color-moss);
  color: var(--color-tooth-dim);
  opacity: 0.4;
  cursor: default;
}

/* Result cards */
.result-card.winner {
  background: rgba(196,98,0,0.05);
  border-color: rgba(196,98,0,0.25);
  box-shadow: 0 2px 12px rgba(196,98,0,0.08);
}
.result-card.loser {
  background: var(--color-murk);
  border-color: var(--color-moss);
  box-shadow: 0 1px 6px rgba(17,17,16,0.04);
}

.card {
  background: var(--color-murk);
  border: 1px solid var(--color-moss);
  border-radius: 0.875rem;
  box-shadow: 0 1px 8px rgba(17,17,16,0.06);
}

.game-over-bg {
  background: rgba(240,239,232,0.96);
  backdrop-filter: blur(6px);
}

.btn-green {
  background: var(--color-bright);
  color: #fff;
  transition: all 0.15s ease;
}
.btn-green:hover {
  background: var(--color-bright-glow);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(10,122,56,0.3);
}
</style>
