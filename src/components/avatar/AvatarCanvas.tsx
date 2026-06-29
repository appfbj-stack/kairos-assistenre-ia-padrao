"use client"

import { useEffect, useRef } from "react"
import { useUIStore } from "@/stores/uiStore"

export function AvatarCanvas() {
  const avatarState = useUIStore((s) => s.avatarState)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const frameRef = useRef(0)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext("2d")
    if (!ctx) return

    const w = 200
    const h = 200
    canvas.width = w * 2
    canvas.height = h * 2
    ctx.scale(2, 2)

    let running = true

    const animate = () => {
      if (!running) return
      frameRef.current++
      ctx.clearRect(0, 0, w, h)

      const cx = w / 2
      const cy = h / 2
      const t = frameRef.current * 0.02

      let baseRadius = 40
      let pulseAmp = 2
      let rings = 3
      let rotationSpeed = 1
      let colorIntensity = 0.6

      if (avatarState === "listening") {
        pulseAmp = 6
        rings = 4
      } else if (avatarState === "thinking") {
        pulseAmp = 4
        rings = 5
        rotationSpeed = 2
        colorIntensity = 0.8
      } else if (avatarState === "speaking") {
        pulseAmp = 8
        rings = 4
        rotationSpeed = 1.5
        colorIntensity = 1
      }

      const pulse = Math.sin(t * 2) * pulseAmp
      const r = baseRadius + pulse

      for (let i = rings; i >= 0; i--) {
        const ringRadius = r + i * 18 + Math.sin(t * rotationSpeed + i * 0.8) * 4
        const alpha = colorIntensity * (1 - i / (rings + 1)) * 0.3

        const hue1 = 220 + Math.sin(t * 0.5 + i * 0.3) * 15
        const hue2 = 270 + Math.cos(t * 0.4 + i * 0.2) * 15

        const gradient = ctx.createConicGradient(t + i * 0.5, cx, cy)
        gradient.addColorStop(0, `hsla(${hue1}, 80%, 55%, ${alpha})`)
        gradient.addColorStop(0.3, `hsla(${hue2}, 70%, 50%, ${alpha * 0.5})`)
        gradient.addColorStop(0.6, `hsla(${hue1 + 20}, 80%, 60%, ${alpha})`)
        gradient.addColorStop(1, `hsla(${hue1}, 80%, 55%, ${alpha})`)

        ctx.beginPath()
        ctx.arc(cx, cy, ringRadius, 0, Math.PI * 2)
        ctx.strokeStyle = gradient
        ctx.lineWidth = 2.5 - i * 0.25
        ctx.stroke()
      }

      const coreGradient = ctx.createRadialGradient(cx - 5, cy - 5, 0, cx, cy, r * 0.5)
      coreGradient.addColorStop(0, `hsla(220, 80%, 65%, ${colorIntensity * 0.3})`)
      coreGradient.addColorStop(1, `hsla(270, 70%, 55%, ${colorIntensity * 0.1})`)
      ctx.beginPath()
      ctx.arc(cx, cy, r * 0.5, 0, Math.PI * 2)
      ctx.fillStyle = coreGradient
      ctx.fill()

      if (avatarState === "listening") {
        for (let i = 0; i < 3; i++) {
          const angle = t + (i * Math.PI * 2) / 3
          const waveR = r + 20 + Math.sin(t * 3 + i) * 10
          ctx.beginPath()
          ctx.arc(cx + Math.cos(angle) * waveR, cy + Math.sin(angle) * waveR, 3, 0, Math.PI * 2)
          ctx.fillStyle = `hsla(220, 80%, 70%, 0.4)`
          ctx.fill()
        }
      }

      frameRef.current = requestAnimationFrame(animate)
    }

    animate()

    return () => {
      running = false
      cancelAnimationFrame(frameRef.current)
    }
  }, [avatarState])

  return (
    <canvas
      ref={canvasRef}
      className="w-[200px] h-[200px]"
      aria-label={`Avatar estado: ${avatarState}`}
    />
  )
}
