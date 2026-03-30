<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/services/api'
import { usePlayerStore } from '@/stores/player'
import { useRoomStore } from '@/stores/room'

const router = useRouter()
const playerStore = usePlayerStore()
const roomStore = useRoomStore()

const newRoomName = ref('')
const joinDisplayName = ref('')
const createError = ref('')
const joinError = ref('')
const duplicateRoomName = ref('')

onMounted(() => roomStore.fetchRooms())

async function createRoom() {
  if (!newRoomName.value.trim()) return
  if (!joinDisplayName.value.trim()) {
    joinError.value = 'Enter your name first'
    return
  }
  createError.value = ''
  duplicateRoomName.value = ''
  try {
    const name = newRoomName.value.trim()
    await api.createRoom(name)
    newRoomName.value = ''
    await join(name)
  } catch (e) {
    const msg = String(e)
    if (msg.toLowerCase().includes('already exists')) {
      duplicateRoomName.value = newRoomName.value.trim()
    } else {
      createError.value = msg
    }
  }
}

async function join(roomName: string) {
  if (!joinDisplayName.value.trim()) {
    joinError.value = 'Enter your name first'
    return
  }
  joinError.value = ''
  try {
    const res = await api.joinRoom(roomName, joinDisplayName.value.trim())
    playerStore.setPlayer(res.player_id, roomName, joinDisplayName.value.trim())
    router.push(`/room/${roomName}`)
  } catch (e) {
    joinError.value = String(e)
  }
}
</script>

<template>
  <div class="min-h-screen bg-swamp flex flex-col items-center justify-center px-4 py-12">
    <div class="w-full max-w-md">

      <!-- Header -->
      <div class="text-center mb-10">
        <div class="text-6xl mb-4 logo-star">⭐</div>
        <h1 class="font-display text-4xl font-bold text-tooth mb-2">Jokestar</h1>
        <p class="font-mono text-sm text-tooth-dim tracking-wide">Finish the joke · steal the crowd</p>
      </div>

      <!-- Your name -->
      <div class="mb-4">
        <label class="block font-mono text-sm text-tooth-dim mb-2">Your name</label>
        <input
          v-model="joinDisplayName"
          type="text"
          placeholder="What do they call you?"
          class="field w-full bg-murk border border-moss rounded-xl px-4 py-3 text-tooth font-mono text-base outline-none transition-colors"
          spellcheck="false"
        />
        <p v-if="joinError" class="text-amber font-mono text-xs mt-2">⚠ {{ joinError }}</p>
      </div>

      <!-- Create room -->
      <div class="card mb-4 p-5">
        <h2 class="font-mono text-sm text-tooth-dim mb-3">Create a room</h2>
        <div class="flex gap-2">
          <input
            v-model="newRoomName"
            type="text"
            placeholder="Room name…"
            class="field flex-1 bg-swamp border border-moss rounded-xl px-4 py-3 text-tooth font-mono text-sm outline-none transition-colors"
            spellcheck="false"
            @keydown.enter="createRoom"
          />
          <button
            class="btn-primary px-5 py-3 font-mono text-sm font-medium rounded-xl disabled:opacity-30 cursor-pointer"
            :disabled="!newRoomName.trim()"
            @click="createRoom"
          >
            Create
          </button>
        </div>
        <p v-if="createError" class="text-amber font-mono text-xs mt-2">{{ createError }}</p>
      </div>

      <!-- Room list -->
      <div class="card p-5">
        <div class="flex items-center justify-between mb-4">
          <h2 class="font-mono text-sm text-tooth-dim">Open rooms</h2>
          <button class="btn-refresh font-mono text-sm cursor-pointer" @click="roomStore.fetchRooms()">
            ↻ Refresh
          </button>
        </div>

        <div v-if="roomStore.loading" class="text-center font-mono text-sm text-tooth-dim py-6">
          Loading…
        </div>

        <div v-else-if="roomStore.rooms.length === 0" class="text-center py-6">
          <div class="text-3xl mb-2">🎤</div>
          <p class="font-mono text-sm text-tooth-dim">Be the first — create a room and invite your friends!</p>
        </div>

        <div v-else class="flex flex-col gap-2">
          <div
            v-for="room in roomStore.rooms"
            :key="room.name"
            class="flex items-center justify-between px-4 py-3 rounded-xl bg-swamp border border-moss"
            :class="room.status !== 'waiting' ? 'opacity-60' : ''"
          >
            <div>
              <span class="text-tooth font-mono text-base font-medium">{{ room.name }}</span>
              <span class="ml-3 text-tooth-dim font-mono text-xs">
                {{ room.player_count }} player{{ room.player_count !== 1 ? 's' : '' }}
              </span>
            </div>
            <button
              v-if="room.status === 'waiting' && !room.locked"
              class="btn-join px-4 py-1.5 font-mono text-xs font-medium rounded-lg disabled:opacity-30 cursor-pointer"
              :disabled="!joinDisplayName.trim()"
              @click="join(room.name)"
            >
              Join →
            </button>
            <span v-else-if="room.locked" class="font-mono text-xs text-amber">🔒 locked</span>
            <span v-else class="font-mono text-xs text-tooth-dim italic">in game</span>
          </div>
        </div>
      </div>

    </div>
  </div>

  <!-- Duplicate room popup -->
  <Transition name="popup">
    <div v-if="duplicateRoomName" class="fixed inset-0 flex items-center justify-center px-4 z-50" @click.self="duplicateRoomName = ''">
      <div class="popup-backdrop absolute inset-0"></div>
      <div class="popup relative w-full max-w-sm p-6 text-center">
        <div class="text-4xl mb-3">🚫</div>
        <h3 class="font-display text-xl font-bold text-tooth mb-2">Room already exists</h3>
        <p class="font-mono text-sm text-tooth-dim mb-6">
          A room named <span class="text-tooth font-medium">"{{ duplicateRoomName }}"</span> already exists. Pick a different name.
        </p>
        <button class="btn-primary w-full py-3 font-mono text-sm font-medium rounded-xl cursor-pointer" @click="duplicateRoomName = ''">
          Got it
        </button>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.logo-star {
  display: inline-block;
  animation: float 3s ease-in-out infinite;
  filter: drop-shadow(0 4px 12px rgba(196,98,0,0.3));
}
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}

.card {
  background: var(--color-murk);
  border: 1px solid var(--color-moss);
  border-radius: 0.875rem;
  box-shadow: 0 1px 8px rgba(17,17,16,0.06);
}

.field:focus {
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
  transform: translateY(-1px);
  box-shadow: 0 4px 14px rgba(196,98,0,0.3);
}

.btn-join {
  background: var(--color-bright);
  color: #fff;
  border: none;
  transition: all 0.15s ease;
}
.btn-join:not(:disabled):hover {
  background: var(--color-bright-glow);
  transform: translateY(-1px);
  box-shadow: 0 4px 14px rgba(10,122,56,0.3);
}

.btn-refresh {
  background: var(--color-swamp);
  color: var(--color-tooth-dim);
  border: 1.5px solid var(--color-moss);
  padding: 0.375rem 0.875rem;
  border-radius: 0.625rem;
  transition: all 0.15s ease;
}
.btn-refresh:hover {
  border-color: var(--color-leaf);
  color: var(--color-tooth);
  background: var(--color-swamp);
}

/* Popup */
.popup-backdrop {
  background: rgba(17,17,16,0.4);
  backdrop-filter: blur(3px);
}

.popup {
  background: var(--color-murk);
  border: 1.5px solid var(--color-moss);
  border-radius: 1.25rem;
  box-shadow: 0 8px 40px rgba(17,17,16,0.18);
}

.popup-enter-active, .popup-leave-active {
  transition: opacity 0.2s ease;
}
.popup-enter-active .popup, .popup-leave-active .popup {
  transition: transform 0.2s ease, opacity 0.2s ease;
}
.popup-enter-from, .popup-leave-to {
  opacity: 0;
}
.popup-enter-from .popup, .popup-leave-to .popup {
  transform: scale(0.95) translateY(8px);
  opacity: 0;
}
</style>
