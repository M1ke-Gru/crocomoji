<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePlayerStore } from '@/stores/player'
import { useGameStore } from '@/stores/game'
import { connect, send, connected } from '@/services/socket'

const route = useRoute()
const router = useRouter()
const playerStore = usePlayerStore()
const gameStore = useGameStore()

const roomName = route.params.name as string
const starting = ref(false)

onMounted(() => {
  if (!playerStore.isLoaded || playerStore.roomName !== roomName) {
    router.replace('/')
    return
  }
  if (!connected.value) {
    connect(roomName, playerStore.playerId)
  }
})

watch(
  () => gameStore.status,
  (status) => {
    if (status === 'playing') router.push(`/room/${roomName}/play`)
  },
)

async function startGame() {
  if (starting.value || !connected.value) return
  starting.value = true
  const ok = await send('start_game', {})
  if (!ok) starting.value = false
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

      <!-- Player list -->
      <div class="bg-murk border border-moss rounded-xl p-5 mb-6">
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
        <p v-if="gameStore.playerList.length < 3" class="text-tooth-dim opacity-40 font-mono text-xs mt-4 text-center">
          Need at least 3 players to start
        </p>
      </div>

      <!-- Start button -->
      <button
        class="w-full py-3 font-mono text-sm rounded-xl transition-all duration-200 cursor-pointer"
        :class="
          gameStore.playerList.length >= 3 && connected
            ? 'bg-amber text-swamp hover:bg-amber-glow hover:-translate-y-px hover:shadow-[0_4px_16px_rgba(212,160,74,0.3)]'
            : 'bg-moss text-tooth-dim opacity-40 cursor-not-allowed'
        "
        :disabled="gameStore.playerList.length < 3 || starting || !connected"
        @click="startGame"
      >
        {{ !connected ? 'Connecting...' : starting ? 'Starting...' : 'Start game' }}
      </button>
    </div>
  </div>
</template>
