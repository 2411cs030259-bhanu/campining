/**
 * AuthContext.js
 * Global authentication state, backed by the Flask session cookie.
 * On first load it asks the backend "who am I?" so a page refresh
 * doesn't lose the logged-in state.
 */

import React, { createContext, useContext, useEffect, useState } from "react";
import * as api from "../api/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .getCurrentUser()
      .then((res) => setUser(res.data))
      .catch(() => setUser(null))
      .finally(() => setLoading(false));
  }, []);

  const login = async (username, password) => {
    const res = await api.login({ username, password });
    setUser(res.data);
    return res;
  };

  const signup = async (username, password, email) => {
    const res = await api.signup({ username, password, email });
    setUser(res.data);
    return res;
  };

  const logout = async () => {
    await api.logout().catch(() => {});
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
