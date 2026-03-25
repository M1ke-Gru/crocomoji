import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface Player {
  id: string
  name: string
  avatar: string
  score: number
}

export interface Guess {
  id: number
  playerId: string
  playerName: string
  playerAvatar: string
  text: string
  time: string
}

export type GamePhase = 'playing' | 'reviewing' | 'revealed'

export const useGameStore = defineStore('game', () => {
  // Players
  const players = ref<Player[]>([
    { id: '1', name: 'You', avatar: '🧑', score: 0 },
    { id: '2', name: 'Heron', avatar: '🪶', score: 3 },
    { id: '3', name: 'Turtle', avatar: '🐢', score: 1 },
    { id: '4', name: 'Otter', avatar: '🦦', score: 2 },
    { id: '5', name: 'Owl', avatar: '🦉', score: 4 },
    { id: '6', name: 'Frog', avatar: '🐸', score: 1 },
  ])

  const currentPlayerId = ref('1')
  const narratorId = ref('5') // Owl is the narrator

  const isNarrator = computed(() => currentPlayerId.value === narratorId.value)
  const narrator = computed(() => players.value.find((p) => p.id === narratorId.value)!)

  // Round state
  const phase = ref<GamePhase>('playing')
  const hiddenSentence = ref('The old lighthouse keeper danced with his shadow under the full moon')
  const emojiClue = ref('🏠🔦👴💃🕺👤🌕')
  const chosenGuess = ref<Guess | null>(null)
  const round = ref(3)

  // Guesses
  let nextGuessId = 1
  const guesses = ref<Guess[]>([
    {
      id: nextGuessId++,
      playerId: '2',
      playerName: 'Heron',
      playerAvatar: '🪶',
      text: 'An old man in a house with a flashlight at night?',
      time: '6:42 pm',
    },
    {
      id: nextGuessId++,
      playerId: '3',
      playerName: 'Turtle',
      playerAvatar: '🐢',
      text: 'Someone dancing alone in a lighthouse',
      time: '6:44 pm',
    },
    {
      id: nextGuessId++,
      playerId: '4',
      playerName: 'Otter',
      playerAvatar: '🦦',
      text: 'A lighthouse keeper dancing with his shadow',
      time: '6:46 pm',
    },
    {
      id: nextGuessId++,
      playerId: '6',
      playerName: 'Frog',
      playerAvatar: '🐸',
      text: 'Old man dancing by moonlight near a tower',
      time: '6:48 pm',
    },
  ])

  function addGuess(text: string) {
    const player = players.value.find((p) => p.id === currentPlayerId.value)
    if (!player) return
    guesses.value.push({
      id: nextGuessId++,
      playerId: player.id,
      playerName: player.name,
      playerAvatar: player.avatar,
      text,
      time: new Date()
        .toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })
        .toLowerCase(),
    })
  }

  function chooseGuess(guess: Guess) {
    if (!isNarrator.value) return
    chosenGuess.value = guess
  }

  /**
   * Call the backend LLM to compare the chosen guess against the hidden sentence.
   * Returns a similarity result that can be used for scoring or feedback.
   * Wire this up to the actual API endpoint when the backend is ready.
   */
  async function reviewGuessWithBackend(
    _sentence: string,
    _guess: string,
  ): Promise<{ match: boolean; score: number; feedback: string }> {
    // TODO: Replace with actual backend call, e.g.:
    // const res = await fetch('/api/review', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify({ sentence: _sentence, guess: _guess }),
    // })
    // return res.json()
    return { match: true, score: 0.85, feedback: '' }
  }

  function submitForReview() {
    if (!isNarrator.value || !chosenGuess.value) return
    phase.value = 'revealed'
  }

  function nextRound() {
    // Award point to the guesser
    if (chosenGuess.value) {
      const guesser = players.value.find((p) => p.id === chosenGuess.value!.playerId)
      if (guesser) guesser.score++
    }
    // Also award point to narrator
    narrator.value.score++

    // Rotate narrator
    const currentIdx = players.value.findIndex((p) => p.id === narratorId.value)
    const nextIdx = (currentIdx + 1) % players.value.length
    narratorId.value = players.value[nextIdx].id

    // Reset
    phase.value = 'playing'
    chosenGuess.value = null
    guesses.value = []
    emojiClue.value = ''
    hiddenSentence.value = 'A curious fox tried to teach butterflies how to swim in a teacup'
    round.value++
  }

  return {
    players,
    currentPlayerId,
    narratorId,
    isNarrator,
    narrator,
    phase,
    hiddenSentence,
    emojiClue,
    chosenGuess,
    round,
    guesses,
    addGuess,
    chooseGuess,
    submitForReview,
    reviewGuessWithBackend,
    nextRound,
  }
})
