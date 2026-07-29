/**
 * api.js
 * Single axios instance + all backend calls in one place.
 * Components should never call axios directly - they import
 * functions from here, so the API contract lives in one file.
 */

import axios from "axios";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:5000/api/v1";

const client = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // send session cookies
  headers: { "Content-Type": "application/json" },
});

// Unwraps the standard { success, message, data } shape and normalizes errors.
async function request(promise) {
  try {
    const response = await promise;
    return response.data;
  } catch (err) {
    if (err.response && err.response.data) {
      throw err.response.data;
    }
    throw { success: false, message: "Unable to reach the server. Please try again." };
  }
}

// ---- Auth ----
export const signup = (payload) => request(client.post("/signup", payload));
export const login = (payload) => request(client.post("/login", payload));
export const logout = () => request(client.post("/logout"));
export const getCurrentUser = () => request(client.get("/me"));

// ---- Upload / Analytics ----
export const uploadDataset = (file) => {
  const formData = new FormData();
  formData.append("file", file);
  return request(
    client.post("/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    })
  );
};

export const getDashboardSummary = () => request(client.get("/dashboard-summary"));

// ---- Reports ----
export const generateReport = (analysis, datasetId) =>
  request(client.post("/download", { analysis, dataset_id: datasetId }));

export const getReportDownloadUrl = (filename) => `${API_BASE_URL}/reports/${filename}`;

export const getReportHistory = () => request(client.get("/reports"));

// ---- Chatbot ----
export const askChatbot = (question) => request(client.post("/chatbot", { question }));

export default client;
