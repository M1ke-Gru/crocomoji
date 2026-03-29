import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const usePlayerStore = defineStore('player', () => {
  const playerId = ref(sessionStorage.getItem('player_id') ?? '')
  const roomName = ref(sessionStorage.getItem('room_name') ?? '')
  const displayName = ref(sessionStorage.getItem('display_name') ?? '')

  const isLoaded = computed(() => !!playerId.value && !!roomName.value)

  function setPlayer(id: string, room: string, name: string) {
    playerId.value = id
    roomName.value = room
    displayName.value = name
    sessionStorage.setItem('player_id', id)
    sessionStorage.setItem('room_name', room)
    sessionStorage.setItem('display_name', name)
  }

  function clear() {
    playerId.value = ''
    roomName.value = ''
    displayName.value = ''
    sessionStorage.removeItem('player_id')
    sessionStorage.removeItem('room_name')
    sessionStorage.removeItem('display_name')
  }

  return { playerId, roomName, displayName, isLoaded, setPlayer, clear }
})
