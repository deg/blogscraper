import { Layout, Menu } from 'antd'
import { BrowserRouter, Route, Routes, Link } from 'react-router-dom'

import PageContainer from './components/PageContainer'
import ScrapePage from './pages/ScrapePage'
import DocsPage from './pages/DocsPage'
import ExportPage from './pages/ExportPage'

const { Header, Content } = Layout

const App = () => (
  <BrowserRouter>
    <Layout style={{ minHeight: '100vh' }}>
      <Header>
        <Menu theme="dark" mode="horizontal" items={[
            { key: 'scrape', label: <Link to="/">Scrape</Link> },
            { key: 'docs', label: <Link to="/docs">Docs</Link> },
            { key: 'export', label: <Link to="/export">Export</Link> },
          ]}>
        </Menu>
      </Header>
      <Content style={{ padding: '24px' }}>
        <PageContainer>
          <Routes>
            <Route path="/" element={<ScrapePage />} />
            <Route path="/docs" element={<DocsPage />} />
            <Route path="/export" element={<ExportPage />} />
          </Routes>
        </PageContainer>
      </Content>
    </Layout>
  </BrowserRouter>
)

export default App
