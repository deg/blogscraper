import { Alert, Button, Input, message, Typography } from 'antd'
import { useEffect, useRef, useState } from 'react'
import {
  useStartScrapeScrapeAuthCodePost,
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
  const [authCode, setAuthCode] = useState('')
  const [taskId, setTaskId] = useState<string | null>(null)
  const [errorMsg, setErrorMsg] = useState<string | null>(null);


  const {
    data: status,
    isLoading: isStatusLoading,
    refetch,
  } = useScrapeStatusScrapeStatusTaskIdGet(taskId!, {
    enabled: !!taskId,
  })

  const { mutate: startScrape, isLoading: isStarting } = useStartScrapeScrapeAuthCodePost()

  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  usePollingUntil({
    shouldContinue: () =>
      !!taskId &&
      status?.status !== 'completed' &&
      status?.status !== 'not found' &&
      !status?.status?.startsWith('failed:'),
    action: () => refetch(),
    delay: 500,
    deps: [taskId, status?.status, refetch],
  })

  const isRunning =
    status?.status && status.status !== 'completed' && !status.status.startsWith('failed:')

  const handleStart = () => {
    startScrape({authCode}, {
      onSuccess: (res) => {
        const failure = res?.detail
        const newTaskId = res?.task_id
        if (failure) {
          setErrorMsg(`Incorrect auth code (${failure})`)}
        else if (newTaskId) {
          setTaskId(newTaskId)
          console.log(`Started scrape task: ${newTaskId}`)
        } else {
          console.error('Missing task_id in response')
        }
      },
      onError: (err: any) => {
        const msg = err?.response?.data?.detail || 'Failed to start scrape'
        console.error(msg)
      },
    })
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (errorMsg) setErrorMsg(null)
    setAuthCode(e.target.value)
  }

  return (
    <div>
      <Title level={2}>Scrape Blogs</Title>
      <Input.Password
        placeholder="Enter authorization code"
        value={authCode}
        disabled={isStarting || isRunning}
        onChange={handleChange}
        style={{ width: 300, marginBottom: 12 }}
      />
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
      {errorMsg && (
        <Alert
          message={errorMsg}
          type="warning"
          showIcon
          style={{ marginTop: 16 }}
        />
)}

    </div>
  )
}

export default ScrapePage
