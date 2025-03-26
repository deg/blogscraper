import {
  BrowserRouter,
  Link,
  Routes,
  Route,
  useLocation,
} from "react-router-dom";
import { Layout, Menu } from "antd";

import ExportPage from "./pages/ExportPage";
import DocsPage from "./pages/DocsPage";
import ScrapePage from "./pages/ScrapePage";

const { Header, Content } = Layout;

const App = () => (
  <BrowserRouter>
    <AppInner />
  </BrowserRouter>
);
const AppInner = () => {
  const location = useLocation();
  const selectedKey =
    location.pathname === "/" ? "export" : location.pathname.slice(1);

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Header>
        <Menu
          theme="dark"
          mode="horizontal"
          selectedKeys={[selectedKey]}
          items={[
            { key: "export", label: <Link to="/">Query/Export</Link> },
            { key: "docs", label: <Link to="/docs">Google managment</Link> },
            { key: "scrape", label: <Link to="/scrape">Scrape</Link> },
          ]}
        />
      </Header>
      <Content style={{ padding: "24px" }}>
        <Routes>
          <Route path="/" element={<ExportPage />} />
          <Route path="/docs" element={<DocsPage />} />
          <Route path="/scrape" element={<ScrapePage />} />
        </Routes>
      </Content>
    </Layout>
  );
};

export default App;
