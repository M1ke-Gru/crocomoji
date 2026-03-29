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
    <div class="w-full max-w-sm">

      <!-- Header -->
      <div class="text-center mb-8">
        <div class="font-mono text-xs text-tooth-dim tracking-widest uppercase mb-3">Room</div>
        <h1 class="font-display text-4xl font-bold text-tooth mb-3">{{ roomName }}</h1>
        <span
          class="inline-flex items-center gap-2 font-mono text-xs px-3 py-1.5 rounded-full border"
          :class="connected
            ? 'border-bright/40 bg-bright/8 text-bright'
            : 'border-moss text-tooth-dim'"
        >
          <span class="w-1.5 h-1.5 rounded-full" :class="connected ? 'bg-bright animate-pulse' : 'bg-moss'"></span>
          {{ connected ? 'Connected' : 'Connecting…' }}
        </span>
      </div>

      <!-- Player list -->
      <div class="card p-5 mb-5">
        <div class="flex items-center justify-between mb-4">
          <h2 class="font-mono text-sm text-tooth-dim">Players</h2>
          <span class="font-mono text-xs text-tooth-dim">{{ gameStore.playerList.length }} joined</span>
        </div>
        <div class="flex flex-col gap-2">
          <div
            v-for="player in gameStore.playerList"
            :key="player.id"
            class="flex items-center gap-3 px-3 py-2.5 rounded-lg"
            :class="player.id === playerStore.playerId
              ? 'bg-amber/8 border border-amber/20'
              : 'bg-swamp border border-moss'"
          >
            <span class="w-2 h-2 rounded-full shrink-0" :class="player.id === playerStore.playerId ? 'bg-amber' : 'bg-bright'"></span>
            <span class="font-mono text-sm font-medium flex-1" :class="player.id === playerStore.playerId ? 'text-amber' : 'text-tooth'">
              {{ player.display_name }}
            </span>
            <span v-if="player.id === playerStore.playerId" class="font-mono text-[0.65rem] text-amber/60 uppercase tracking-wider">you</span>
          </div>
        </div>
        <p v-if="gameStore.playerList.length < 3" class="font-mono text-xs text-tooth-dim text-center mt-4">
          Need {{ 3 - gameStore.playerList.length }} more to start
        </p>
      </div>

      <!-- Start button -->
      <button
        class="w-full py-4 font-mono text-base font-medium rounded-2xl transition-all duration-200 cursor-pointer"
        :class="gameStore.playerList.length >= 3 && connected ? 'btn-start-active' : 'btn-start-inactive cursor-not-allowed'"
        :disabled="gameStore.playerList.length < 3 || starting || !connected"
        @click="startGame"
      >
        {{ !connected ? 'Connecting…' : starting ? 'Starting…' : 'Start game' }}
      </button>

    </div>
  </div>
</template>

<style scoped>
.card {
  background: var(--color-murk);
  border: 1px solid var(--color-moss);
  border-radius: 0.875rem;
  box-shadow: 0 1px 8px rgba(17,17,16,0.06);
}

.btn-start-active {
  background: var(--color-bright);
  color: #fff;
}
.btn-start-active:hover {
  background: var(--color-bright-glow);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(10,122,56,0.3);
}
.btn-start-active:active { transform: translateY(0); }

.btn-start-inactive {
  background: var(--color-moss);
  color: var(--color-tooth-dim);
  opacity: 0.5;
}
</style>
