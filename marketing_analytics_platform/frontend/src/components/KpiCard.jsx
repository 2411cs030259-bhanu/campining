import React from "react";

export default function KpiCard({ label, value, accent }) {
  return (
    <div className={`kpi-card ${accent ? "kpi-card-" + accent : ""}`}>
      <div className="kpi-label">{label}</div>
      <div className="kpi-value">{value}</div>
    </div>
  );
}
