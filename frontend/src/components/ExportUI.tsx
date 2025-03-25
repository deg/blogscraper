import { useState, useEffect } from "react";
import { Button, DatePicker, Input, Typography, Space, message } from "antd";
import { CopyOutlined, DownloadOutlined } from "@ant-design/icons";
import dayjs from "dayjs";

const { Text, Title } = Typography;
const { RangePicker } = DatePicker;

type Props = {
  refetch: () => void;
  setQueryParams: (params: {
    start_date?: string;
    end_date?: string;
    match_string?: string;
  }) => void;
  data: unknown;
  isLoading: boolean;
  error: unknown;
};

const ExportUI = ({
  refetch,
  setQueryParams,
  data,
  isLoading,
  error,
}: Props) => {
  const [range, setRange] = useState<[dayjs.Dayjs, dayjs.Dayjs]>();
  const [match, setMatch] = useState("");

  // Prefill last 7 days
  useEffect(() => {
    const end = dayjs();
    const start = end.subtract(7, "day");
    setRange([start, end]);
  }, []);

  const isReady = range?.[0] && range?.[1];

  const handleRun = () => {
    if (!isReady) {
      message.error("Please select a date range before running the query.");
      return;
    }

    setQueryParams({
      start_date: range[0].format("YYYY-MM-DD"),
      end_date: range[1].format("YYYY-MM-DD"),
      match_string: match,
    });

    refetch();
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(data);
    message.success("Copied to clipboard");
  };

  const handleDownload = () => {
    const blob = new Blob([data], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "export.json";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <Space direction="vertical" size="middle" style={{ width: "100%" }}>
      <RangePicker
        value={range}
        onChange={(val) =>
          setRange(
            val && val.length === 2
              ? (val as [dayjs.Dayjs, dayjs.Dayjs])
              : undefined
          )
        }
      />
      <Input
        placeholder="match_string"
        value={match}
        onChange={(e) => setMatch(e.target.value)}
        style={{ width: 300 }}
      />
      <Button onClick={handleRun} disabled={!isReady}>
        Run Query
      </Button>

      {isLoading && <Text>Loading...</Text>}
      {error && <Text type="danger">Error: {String(error)}</Text>}
      {data && (
        <>
          <Title level={5}>Result:</Title>
          <Space>
            <Button icon={<CopyOutlined />} onClick={handleCopy}>
              Copy
            </Button>
            <Button icon={<DownloadOutlined />} onClick={handleDownload}>
              Download
            </Button>
          </Space>
          <div
            style={{
              fontFamily: "monospace",
              whiteSpace: "pre-wrap",
              overflowWrap: "anywhere",
            }}
          >
            {String(data)}
          </div>
          <Space>
            <Button icon={<CopyOutlined />} onClick={handleCopy}>
              Copy
            </Button>
            <Button icon={<DownloadOutlined />} onClick={handleDownload}>
              Download
            </Button>
          </Space>
        </>
      )}
    </Space>
  );
};

export default ExportUI;
