import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import AppLayout from "../components/AppLayout";
import KpiCard from "../components/KpiCard";
import { useAuth } from "../context/AuthContext";
import * as api from "../api/api";

export default function Dashboard() {
  const { user } = useAuth();
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .getDashboardSummary()
      .then((res) => setSummary(res.data))
      .catch((err) => setError(err.message || "Unable to load dashboard data."))
      .finally(() => setLoading(false));
  }, []);

  const latest = summary?.latest_report;

  return (
    <AppLayout>
      <div className="page-header">
        <h1>Welcome back, {user?.username}</h1>
        <p className="page-subtitle">Here's a snapshot of your latest campaign performance.</p>
      </div>

      {loading && <div className="page-loading">Loading dashboard...</div>}
      {error && <div className="alert alert-error">{error}</div>}

      {!loading && !latest && (
        <div className="empty-state">
          <h3>No reports yet</h3>
          <p>Upload your first campaign dataset to see KPIs and insights here.</p>
          <Link to="/upload" className="btn btn-primary">
            Upload Data
          </Link>
        </div>
      )}

      {latest && (
        <>
          <div className="kpi-grid">
            <KpiCard label="Total Spend" value={`$${Number(latest.total_spend).toLocaleString()}`} accent="blue" />
            <KpiCard label="Total Revenue" value={`$${Number(latest.total_revenue).toLocaleString()}`} accent="green" />
            <KpiCard label="ROAS" value={Number(latest.roas).toFixed(2)} accent="purple" />
            <KpiCard label="CTR" value={`${Number(latest.ctr).toFixed(2)}%`} accent="orange" />
          </div>

          <div className="kpi-grid kpi-grid-secondary">
            <KpiCard label="CPC" value={`$${Number(latest.cpc).toFixed(2)}`} />
            <KpiCard label="CPA" value={`$${Number(latest.cpa).toFixed(2)}`} />
            <KpiCard label="Reports Generated" value={summary.total_reports} />
          </div>

          <div className="dashboard-actions">
            <Link to="/reports" className="btn btn-secondary">
              View Full Reports
            </Link>
            <Link to="/upload" className="btn btn-primary">
              Upload New Dataset
            </Link>
          </div>
        </>
      )}
    </AppLayout>
  );
}
