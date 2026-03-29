import { defineStore } from 'pinia'
import { ref } from 'vue'

export const usePlayerStore = defineStore('player', () => {
  const currentPlayerId = ref(5)

  return { currentPlayerId }
})
