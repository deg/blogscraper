import { useState } from "react"
import {
  useListDocumentsListDocumentsGet,
  useMarkdownFromDocumentsMarkdownFromDocumentsGet,
  useGoogleDocFromDocumentsGoogleDocFromDocumentsGet,
  useLlmPromptFromDocumentsLlmPromptFromDocumentsGet,
} from "../api/orval"
import ExportUI from "./ExportUI"

const ExportRunner = ({ selected }: { selected: string }) => {
  const [params, setParams] = useState({
    start_date: "",
    end_date: "",
    match_string: "",
  })

  switch (selected) {
    case "listDocuments": {
      const { data, isLoading, error, refetch } = useListDocumentsListDocumentsGet(
        params,
        { query: { enabled: false } }
      )
      return <ExportUI {...{ data, isLoading, error, refetch, setQueryParams: setParams }} />
    }

    case "markdownFromDocuments": {
      const { data, isLoading, error, refetch } = useMarkdownFromDocumentsMarkdownFromDocumentsGet(
        params,
        { query: { enabled: false } }
      )
      return <ExportUI {...{ data, isLoading, error, refetch, setQueryParams: setParams }} />
    }

    case "googleDocFromDocuments": {
      const { data, isLoading, error, refetch } = useGoogleDocFromDocumentsGoogleDocFromDocumentsGet(
        params,
        { query: { enabled: false } }
      )
      return <ExportUI {...{ data, isLoading, error, refetch, setQueryParams: setParams }} />
    }

    case "llmPromptFromDocuments": {
      const { data, isLoading, error, refetch } = useLlmPromptFromDocumentsLlmPromptFromDocumentsGet(
        params,
        { query: { enabled: false } }
      )
      return <ExportUI {...{ data, isLoading, error, refetch, setQueryParams: setParams }} />
    }

    default:
      return null
  }
}

export default ExportRunner
