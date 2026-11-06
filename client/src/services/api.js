import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor for adding JWT token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);

// --- Authentication --- //
export const registerUser = (userData) =>
  api.post("/api/v1/auth/register", userData);
export const loginUser = (credentials) =>
  api.post("/api/v1/auth/login", credentials);
export const getMe = () => api.get("/api/v1/auth/me");

// --- Currencies --- //
export const getCurrencies = (isActive = null) => {
  return api.get("/api/v1/currencies", { params: { is_active: isActive } });
};
export const createCurrency = (currencyData) =>
  api.post("/api/v1/currencies", currencyData);
export const getCurrency = (idOrCode) =>
  api.get(`/api/v1/currencies/${idOrCode}`);
export const updateCurrency = (idOrCode, currencyData) =>
  api.put(`/api/v1/currencies/${idOrCode}`, currencyData);
export const deleteCurrency = (idOrCode) =>
  api.delete(`/api/v1/currencies/${idOrCode}`);

export const getExchangeRates = (isActive = null) => {
  return api.get("/api/v1/exchange-rates", { params: { is_active: isActive } });
};
export const createOrUpdateExchangeRate = (rateData) =>
  api.post("/api/v1/exchange-rates", rateData);

// --- Products & Pricing --- //
export const getProducts = (params) => api.get("/api/v1/products", { params });
export const createProduct = (productData) =>
  api.post("/api/v1/products", productData);
export const getProduct = (productId, currency = null) => {
  return api.get(`/api/v1/products/${productId}`, { params: { currency } });
};
export const updateProduct = (productId, productData) =>
  api.put(`/api/v1/products/${productId}`, productData);
export const deleteProduct = (productId) =>
  api.delete(`/api/v1/products/${productId}`);

export const getProductPrices = (productId) =>
  api.get(`/api/v1/products/${productId}/prices`);
export const createOrUpdateProductPrice = (productId, priceData) =>
  api.post(`/api/v1/products/${productId}/prices`, priceData);
export const updateProductPrice = (productId, priceIdOrCode, priceData) =>
  api.put(`/api/v1/products/${productId}/prices/${priceIdOrCode}`, priceData);
export const deleteProductPrice = (productId, priceIdOrCode) =>
  api.delete(`/api/v1/products/${productId}/prices/${priceIdOrCode}`);

export const getLocalizedProductPrice = (productId, currencyCode = null) => {
  return api.get(`/api/v1/products/${productId}/price`, {
    params: { currency_code: currencyCode },
  });
};

export default api;
