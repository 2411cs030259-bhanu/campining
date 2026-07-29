import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Signup() {
  const { signup } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", email: "", password: "" });
  const [errors, setErrors] = useState({});
  const [serverError, setServerError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors({});
    setServerError("");
    setSubmitting(true);
    try {
      await signup(form.username, form.password, form.email);
      navigate("/dashboard");
    } catch (err) {
      if (err.errors) setErrors(err.errors);
      setServerError(err.message || "Unable to create your account.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="auth-page">
      <form className="auth-card" onSubmit={handleSubmit}>
        <div className="auth-brand">Marketing Analytics Platform</div>
        <h1>Create your account</h1>
        <p className="auth-subtitle">Start analyzing your marketing campaigns in minutes.</p>

        {serverError && <div className="alert alert-error">{serverError}</div>}

        <label className="field">
          <span>Username</span>
          <input
            name="username"
            value={form.username}
            onChange={handleChange}
            placeholder="yourusername"
            autoComplete="username"
          />
          {errors.username && <span className="field-error">{errors.username}</span>}
        </label>

        <label className="field">
          <span>Email (optional)</span>
          <input
            name="email"
            value={form.email}
            onChange={handleChange}
            placeholder="you@company.com"
            autoComplete="email"
          />
          {errors.email && <span className="field-error">{errors.email}</span>}
        </label>

        <label className="field">
          <span>Password</span>
          <input
            type="password"
            name="password"
            value={form.password}
            onChange={handleChange}
            placeholder="At least 8 characters"
            autoComplete="new-password"
          />
          {errors.password && <span className="field-error">{errors.password}</span>}
        </label>

        <button className="btn btn-primary btn-block" type="submit" disabled={submitting}>
          {submitting ? "Creating account..." : "Sign Up"}
        </button>

        <p className="auth-switch">
          Already have an account? <Link to="/login">Log in</Link>
        </p>
      </form>
    </div>
  );
}
