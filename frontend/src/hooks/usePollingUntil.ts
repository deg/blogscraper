import { useEffect, useRef } from 'react'

export const usePollingUntil = ({
  shouldContinue,
  action,
  delay = 1000,
  deps = [],
}: {
  shouldContinue: () => boolean
  action: () => void
  delay?: number
  deps?: any[]
}) => {
  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    if (shouldContinue()) {
      intervalRef.current = setInterval(action, delay)
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
    }
  }, [shouldContinue, action, delay, ...deps])
}
