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
const joiningRoom = ref('')
const createError = ref('')
const joinError = ref('')

onMounted(() => roomStore.fetchRooms())

async function createRoom() {
  if (!newRoomName.value.trim()) return
  createError.value = ''
  try {
    await api.createRoom(newRoomName.value.trim())
    joiningRoom.value = newRoomName.value.trim()
    newRoomName.value = ''
    await roomStore.fetchRooms()
  } catch (e) {
    createError.value = String(e)
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
    <div class="w-full max-w-lg">
      <!-- Header -->
      <div class="text-center mb-10">
        <div class="text-5xl mb-3">⭐</div>
        <h1 class="font-display text-3xl text-tooth font-bold">Jokestar</h1>
        <p class="text-tooth-dim opacity-50 font-mono text-sm mt-2">finish the joke · vote for the funniest</p>
      </div>

      <!-- Name input (shared for create + join) -->
      <div class="mb-6">
        <label class="block text-xs uppercase tracking-[0.2em] text-tooth-dim opacity-60 font-mono mb-2">
          Your name
        </label>
        <input
          v-model="joinDisplayName"
          type="text"
          placeholder="Enter your display name..."
          class="w-full bg-murk border border-moss rounded-lg px-4 py-3 text-tooth font-mono text-sm outline-none focus:border-leaf transition-colors"
          spellcheck="false"
        />
        <p v-if="joinError" class="text-amber text-xs font-mono mt-1">{{ joinError }}</p>
      </div>

      <!-- Create room -->
      <div class="mb-8 bg-murk border border-moss rounded-xl p-5">
        <h2 class="font-mono text-xs uppercase tracking-[0.2em] text-tooth-dim opacity-60 mb-3">
          Create a room
        </h2>
        <div class="flex gap-2">
          <input
            v-model="newRoomName"
            type="text"
            placeholder="Room name..."
            class="flex-1 bg-swamp border border-moss rounded-lg px-3 py-2.5 text-tooth font-mono text-sm outline-none focus:border-leaf transition-colors"
            spellcheck="false"
            @keydown.enter="createRoom"
          />
          <button
            class="px-4 py-2.5 bg-leaf text-tooth font-mono text-sm rounded-lg hover:bg-bright transition-colors disabled:opacity-40 cursor-pointer"
            :disabled="!newRoomName.trim() || !joinDisplayName.trim()"
            @click="createRoom"
          >
            Create
          </button>
        </div>
        <p v-if="createError" class="text-amber text-xs font-mono mt-1">{{ createError }}</p>
      </div>

      <!-- Room list -->
      <div>
        <div class="flex items-center justify-between mb-3">
          <h2 class="font-mono text-xs uppercase tracking-[0.2em] text-tooth-dim opacity-60">
            Open rooms
          </h2>
          <button
            class="text-xs text-tooth-dim opacity-40 font-mono hover:opacity-70 transition-opacity cursor-pointer"
            @click="roomStore.fetchRooms()"
          >
            refresh
          </button>
        </div>

        <div v-if="roomStore.loading" class="text-center text-tooth-dim opacity-30 font-mono text-sm py-8">
          loading...
        </div>

        <div v-else-if="roomStore.rooms.length === 0" class="text-center text-tooth-dim opacity-30 font-mono text-sm py-8">
          No rooms yet. Create one!
        </div>

        <div v-else class="flex flex-col gap-2">
          <div
            v-for="room in roomStore.rooms"
            :key="room.name"
            class="flex items-center justify-between bg-murk border border-moss rounded-lg px-4 py-3"
          >
            <div>
              <span class="text-tooth font-mono text-sm font-medium">{{ room.name }}</span>
              <span class="ml-3 text-tooth-dim opacity-50 font-mono text-xs">
                {{ room.player_count }} player{{ room.player_count !== 1 ? 's' : '' }}
              </span>
            </div>
            <button
              v-if="room.status === 'waiting'"
              class="px-3 py-1.5 bg-amber/10 border border-amber/30 text-amber font-mono text-xs rounded-lg hover:bg-amber/20 transition-colors cursor-pointer disabled:opacity-40"
              :disabled="!joinDisplayName.trim()"
              @click="join(room.name)"
            >
              join
            </button>
            <span v-else class="text-xs font-mono text-tooth-dim opacity-40">in game</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
