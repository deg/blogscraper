import { Button, message, Typography } from 'antd'
import { useStartScrapeScrapePost } from '../api/orval'

const { Title } = Typography

const ScrapePage = () => {
  const { mutate: startScrape, isLoading } = useStartScrapeScrapePost()

  const handleStart = () => {
    startScrape({}, {
      onSuccess: () => message.success('Scrape started!'),
      onError: () => message.error('Failed to start scrape'),
    })
  }

  return (
    <div>
      <Title level={2}>Scrape Blogs</Title>
      <Button type="primary" loading={isLoading} onClick={handleStart}>
        Start Scrape
      </Button>
    </div>
  )
}

export default ScrapePage
