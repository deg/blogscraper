import { useState, useEffect } from "react";
import { Button, Modal, Table, message } from "antd";
import { DeleteOutlined } from "@ant-design/icons";

import {
  listGoogleDocsListGoogleDocsGet,
  deleteGoogleDocDeleteGoogleDocPost,
} from "../api/orval";

const DocsPage = () => {
  const [docs, setDocs] = useState([]);
  const [loading, setLoading] = useState(false);

  const loadDocs = async () => {
    setLoading(true);
    try {
      const res = await listGoogleDocsListGoogleDocsGet();
      setDocs(res || []);
    } catch (err) {
      message.error("Failed to fetch documents");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocs();
  }, []);

  const confirmDelete = async (id: string, name: string) => {
    const confirmed = window.confirm(`Delete ${name}?`);
    if (!confirmed) return;

    try {
      await deleteGoogleDocDeleteGoogleDocPost({ doc_id: id, name });
      message.success(`Deleted ${name}`);
      await loadDocs();
    } catch {
      message.error("Failed to delete document");
    }
  };

  const columns = [
    {
      title: "Name",
      dataIndex: "name",
      key: "name",
      render: (_: string, record: any) => (
        <a href={record.url} target="_blank" rel="noopener noreferrer">
          {record.name}
        </a>
      ),
    },
    {
      title: "Created",
      dataIndex: "createdTime",
      key: "createdTime",
    },
    {
      title: "Modified",
      dataIndex: "modifiedTime",
      key: "modifiedTime",
    },
    {
      title: "",
      key: "actions",
      render: (_: any, record: any) => (
        <DeleteOutlined
          onClick={() => confirmDelete(record.id, record.name)}
          style={{ color: "red", cursor: "pointer" }}
        />
      ),
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Button onClick={loadDocs} loading={loading} style={{ marginBottom: 16 }}>
        Refresh
      </Button>
      <Table
        rowKey="id"
        dataSource={docs}
        columns={columns}
        loading={loading}
        pagination={false}
      />
    </div>
  );
};

export default DocsPage;
