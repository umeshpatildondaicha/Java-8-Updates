import { useState } from 'react'

export default function StructureList({ meshes, onVisibilityChange, onOpacityChange }) {
  const [hidden, setHidden] = useState(new Set())
  const [opacity, setOpacity] = useState({})

  const toggle = (name) => {
    const next = new Set(hidden)
    if (next.has(name)) next.delete(name)
    else next.add(name)
    setHidden(next)
    onVisibilityChange?.(name, !next.has(name))
  }

  const setOp = (name, val) => {
    setOpacity(prev => ({ ...prev, [name]: val }))
    onOpacityChange?.(name, val / 100)
  }

  if (!meshes || meshes.length === 0) return null

  return (
    <div className="panel" style={{ flex: 1, overflowY: 'auto' }}>
      <p className="panel-title">Segmented Structures ({meshes.length})</p>
      {meshes.map((mesh) => {
        const [r, g, b] = mesh.color || [150, 150, 200]
        const hex = `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`
        const isHidden = hidden.has(mesh.name)
        const op = opacity[mesh.name] ?? 80

        return (
          <div key={mesh.name}>
            <div className={`structure-item ${isHidden ? '' : 'active'}`}>
              <div className="structure-dot" style={{ background: hex }} />
              <span className="structure-name">{mesh.label || mesh.name}</span>
              <button
                className={`structure-toggle ${isHidden ? 'hidden' : ''}`}
                onClick={() => toggle(mesh.name)}
              >
                {isHidden ? 'Show' : 'Hide'}
              </button>
            </div>
            {!isHidden && (
              <div className="opacity-row" style={{ paddingLeft: 32, paddingRight: 10 }}>
                <span className="opacity-label">Opacity</span>
                <input
                  type="range" min="0" max="100" value={op}
                  onChange={(e) => setOp(mesh.name, Number(e.target.value))}
                />
                <span style={{ fontSize: 11, color: 'var(--text-3)', width: 28 }}>{op}%</span>
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
