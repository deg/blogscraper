import { useState } from "react"
import { Card } from "antd"
import ExportSelect from "../components/ExportSelect"
import ExportRunner from "../components/ExportRunner"

import MarkdownViewer from "../components/MarkdownViewer";


const helpText=`
# Exporting Cached Blog Posts

Use this page to explore and extract AI-related blog posts collected by Blogscraper.
You can generate outputs in multiple formats, whether you're skimming for URLs or
preparing inputs for downstream tools like LLMs or NotebookLM.

Each export accepts the following filters:

- **Date range**: Start and end date (inclusive).
- **Search string** *(optional)*: A Python-style regular expression to match content or URLs.

## Export Formats

You can choose from four export types:

- **List of URLs**
  A fast, minimal export that returns matching document links. Ideal for quick inspection
  or downstream scripting.

- **Markdown Document**
  Compiles the full content and metadata of all matching documents into a single Markdown file,
  complete with a table of contents.

- **Google Doc**
  Similar to the Markdown export, but generates a shareable Google Doc and returns the URL.
  Perfect for collaboration or reading on the go.

- **LLM Prompt** *(experimental)*
  Generates a structured prompt containing relevant document links. Intended for LLMs that
  can browse the web (e.g. ChatGPT with browsing). Still under development — may produce
  erratic or verbose results.

## Suggested Workflows

- **Start with “List of URLs”** to confirm your filters are working and the date range
  returns expected results.
- **Use “Markdown” or “Google Doc”** for deep dives, collaborative review, or to feed tools
  like [NotebookLM](https://notebooklm.google.com/).
- **Try “LLM Prompt”** when you're feeding a browsing-capable LLM — but be cautious. This is
  an experimental format and may confuse models not optimized for long structured prompts.

## Known Limits

- **Google Docs**: ~1 million characters max
- **NotebookLM**: ~3 million characters max

These limits are approximate and may change over time.

---

Let us know how you're using these exports — and what formats you'd like us to support next!
`;

const ExportPage = () => {
  const [selected, setSelected] = useState<string | null>(null)

  return (
    <>
    <MarkdownViewer markdown={helpText} />
    <Card title="Export">
      <ExportSelect selected={selected} onChange={setSelected} />
      <div style={{ marginTop: 24 }}>
        {selected && <ExportRunner selected={selected} />}
      </div>
    </Card>
    </>
  )
}

export default ExportPage
