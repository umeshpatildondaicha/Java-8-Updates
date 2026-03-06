import { useEffect, useRef, useCallback } from 'react'

// Mesh color presets for Niivue rgba255 format
function hexToRgba255(hex, alpha = 200) {
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  return [r, g, b, alpha]
}

function colorToRgba255(colorArr, alpha = 200) {
  if (!colorArr || colorArr.length < 3) return [150, 150, 200, alpha]
  return [colorArr[0], colorArr[1], colorArr[2], alpha]
}

export default function Viewer3D({ volumeUrl, meshes = [], viewMode = '3d' }) {
  const canvasRef = useRef(null)
  const nvRef = useRef(null)
  const loadedRef = useRef(false)

  const initNiivue = useCallback(async () => {
    if (!canvasRef.current || loadedRef.current) return

    try {
      const { Niivue } = await import('@niivue/niivue')

      const nv = new Niivue({
        show3Dcrosshair: true,
        backColor: [0.04, 0.07, 0.08, 1],
        crosshairColor: [0, 0.83, 1, 0.8],
        fontColor: [0.53, 0.75, 0.98, 1],
        isColorbar: false,
        isOrientCube: true,
        isRadiologicalConvention: false,
        dragMode: 1, // pan
        multiplanarLayout: 1, // grid
      })

      await nv.attachToCanvas(canvasRef.current)
      nvRef.current = nv
      loadedRef.current = true

      if (volumeUrl) {
        await nv.loadVolumes([{
          url: volumeUrl,
          colormap: 'gray',
          opacity: 1.0,
        }])
      }

      if (meshes && meshes.length > 0) {
        const meshDefs = meshes.map((m) => ({
          url: m.url,
          rgba255: colorToRgba255(m.color),
        }))
        await nv.loadMeshes(meshDefs)
      }

      // Set initial view
      if (viewMode === '3d') {
        nv.setSliceType(nv.sliceTypeRender)
      } else {
        nv.setSliceType(nv.sliceTypeMultiplanar)
      }

    } catch (err) {
      console.error('Niivue init error:', err)
    }
  }, [volumeUrl, meshes, viewMode])

  useEffect(() => {
    loadedRef.current = false
    initNiivue()
  }, [initNiivue])

  return (
    <div className="niivue-wrap">
      <canvas ref={canvasRef} style={{ width: '100%', height: '100%', display: 'block' }} />
    </div>
  )
}
