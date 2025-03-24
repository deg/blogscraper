import { Button, message, Typography } from 'antd'
import { useEffect, useRef, useState } from 'react'
import {
  useStartScrapeScrapePost,
  useScrapeStatusScrapeStatusTaskIdGet,
} from '../api/orval'

const { Title, Paragraph } = Typography

const ScrapeStatus = ({ taskId }: { taskId: string }) => {
  const {
    data: status,
    isLoading,
    refetch,
  } = useScrapeStatusScrapeStatusTaskIdGet(taskId)

  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    const shouldContinue = (s?: string) =>
      s !== 'completed' && !s?.startsWith('failed:')

    if (shouldContinue(status?.status)) {
      intervalRef.current = setInterval(() => {
        refetch()
      }, 500)
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
    }
  }, [status?.status, refetch])

  return (
    <Paragraph style={{ marginTop: 24 }}>
      Status for task <code>{taskId}</code>:&nbsp;
      {isLoading ? 'Loading…' : JSON.stringify(status)}
    </Paragraph>
  )
}

const ScrapePage = () => {
  const [taskId, setTaskId] = useState<string | null>(null)

  const { mutate: startScrape, isLoading: isStarting } = useStartScrapeScrapePost()

  const handleStart = () => {
    startScrape({}, {
      onSuccess: (res) => {
        const newTaskId = res?.task_id
        if (newTaskId) {
          setTaskId(newTaskId)
          message.success(`Started scrape task: ${newTaskId}`)
        } else {
          message.error('Missing task_id in response')
        }
      },
      onError: () => message.error('Failed to start scrape'),
    })
  }

  return (
    <div>
      <Title level={2}>Scrape Blogs</Title>
      <Button type="primary" loading={isStarting} onClick={handleStart}>
        Start Scrape
      </Button>

      {taskId && <ScrapeStatus taskId={taskId} />}
    </div>
  )
}

export default ScrapePage
