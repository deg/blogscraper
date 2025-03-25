import React, { useState } from "react";
import { Alert, Button, Input, Typography } from "antd";
import {
  useStartScrapeScrapeAuthCodePost,
  useScrapeStatusScrapeStatusTaskIdGet,
} from "../api/orval";

import { usePollingUntil } from "../hooks/usePollingUntil";
import MarkdownViewer from "../components/MarkdownViewer";

const { Paragraph } = Typography;

const ScrapeStatus = ({
  taskId,
  status,
  isLoading,
}: {
  taskId: string;
  status: any;
  isLoading: boolean;
}) => (
  <Paragraph style={{ marginTop: 24 }}>
    Status for task <code>{taskId}</code>:&nbsp;
    {isLoading ? "Loading…" : JSON.stringify(status)}
  </Paragraph>
);

const ScrapePage = () => {
  const [authCode, setAuthCode] = useState("");
  const [taskId, setTaskId] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const {
    data: status,
    isLoading: isStatusLoading,
    refetch,
  } = useScrapeStatusScrapeStatusTaskIdGet(taskId!, {
    enabled: !!taskId,
  });

  const { mutate: startScrape, isLoading: isStarting } =
    useStartScrapeScrapeAuthCodePost();

  usePollingUntil({
    shouldContinue: () =>
      !!taskId &&
      status?.status !== "completed" &&
      status?.status !== "not found" &&
      !status?.status?.startsWith("failed:"),
    action: () => refetch(),
    delay: 2000,
    deps: [taskId, status?.status, refetch],
  });

  const isRunning =
    status?.status &&
    status.status !== "completed" &&
    !status.status.startsWith("failed:");

  const handleStart = () => {
    startScrape(
      { authCode },
      {
        onSuccess: (res) => {
          const failure = res?.detail;
          const newTaskId = res?.task_id;
          if (failure) {
            setErrorMsg(`Incorrect auth code (${failure})`);
          } else if (newTaskId) {
            setTaskId(newTaskId);
            console.log(`Started scrape task: ${newTaskId}`);
          } else {
            console.error("Missing task_id in response");
          }
        },
        onError: (err: any) => {
          const msg = err?.response?.data?.detail || "Failed to start scrape";
          console.error(msg);
        },
      }
    );
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (errorMsg) setErrorMsg(null);
    setAuthCode(e.target.value);
  };

  return (
    <div>
      <MarkdownViewer markdown={`# Scrape Blogs

This action triggers a full scrape of all the blogs from the backend. It is
a reasonably expensive operation and can also trigger rate limits and other
unpleasantness.

We will automate this task soon, and relegate it to the backend. Until then,
this is available here, but is protected by an authorization code. If you need
to run this, contact [David Goldfarb](mailto:deg@degel.com).
`} />
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
  );
};

export default ScrapePage;
