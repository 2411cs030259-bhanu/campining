import React from "react";
import AppLayout from "../components/AppLayout";
import { useAuth } from "../context/AuthContext";

export default function Profile() {
  const { user } = useAuth();

  return (
    <AppLayout>
      <div className="page-header">
        <h1>Profile</h1>
        <p className="page-subtitle">Your account details.</p>
      </div>

      <div className="profile-card">
        <div className="profile-avatar">{user?.username?.[0]?.toUpperCase()}</div>
        <div>
          <div className="profile-field">
            <span className="profile-label">Username</span>
            <span>{user?.username}</span>
          </div>
          <div className="profile-field">
            <span className="profile-label">User ID</span>
            <span>{user?.id}</span>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
