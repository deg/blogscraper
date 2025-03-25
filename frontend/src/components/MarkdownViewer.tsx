import React from 'react'
import ReactMarkdown from 'react-markdown'

type Props = {
  markdown: string
}

const MarkdownViewer: React.FC<Props> = ({ markdown }) => (
  <div style={{ padding: '1em' }}>
    <ReactMarkdown>{markdown}</ReactMarkdown>
  </div>
)

export default MarkdownViewer
