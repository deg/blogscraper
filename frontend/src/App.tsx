import { Layout, Menu } from 'antd'
import { BrowserRouter, Route, Routes, Link } from 'react-router-dom'
import ScrapePage from './pages/ScrapePage'
import DocsPage from './pages/DocsPage'
import ExportPage from './pages/ExportPage'

const { Header, Content } = Layout

const App = () => (
  <BrowserRouter>
    <Layout style={{ minHeight: '100vh' }}>
      <Header>
        <Menu theme="dark" mode="horizontal">
          <Menu.Item key="scrape"><Link to="/">Scrape</Link></Menu.Item>
          <Menu.Item key="docs"><Link to="/docs">Docs</Link></Menu.Item>
          <Menu.Item key="export"><Link to="/export">Export</Link></Menu.Item>
        </Menu>
      </Header>
      <Content style={{ padding: '24px' }}>
        <Routes>
          <Route path="/" element={<ScrapePage />} />
          <Route path="/docs" element={<DocsPage />} />
          <Route path="/export" element={<ExportPage />} />
        </Routes>
      </Content>
    </Layout>
  </BrowserRouter>
)

export default App
