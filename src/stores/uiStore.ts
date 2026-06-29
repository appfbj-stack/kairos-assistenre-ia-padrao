import { create } from "zustand"

type AvatarState = "idle" | "listening" | "thinking" | "speaking"
type Panel = "chat" | "home"

interface UIState {
  sidebarOpen: boolean
  activePanel: Panel
  avatarState: AvatarState
  toggleSidebar: () => void
  setSidebarOpen: (open: boolean) => void
  setActivePanel: (panel: Panel) => void
  setAvatarState: (state: AvatarState) => void
}

export const useUIStore = create<UIState>((set) => ({
  sidebarOpen: false,
  activePanel: "home",
  avatarState: "idle",
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  setActivePanel: (panel) => set({ activePanel: panel }),
  setAvatarState: (state) => set({ avatarState: state }),
}))
