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
      // Allow browser / Axios to set proper boundary
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
 * Retrieves past verification result by ID.
 * @param {number} verificationId
 */
export async function getVerificationById(verificationId) {
  const response = await API.get(`/api/verifications/${verificationId}`);
  return response.data;
}

export default API;