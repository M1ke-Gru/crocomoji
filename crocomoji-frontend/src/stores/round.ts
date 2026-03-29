import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface Submission {
  player_id: string
  display_name: string
  text: string
}

export interface RoundResult {
  player_id: string
  display_name: string
  text: string
  votes: number
  stars_earned: number
}

export const useRoundStore = defineStore('round', () => {
  const DRAFT_KEY = 'round_draft_ending'
  const index = ref(0)
  const totalRounds = ref(0)
  const phase = ref<'submitting' | 'voting' | 'reveal'>('submitting')
  const setup = ref('')
  const actualPunchline = ref('')
  const submittedCount = ref(0)
  const totalPlayers = ref(0)
  const draftEnding = ref(sessionStorage.getItem(DRAFT_KEY) ?? '')
  const mySubmission = ref('')
  const submissions = ref<Record<string, Submission>>({})
  const myVote = ref('')
  const votedCount = ref(0)
  const results = ref<RoundResult[]>([])

  function onRoundStarted(data: {
    round_index: number
    setup: string
    phase: string
    joke_time_seconds: number
    total_rounds: number
  }) {
    index.value = data.round_index
    totalRounds.value = data.total_rounds
    phase.value = 'submitting'
    setup.value = data.setup
    actualPunchline.value = ''
    submittedCount.value = 0
    draftEnding.value = ''
    sessionStorage.removeItem(DRAFT_KEY)
    mySubmission.value = ''
    submissions.value = {}
    myVote.value = ''
    votedCount.value = 0
    results.value = []
  }

  function onPlayerSubmitted(data: { player_id: string; display_name: string; submitted_count: number; total_players: number }) {
    submittedCount.value = data.submitted_count
    totalPlayers.value = data.total_players
  }

  function onVotingStarted(data: { submissions: Record<string, { display_name: string; text: string }>; voting_time_seconds: number }) {
    phase.value = 'voting'
    submissions.value = Object.fromEntries(
      Object.entries(data.submissions).map(([id, s]) => [id, { player_id: id, ...s }]),
    )
  }

  function onVoteReceived(data: { voter_id: string; voter_name: string; voted_count: number }) {
    votedCount.value = data.voted_count
  }

  function onRoundOver(data: { results: RoundResult[]; scores: Record<string, number>; actual_punchline?: string }) {
    phase.value = 'reveal'
    results.value = data.results
    actualPunchline.value = data.actual_punchline ?? ''
  }

  function setDraftEnding(text: string) {
    draftEnding.value = text
    sessionStorage.setItem(DRAFT_KEY, text)
  }

  function clearDraftEnding() {
    draftEnding.value = ''
    sessionStorage.removeItem(DRAFT_KEY)
  }

  return {
    index,
    totalRounds,
    phase,
    setup,
    actualPunchline,
    submittedCount,
    totalPlayers,
    draftEnding,
    mySubmission,
    submissions,
    myVote,
    votedCount,
    results,
    onRoundStarted,
    onPlayerSubmitted,
    onVotingStarted,
    onVoteReceived,
    onRoundOver,
    setDraftEnding,
    clearDraftEnding,
  }
})
