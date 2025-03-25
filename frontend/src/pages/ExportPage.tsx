import { useState } from "react"
import { Card } from "antd"
import ExportSelect from "../components/ExportSelect"
import ExportRunner from "../components/ExportRunner"

const ExportPage = () => {
  const [selected, setSelected] = useState<string | null>(null)

  return (
    <Card title="Export">
      <ExportSelect selected={selected} onChange={setSelected} />
      <div style={{ marginTop: 24 }}>
        {selected && <ExportRunner selected={selected} />}
      </div>
    </Card>
  )
}

export default ExportPage
