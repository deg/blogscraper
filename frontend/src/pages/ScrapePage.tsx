import { Button, message, Typography } from 'antd'
import { useEffect, useRef, useState } from 'react'
import {
  useStartScrapeScrapePost,
  useScrapeStatusScrapeStatusTaskIdGet,
} from '../api/orval'

import { usePollingUntil } from '../hooks/usePollingUntil'

const { Title, Paragraph } = Typography

const ScrapeStatus = ({
  taskId,
  status,
  isLoading,
}: {
  taskId: string
  status: any
  isLoading: boolean
}) => (
  <Paragraph style={{ marginTop: 24 }}>
    Status for task <code>{taskId}</code>:&nbsp;
    {isLoading ? 'Loading…' : JSON.stringify(status)}
  </Paragraph>
)

const ScrapePage = () => {
  const [taskId, setTaskId] = useState<string | null>(null)

  const {
    data: status,
    isLoading: isStatusLoading,
    refetch,
  } = useScrapeStatusScrapeStatusTaskIdGet(taskId!, {
    enabled: !!taskId,
  })

  const { mutate: startScrape, isLoading: isStarting } = useStartScrapeScrapePost()

  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  usePollingUntil({
    shouldContinue: () =>
      !!taskId &&
      status?.status !== 'completed' &&
      !status?.status?.startsWith('failed:'),
    action: () => refetch(),
    delay: 500,
    deps: [taskId, status?.status, refetch],
  })


  const isRunning =
    status?.status && status.status !== 'completed' && !status.status.startsWith('failed:')

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
      <Button
        type="primary"
        loading={isStarting}
        disabled={isStarting || isRunning}
        onClick={handleStart}
      >
        Start Scrape
      </Button>

      {taskId && (
        <ScrapeStatus
          taskId={taskId}
          status={status}
          isLoading={isStatusLoading}
        />
      )}
    </div>
  )
}

export default ScrapePage
