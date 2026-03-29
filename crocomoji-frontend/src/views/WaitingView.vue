<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/services/api'
import { usePlayerStore } from '@/stores/player'
import { useGameStore } from '@/stores/game'
import { connect, send } from '@/services/socket'

const route = useRoute()
const router = useRouter()
const playerStore = usePlayerStore()
const gameStore = useGameStore()

const roomName = route.params.name as string
const loading = ref(true)
const starting = ref(false)

// Game config
const numRounds = ref(5)
const jokeTime = ref(60)
const votingTime = ref(30)

onMounted(async () => {
  if (!playerStore.isLoaded || playerStore.roomName !== roomName) {
    router.replace('/')
    return
  }
  connect(roomName, playerStore.playerId)
  try {
    const room = await api.getRoom(roomName)
    gameStore.setPlayersFromRoom(room.players)
    gameStore.setStatus(room.status as 'waiting' | 'playing' | 'finished')
  } finally {
    loading.value = false
  }
})

watch(
  () => gameStore.status,
  (status) => {
    if (status === 'playing') router.push(`/room/${roomName}/play`)
  },
)

function startGame() {
  if (starting.value) return
  starting.value = true
  const sent = send('start_game', {
    num_rounds: numRounds.value,
    joke_time_seconds: jokeTime.value,
    voting_time_seconds: votingTime.value,
  })
  if (!sent) starting.value = false
}
</script>

<template>
  <div class="min-h-screen bg-swamp flex flex-col items-center justify-center px-4">
    <div class="w-full max-w-md">
      <!-- Header -->
      <div class="text-center mb-8">
        <div class="text-4xl mb-2">⭐</div>
        <h1 class="font-display text-2xl text-tooth">Jokestar</h1>
        <p class="text-tooth-dim opacity-40 font-mono text-xs mt-1">Room: {{ roomName }}</p>
      </div>

      <div v-if="loading" class="text-center text-tooth-dim opacity-30 font-mono text-sm py-8">
        loading...
      </div>

      <template v-else>
        <!-- Player list -->
        <div class="bg-murk border border-moss rounded-xl p-5 mb-4">
          <h2 class="font-mono text-xs uppercase tracking-[0.2em] text-tooth-dim opacity-60 mb-4">
            Players ({{ gameStore.playerList.length }})
          </h2>
          <div class="flex flex-col gap-2">
            <div
              v-for="player in gameStore.playerList"
              :key="player.id"
              class="flex items-center gap-3 px-3 py-2 rounded-lg bg-swamp/50"
            >
              <span class="w-2 h-2 rounded-full bg-bright"></span>
              <span class="text-tooth font-mono text-sm">{{ player.display_name }}</span>
              <span v-if="player.id === playerStore.playerId" class="ml-auto text-xs text-amber font-mono">you</span>
            </div>
          </div>
          <p v-if="gameStore.playerList.length < 2" class="text-tooth-dim opacity-40 font-mono text-xs mt-4 text-center">
            Need at least 2 players to start
          </p>
        </div>

        <!-- Game config -->
        <div class="bg-murk border border-moss rounded-xl p-5 mb-6">
          <h2 class="font-mono text-xs uppercase tracking-[0.2em] text-tooth-dim opacity-60 mb-4">Game settings</h2>
          <div class="flex flex-col gap-3">
            <label class="flex items-center justify-between gap-4">
              <span class="text-tooth-dim font-mono text-xs">Rounds</span>
              <input
                v-model.number="numRounds"
                type="number" min="1" max="20"
                class="w-20 bg-swamp border border-moss rounded px-2 py-1.5 text-tooth font-mono text-sm outline-none focus:border-leaf text-center"
              />
            </label>
            <label class="flex items-center justify-between gap-4">
              <span class="text-tooth-dim font-mono text-xs">Joke time (seconds)</span>
              <input
                v-model.number="jokeTime"
                type="number" min="10" max="300"
                class="w-20 bg-swamp border border-moss rounded px-2 py-1.5 text-tooth font-mono text-sm outline-none focus:border-leaf text-center"
              />
            </label>
            <label class="flex items-center justify-between gap-4">
              <span class="text-tooth-dim font-mono text-xs">Voting time (seconds)</span>
              <input
                v-model.number="votingTime"
                type="number" min="10" max="120"
                class="w-20 bg-swamp border border-moss rounded px-2 py-1.5 text-tooth font-mono text-sm outline-none focus:border-leaf text-center"
              />
            </label>
          </div>
        </div>

        <!-- Start button -->
        <button
          class="w-full py-3 font-mono text-sm rounded-xl transition-all duration-200 cursor-pointer"
          :class="
            gameStore.playerList.length >= 2
              ? 'bg-amber text-swamp hover:bg-amber-glow hover:-translate-y-px hover:shadow-[0_4px_16px_rgba(212,160,74,0.3)]'
              : 'bg-moss text-tooth-dim opacity-40 cursor-not-allowed'
          "
          :disabled="gameStore.playerList.length < 2 || starting"
          @click="startGame"
        >
          {{ starting ? 'Starting...' : 'Start game' }}
        </button>
      </template>
    </div>
  </div>
</template>
