import { defineStore } from 'pinia'
import { computed } from 'vue'
import type { RichGuess } from '@/types/rich_guess'
import { get_players } from '@/api/player_api'
import { get_current_game, update_game } from '@/api/game_api'
import { get_guesses, add_guess, clear_guesses } from '@/api/guess_api'
import { usePlayerStore } from '@/stores/player'
import { GamePhase } from '@/enums/GamePhase'

export const useGameStore = defineStore('game', () => {
  const playerStore = usePlayerStore()

  // Data sources (mock API layer)
  const players = get_players()                           // Ref<Player[]>
  const game = get_current_game(1)                        // Ref<Game> — reactive computed
  const rawGuesses = get_guesses(game.value.id)           // Ref<Guess[]>

  // Flat computed properties from game state
  const phase = computed(() => game.value.phase)
  const narratorId = computed(() => game.value.narrator_id)
  const hiddenSentence = computed(() => game.value.hidden_sentence)
  const round = computed(() => game.value.round)

  // Writable computed — EmojiInput writes directly via storeToRefs
  const emojiClue = computed({
    get: () => game.value.emoji_clue,
    set: (val: string) => update_game(game.value.id, { emoji_clue: val }),
  })

  const narrator = computed(() => players.value.find((p) => p.id === narratorId.value)!)

  const isNarrator = computed(() => playerStore.currentPlayerId === narratorId.value)

  // Enrich guesses with player info for display
  const guesses = computed<RichGuess[]>(() =>
    rawGuesses.value.map((g) => {
      const player = players.value.find((p) => p.id === g.playerId)
      return {
        ...g,
        playerName: player?.name ?? 'Unknown',
        playerAvatar: player?.avatar ?? '❓',
      }
    }),
  )

  const chosenGuess = computed<RichGuess | null>(() => {
    const id = game.value.chosen_guess_id
    if (id === null) return null
    return guesses.value.find((g) => g.id === id) ?? null
  })

  // Actions
  function addGuess(text: string): void {
    if (isNarrator.value) return
    const time = new Date()
      .toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })
      .toLowerCase()
    add_guess(game.value.id, { playerId: playerStore.currentPlayerId, text, time })
  }

  function chooseGuess(guess: RichGuess): void {
    if (!isNarrator.value) return
    update_game(game.value.id, { chosen_guess_id: guess.id })
  }

  function submitForReview(): void {
    if (!isNarrator.value || game.value.chosen_guess_id === null) return
    update_game(game.value.id, { phase: GamePhase.Revealed })
  }

  async function reviewGuessWithBackend(
    _sentence: string,
    _guess: string,
  ): Promise<{ match: boolean; score: number; feedback: string }> {
    // TODO: replace with actual fetch('/api/review', ...) call
    return { match: true, score: 0.85, feedback: '' }
  }

  function nextRound(): void {
    // Award point to winning guesser
    const chosen = chosenGuess.value
    if (chosen) {
      const guesser = players.value.find((p) => p.id === chosen.playerId)
      if (guesser) guesser.score++
    }
    // Award point to narrator
    const narratorPlayer = players.value.find((p) => p.id === narratorId.value)
    if (narratorPlayer) narratorPlayer.score++

    // Rotate narrator
    const currentIdx = players.value.findIndex((p) => p.id === narratorId.value)
    const nextNarratorId = players.value[(currentIdx + 1) % players.value.length].id

    clear_guesses(game.value.id)

    update_game(game.value.id, {
      phase: GamePhase.Playing,
      chosen_guess_id: null,
      emoji_clue: '',
      hidden_sentence: 'A curious fox tried to teach butterflies how to swim in a teacup',
      round: game.value.round + 1,
      narrator_id: nextNarratorId,
    })
  }

  return {
    players,
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
