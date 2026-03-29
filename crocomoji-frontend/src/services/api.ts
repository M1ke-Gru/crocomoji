const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const body = await res.text()
    throw new Error(body || `HTTP ${res.status}`)
  }
  return res.json()
}

export const api = {
  createRoom: (roomName: string) =>
    request<{ room_name: string }>('/rooms', {
      method: 'POST',
      body: JSON.stringify({ room_name: roomName }),
    }),

  listRooms: () =>
    request<{ name: string; player_count: number; status: string }[]>('/rooms'),

  getRoom: (name: string) =>
    request<{ name: string; players: { id: string; display_name: string; stars: number }[]; status: string }>(
      `/rooms/${name}`,
    ),

  joinRoom: (name: string, displayName: string) =>
    request<{ player_id: string; room_name: string }>(`/rooms/${name}/join`, {
      method: 'POST',
      body: JSON.stringify({ display_name: displayName }),
    }),
}
