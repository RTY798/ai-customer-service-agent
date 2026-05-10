export interface AgentThought {
  agent: string
  status: 'running' | 'completed' | 'error'
  input?: string
  output?: string
  detail?: string
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'agent'
  content: string
  thoughts?: AgentThought[]
  ticket?: EscalationTicket | null
}

export interface EscalationTicket {
  ticket_id: string
  ticket_summary: string
  issue_category: string
  urgency: string
  detail: string
  suggested_action: string
  timestamp: string
}
