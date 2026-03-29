import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '@/services/api'

export interface RoomSummary {
  name: string
  player_count: number
  status: string
}

export const useRoomStore = defineStore('room', () => {
  const rooms = ref<RoomSummary[]>([])
  const loading = ref(false)
  const error = ref('')

  async function fetchRooms() {
    loading.value = true
    error.value = ''
    try {
      rooms.value = await api.listRooms()
    } catch (e) {
      error.value = String(e)
    } finally {
      loading.value = false
    }
  }

  return { rooms, loading, error, fetchRooms }
})
