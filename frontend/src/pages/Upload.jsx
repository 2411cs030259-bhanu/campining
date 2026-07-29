import React, { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import AppLayout from "../components/AppLayout";
import * as api from "../api/api";

export default function Upload() {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);

  const [dragging, setDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [status, setStatus] = useState("idle"); // idle | uploading | success | error
  const [message, setMessage] = useState("");

  const handleFiles = (files) => {
    const file = files?.[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith(".csv")) {
      setStatus("error");
      setMessage("Only CSV files are supported in Version 1.0.");
      return;
    }

    setSelectedFile(file);
    setStatus("idle");
    setMessage("");
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    handleFiles(e.dataTransfer.files);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    setStatus("uploading");
    setMessage("");

    try {
      const res = await api.uploadDataset(selectedFile);
      setStatus("success");
      setMessage("File processed successfully. Redirecting to your report...");
      // Stash the analysis for the Reports page to pick up.
      sessionStorage.setItem("latestAnalysis", JSON.stringify(res.data));
      setTimeout(() => navigate("/reports"), 900);
    } catch (err) {
      setStatus("error");
      setMessage(err.message || "Unable to process this file. Please check the required columns and try again.");
    }
  };

  return (
    <AppLayout>
      <div className="page-header">
        <h1>Upload Campaign Data</h1>
        <p className="page-subtitle">
          Upload a CSV with columns: campaign, platform, impressions, clicks, ad_spend, conversions, revenue.
        </p>
      </div>

      <div
        className={`dropzone ${dragging ? "dropzone-active" : ""}`}
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <div className="dropzone-icon">📁</div>
        <p className="dropzone-text">
          {selectedFile ? selectedFile.name : "Drag and drop your CSV file here, or click to browse"}
        </p>
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv"
          hidden
          onChange={(e) => handleFiles(e.target.files)}
        />
      </div>

      {message && (
        <div className={`alert ${status === "error" ? "alert-error" : "alert-success"}`}>{message}</div>
      )}

      <button
        className="btn btn-primary"
        onClick={handleUpload}
        disabled={!selectedFile || status === "uploading"}
      >
        {status === "uploading" ? "Processing..." : "Upload & Analyze"}
      </button>

      <div className="upload-example">
        <h3>Example row</h3>
        <table className="example-table">
          <thead>
            <tr>
              <th>campaign</th>
              <th>platform</th>
              <th>impressions</th>
              <th>clicks</th>
              <th>ad_spend</th>
              <th>conversions</th>
              <th>revenue</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Summer Sale</td>
              <td>Facebook</td>
              <td>50000</td>
              <td>2500</td>
              <td>1000</td>
              <td>200</td>
              <td>5000</td>
            </tr>
          </tbody>
        </table>
      </div>
    </AppLayout>
  );
}
