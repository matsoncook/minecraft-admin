import './style.css'

type StatusResponse = { status: string }
type BackupResponse = {
  ok: boolean
  archive_path: string
  size_bytes: number
  notes?: string[]
}
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
const restartAdminButton = document.querySelector<HTMLButtonElement>('#restart-admin')
const backupButton = document.querySelector<HTMLButtonElement>('#create-backup')
const backupLine = document.querySelector<HTMLParagraphElement>('#backup-line')

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(path)
  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || `Request failed: ${response.status}`)
  }
  return response.json() as Promise<T>
}

async function kickPlayer(playerName: string): Promise<void> {
  const reasonInput = window.prompt(`Kick ${playerName}.\nOptional reason:`, 'Kicked by admin')
  if (reasonInput === null) {
    return
  }

  const reason = reasonInput.trim()
  const params = new URLSearchParams()
  if (reason.length > 0) {
    params.set('reason', reason)
  }

  const path = `/api/server/players/${encodeURIComponent(playerName)}/kick${
    params.toString() ? `?${params.toString()}` : ''
  }`
  const response = await fetch(path, { method: 'POST' })
  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || `Failed to kick ${playerName}`)
  }
}

async function banPlayer(playerName: string): Promise<void> {
  const confirmed = window.confirm(
    `Ban ${playerName}? They will be kicked and prevented from rejoining.`
  )
  if (!confirmed) {
    return
  }

  const reasonInput = window.prompt(`Ban ${playerName}.\nOptional reason:`, 'Banned by admin')
  if (reasonInput === null) {
    return
  }

  const reason = reasonInput.trim()
  const params = new URLSearchParams()
  if (reason.length > 0) {
    params.set('reason', reason)
  }

  const path = `/api/server/players/${encodeURIComponent(playerName)}/ban${
    params.toString() ? `?${params.toString()}` : ''
  }`
  const response = await fetch(path, { method: 'POST' })
  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || `Failed to ban ${playerName}`)
  }
}


async function restartAdminService(): Promise<void> {
  const response = await fetch('/api/systemctl/minecraft-admin/restart', { method: 'POST' })
  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || 'Failed to restart minecraft-admin service')
  }
}

async function createBackup(): Promise<BackupResponse> {
  const response = await fetch('/api/server/backup', { method: 'POST' })
  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || 'Failed to create world backup')
  }
  return response.json() as Promise<BackupResponse>
}

function formatBytes(bytes: number): string {
  if (!Number.isFinite(bytes) || bytes < 1024) {
    return `${bytes} B`
  }
  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`
  }
  if (bytes < 1024 * 1024 * 1024) {
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`
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
    li.className = 'player-row'

    const nameSpan = document.createElement('span')
    nameSpan.textContent = name

    const kickButton = document.createElement('button')
    kickButton.type = 'button'
    kickButton.className = 'kick-button'
    kickButton.textContent = 'Kick'
    kickButton.addEventListener('click', () => {
      kickButton.disabled = true
      setError(null)

      void kickPlayer(name)
        .then(() => refresh())
        .catch((error) => {
          setError(error instanceof Error ? error.message : `Failed to kick ${name}`)
        })
        .finally(() => {
          kickButton.disabled = false
        })
    })

    const banButton = document.createElement('button')
    banButton.type = 'button'
    banButton.className = 'ban-button'
    banButton.textContent = 'Ban'
    banButton.addEventListener('click', () => {
      banButton.disabled = true
      setError(null)

      void banPlayer(name)
        .then(() => refresh())
        .catch((error) => {
          setError(error instanceof Error ? error.message : `Failed to ban ${name}`)
        })
        .finally(() => {
          banButton.disabled = false
        })
    })

    const actions = document.createElement('div')
    actions.className = 'player-actions'
    actions.append(kickButton, banButton)

    li.append(nameSpan, actions)
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

restartAdminButton?.addEventListener('click', () => {
  const confirmed = window.confirm(
    'Restart minecraft-admin service now? This will briefly interrupt the dashboard API.'
  )
  if (!confirmed) {
    return
  }

  restartAdminButton.disabled = true
  setError(null)

  void restartAdminService()
    .then(() => {
      setTimeout(() => {
        void refresh()
      }, 2500)
    })
    .catch((error) => {
      setError(
        error instanceof Error ? error.message : 'Failed to restart minecraft-admin service'
      )
    })
    .finally(() => {
      restartAdminButton.disabled = false
    })
})

backupButton?.addEventListener('click', () => {
  const confirmed = window.confirm('Create a world backup tar.gz now?')
  if (!confirmed) {
    return
  }

  backupButton.disabled = true
  setError(null)
  if (backupLine) {
    backupLine.textContent = 'Backup: creating archive...'
  }

  void createBackup()
    .then((backup) => {
      const noteSuffix =
        backup.notes && backup.notes.length > 0 ? ` (${backup.notes.join('; ')})` : ''
      if (backupLine) {
        backupLine.textContent =
          `Backup: saved ${backup.archive_path} (${formatBytes(backup.size_bytes)})` + noteSuffix
      }
    })
    .catch((error) => {
      if (backupLine) {
        backupLine.textContent = 'Backup: failed'
      }
      setError(error instanceof Error ? error.message : 'Failed to create world backup')
    })
    .finally(() => {
      backupButton.disabled = false
    })
})

void refresh()
setInterval(() => {
  void refresh()
}, 15000)
