const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || ""

function headers() {
  return {
    Authorization: `Bearer ${API_KEY}`,
  }
}

export async function getAionStatus() {
  const res = await fetch(`${API_BASE}/api/aion/status`, {
    headers: headers(),
  })
  if (!res.ok) throw new Error(`Aion status error: ${res.status}`)
  return res.json()
}

export async function initializeAion() {
  const res = await fetch(`${API_BASE}/api/aion/initialize`, {
    method: "POST",
    headers: headers(),
  })
  if (!res.ok) throw new Error(`Aion init error: ${res.status}`)
  return res.json()
}

export async function getAionSkills() {
  const res = await fetch(`${API_BASE}/api/aion/skills`, {
    headers: headers(),
  })
  if (!res.ok) throw new Error(`Aion skills error: ${res.status}`)
  return res.json()
}

export async function getAionMcps() {
  const res = await fetch(`${API_BASE}/api/aion/mcps`, {
    headers: headers(),
  })
  if (!res.ok) throw new Error(`Aion MCPs error: ${res.status}`)
  return res.json()
}

export async function getAionAgents() {
  const res = await fetch(`${API_BASE}/api/aion/agents`, {
    headers: headers(),
  })
  if (!res.ok) throw new Error(`Aion agents error: ${res.status}`)
  return res.json()
}

export async function getAionCapabilities() {
  const res = await fetch(`${API_BASE}/api/aion/capabilities`, {
    headers: headers(),
  })
  if (!res.ok) throw new Error(`Aion capabilities error: ${res.status}`)
  return res.json()
}

export async function getPendingApprovals() {
  const res = await fetch(`${API_BASE}/api/aion/approvals/pending`, {
    headers: headers(),
  })
  if (!res.ok) throw new Error(`Aion approvals error: ${res.status}`)
  return res.json()
}

export async function approveAction(approvalId: string, decision: "approve" | "reject") {
  const res = await fetch(`${API_BASE}/api/aion/approve`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...headers(),
    },
    body: JSON.stringify({ approval_id: approvalId, decision }),
  })
  if (!res.ok) throw new Error(`Aion approve error: ${res.status}`)
  return res.json()
}

export async function toggleSkill(skillName: string) {
  const res = await fetch(`${API_BASE}/api/aion/skills/${skillName}/toggle`, {
    method: "POST",
    headers: headers(),
  })
  if (!res.ok) throw new Error(`Aion toggle skill error: ${res.status}`)
  return res.json()
}
