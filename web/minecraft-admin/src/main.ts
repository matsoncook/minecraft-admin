import './style.css'

type StatusResponse = { status: string }
type PlayersResponse = {
  online: number
  players: string[]
  source: 'rcon' | 'journal'
  note?: string
}

const statusLine = document.querySelector<HTMLParagraphElement>('#status-line')
const errorLine = document.querySelector<HTMLParagraphElement>('#error-line')
const playerCount = document.querySelector<HTMLSpanElement>('#player-count')
const playersList = document.querySelector<HTMLUListElement>('#players-list')
const playersMeta = document.querySelector<HTMLParagraphElement>('#players-meta')
const refreshButton = document.querySelector<HTMLButtonElement>('#refresh-all')

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(path)
  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || `Request failed: ${response.status}`)
  }
  return response.json() as Promise<T>
}

function renderPlayers(data: PlayersResponse): void {
  if (!playerCount || !playersList || !playersMeta) {
    return
  }

  playerCount.textContent = String(data.online)
  playersMeta.textContent =
    data.source === 'rcon'
      ? 'Source: live RCON query'
      : 'Source: journal fallback (best-effort)'

  playersList.innerHTML = ''
  if (data.players.length === 0) {
    playersList.innerHTML = '<li class="muted">No players online</li>'
    return
  }

  for (const name of data.players) {
    const li = document.createElement('li')
    li.textContent = name
    playersList.append(li)
  }
}

function setError(message: string | null): void {
  if (!errorLine) {
    return
  }
  if (!message) {
    errorLine.hidden = true
    errorLine.textContent = ''
    return
  }
  errorLine.hidden = false
  errorLine.textContent = message
}

async function refresh(): Promise<void> {
  try {
    setError(null)
    const [status, players] = await Promise.all([
      fetchJson<StatusResponse>('/api/server/status'),
      fetchJson<PlayersResponse>('/api/server/players'),
    ])

    if (statusLine) {
      statusLine.textContent = `Server status: ${status.status}`
    }

    renderPlayers(players)
  } catch (error) {
    setError(error instanceof Error ? error.message : 'Failed to load dashboard data')
  }
}

refreshButton?.addEventListener('click', () => {
  void refresh()
})

void refresh()
setInterval(() => {
  void refresh()
}, 15000)
