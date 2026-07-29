import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";
import AppLayout from "../components/AppLayout";
import KpiCard from "../components/KpiCard";
import * as api from "../api/api";

const COLORS = ["#4f46e5", "#059669", "#d97706", "#dc2626", "#0891b2", "#7c3aed"];

export default function Reports() {
  const [analysis, setAnalysis] = useState(null);
  const [downloading, setDownloading] = useState(false);
  const [downloadMsg, setDownloadMsg] = useState("");

  useEffect(() => {
    const stashed = sessionStorage.getItem("latestAnalysis");
    if (stashed) {
      setAnalysis(JSON.parse(stashed));
    }
  }, []);

  const handleDownload = async () => {
    if (!analysis) return;
    setDownloading(true);
    setDownloadMsg("");
    try {
      const res = await api.generateReport(analysis, analysis.dataset_id);
      const url = api.getReportDownloadUrl(res.data.filename);
      window.open(url, "_blank");
    } catch (err) {
      setDownloadMsg(err.message || "Unable to generate the report right now.");
    } finally {
      setDownloading(false);
    }
  };

  if (!analysis) {
    return (
      <AppLayout>
        <div className="page-header">
          <h1>Reports</h1>
        </div>
        <div className="empty-state">
          <h3>No report to show yet</h3>
          <p>Upload a campaign dataset first to generate a report.</p>
          <Link to="/upload" className="btn btn-primary">
            Upload Data
          </Link>
        </div>
      </AppLayout>
    );
  }

  const { kpis, campaigns, platforms, insights } = analysis;

  return (
    <AppLayout>
      <div className="page-header">
        <h1>Analytics Report</h1>
        <p className="page-subtitle">Performance overview, campaign analysis, and insights.</p>
      </div>

      <section className="report-section">
        <h2>Performance Overview</h2>
        <div className="kpi-grid">
          <KpiCard label="Total Spend" value={`$${kpis.total_spend.toLocaleString()}`} accent="blue" />
          <KpiCard label="Total Revenue" value={`$${kpis.total_revenue.toLocaleString()}`} accent="green" />
          <KpiCard label="ROAS" value={kpis.roas} accent="purple" />
          <KpiCard label="CTR" value={`${kpis.ctr}%`} accent="orange" />
          <KpiCard label="CPC" value={`$${kpis.cpc}`} />
          <KpiCard label="CPA" value={`$${kpis.cpa}`} />
        </div>
      </section>

      <section className="report-section">
        <h2>Revenue by Campaign</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={campaigns}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="campaign" tick={{ fontSize: 12 }} />
            <YAxis />
            <Tooltip />
            <Bar dataKey="revenue" fill="#4f46e5" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </section>

      <section className="report-section">
        <h2>Spending Trend by Campaign</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={campaigns}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="campaign" tick={{ fontSize: 12 }} />
            <YAxis />
            <Tooltip />
            <Bar dataKey="ad_spend" fill="#d97706" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </section>

      <section className="report-section">
        <h2>Platform Performance</h2>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={platforms}
              dataKey="revenue"
              nameKey="platform"
              cx="50%"
              cy="50%"
              outerRadius={100}
              label={(entry) => entry.platform}
            >
              {platforms.map((entry, index) => (
                <Cell key={entry.platform} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </section>

      <section className="report-section">
        <h2>Insights</h2>
        <ul className="insights-list">
          {insights.map((insight, i) => (
            <li key={i}>{insight}</li>
          ))}
        </ul>
      </section>

      {downloadMsg && <div className="alert alert-error">{downloadMsg}</div>}

      <button className="btn btn-primary" onClick={handleDownload} disabled={downloading}>
        {downloading ? "Preparing report..." : "Download Report (CSV)"}
      </button>
    </AppLayout>
  );
}
