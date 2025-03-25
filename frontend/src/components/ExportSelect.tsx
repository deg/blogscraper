import { Select } from "antd"

const { Option } = Select

const ExportSelect = ({
  selected,
  onChange,
}: {
  selected: string | null
  onChange: (value: string) => void
}) => (
  <Select
    placeholder="Select an export format"
    style={{ width: 400 }}
    value={selected ?? undefined}
    onChange={onChange}
  >
    <Option value="listDocuments">List Documents</Option>
    <Option value="markdownFromDocuments">Markdown from Documents</Option>
    <Option value="googleDocFromDocuments">Google Doc from Documents</Option>
    <Option value="llmPromptFromDocuments">LLM Prompt from Documents</Option>
  </Select>
)

export default ExportSelect
