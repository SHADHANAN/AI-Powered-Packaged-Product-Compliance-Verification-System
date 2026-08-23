import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const API = axios.create({
  baseURL: API_BASE_URL,
  timeout: 45000,
});

/**
 * Executes full packaged-product compliance verification pipeline.
 * @param {File} imageFile - Uploaded package image file
 * @param {string} [strategy="standard"] - Preprocessing pipeline ('standard', 'grayscale_clahe', 'binarized', 'raw')
 * @returns {Promise<Object>} Verification pipeline response object
 */
export async function verifyProductImage(imageFile, strategy = "standard") {
  const formData = new FormData();
  formData.append("image", imageFile);
  if (strategy) {
    formData.append("preprocessing_strategy", strategy);
  }

  const response = await API.post("/api/verify", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
  return response.data;
}

/**
 * Checks API server health status.
 */
export async function checkHealth() {
  const response = await API.get("/api/health");
  return response.data;
}

/**
 * Retrieves past verification history.
 * @param {number} [skip=0]
 * @param {number} [limit=50]
 */
export async function getVerificationHistory(skip = 0, limit = 50) {
  const response = await API.get(`/api/verifications?skip=${skip}&limit=${limit}`);
  return response.data;
}

/**
 * Retrieves past verification result by ID.
 * @param {number} verificationId
 */
export async function getVerificationById(verificationId) {
  const response = await API.get(`/api/verifications/${verificationId}`);
  return response.data;
}

/**
 * Retrieves downloadable verification compliance audit report.
 * @param {number} verificationId
 */
export async function getVerificationReport(verificationId) {
  const response = await API.get(`/api/verifications/${verificationId}/report`);
  return response.data;
}

export default API;