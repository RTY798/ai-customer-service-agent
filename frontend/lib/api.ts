const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000'

export interface ChatResponse {
  reply: string
  intent: string
  thought_chain: Array<{
    agent: string
    status: string
    input?: string
    output?: string
    detail?: string
  }>
  escalation_ticket: Record<string, unknown> | null
}

export async function sendMessage(message: string): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: '请求失败' }))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }

  return res.json()
}
