import { useState, useEffect } from 'react'

export const useDeviceMode = () => {
  // Detect initial mode
  const getInitialMode = () => {
    // Check localStorage first
    const savedMode = localStorage.getItem('deviceMode')
    if (savedMode) return savedMode

    // Auto-detect based on screen size and user agent
    const isMobileScreen = window.innerWidth <= 768
    const isMobileDevice = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
      navigator.userAgent
    )
    
    return (isMobileScreen || isMobileDevice) ? 'mobile' : 'desktop'
  }

  const [mode, setMode] = useState(getInitialMode())

  useEffect(() => {
    // Save to localStorage when mode changes
    localStorage.setItem('deviceMode', mode)
    
    // Add mode class to body for CSS styling
    document.body.className = `mode-${mode}`
  }, [mode])

  useEffect(() => {
    // Re-detect on window resize (debounced)
    let timeoutId
    const handleResize = () => {
      clearTimeout(timeoutId)
      timeoutId = setTimeout(() => {
        // Only auto-switch if user hasn't manually set a preference
        const hasManualPreference = localStorage.getItem('deviceModeManual')
        if (!hasManualPreference) {
          const newMode = window.innerWidth <= 768 ? 'mobile' : 'desktop'
          if (newMode !== mode) {
            setMode(newMode)
          }
        }
      }, 250)
    }

    window.addEventListener('resize', handleResize)
    return () => {
      window.removeEventListener('resize', handleResize)
      clearTimeout(timeoutId)
    }
  }, [mode])

  const toggleMode = () => {
    const newMode = mode === 'mobile' ? 'desktop' : 'mobile'
    setMode(newMode)
    localStorage.setItem('deviceModeManual', 'true')
  }

  const resetToAuto = () => {
    localStorage.removeItem('deviceModeManual')
    setMode(getInitialMode())
  }

  return { mode, toggleMode, resetToAuto, isMobile: mode === 'mobile' }
}
