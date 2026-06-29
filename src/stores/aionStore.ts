"use client"

import { create } from "zustand"

export interface AionSkill {
  id: string
  name: string
  description: string
  category: string
  is_active: boolean
  parameters: Record<string, unknown>[]
}

export interface AionMCP {
  id: string
  name: string
  description: string
  endpoint: string
  tools: { name: string; description: string }[]
  is_active: boolean
}

export interface AionAgent {
  id: string
  name: string
  description: string
  capabilities: string[]
}

export interface AionApproval {
  id: string
  action: string
  action_type: string
  details: Record<string, unknown>
  requested_by: string
  created_at: string
  status: "pending" | "approved" | "rejected"
}

interface AionState {
  connected: boolean
  initialized: boolean
  loading: boolean
  error: string | null
  skills: AionSkill[]
  mcps: AionMCP[]
  agents: AionAgent[]
  pendingApprovals: AionApproval[]
  setConnected: (v: boolean) => void
  setInitialized: (v: boolean) => void
  setLoading: (v: boolean) => void
  setError: (e: string | null) => void
  setSkills: (s: AionSkill[]) => void
  setMcps: (m: AionMCP[]) => void
  setAgents: (a: AionAgent[]) => void
  setPendingApprovals: (a: AionApproval[]) => void
  updateSkillActive: (name: string, active: boolean) => void
}

export const useAionStore = create<AionState>((set) => ({
  connected: false,
  initialized: false,
  loading: false,
  error: null,
  skills: [],
  mcps: [],
  agents: [],
  pendingApprovals: [],
  setConnected: (v) => set({ connected: v }),
  setInitialized: (v) => set({ initialized: v }),
  setLoading: (v) => set({ loading: v }),
  setError: (e) => set({ error: e }),
  setSkills: (s) => set({ skills: s }),
  setMcps: (m) => set({ mcps: m }),
  setAgents: (a) => set({ agents: a }),
  setPendingApprovals: (a) => set({ pendingApprovals: a }),
  updateSkillActive: (name, active) =>
    set((state) => ({
      skills: state.skills.map((s) =>
        s.name === name ? { ...s, is_active: active } : s,
      ),
    })),
}))
