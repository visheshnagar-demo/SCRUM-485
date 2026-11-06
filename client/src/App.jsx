import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { CurrencyProvider } from "./context/CurrencyContext";

// Admin Pages
import CurrencyManagementPage from "./pages/admin/CurrencyManagementPage";
import ProductEditPage from "./pages/admin/ProductEditPage";

// Customer Pages
import ProductListingPage from "./pages/customer/ProductListingPage";
import ProductDetailPage from "./pages/customer/ProductDetailPage";

function App() {
  return (
    <CurrencyProvider>
      <Router>
        <Routes>
          {/* Admin Routes */}
          <Route
            path="/admin/currencies"
            element={<CurrencyManagementPage />}
          />
          <Route
            path="/admin/products/:productId"
            element={<ProductEditPage />}
          />
          {/* Customer Routes */}
          <Route path="/products" element={<ProductListingPage />} />
          <Route path="/products/:productId" element={<ProductDetailPage />} />
          <Route path="/" element={<ProductListingPage />} />{" "}
          {/* Default route */}
        </Routes>
      </Router>
    </CurrencyProvider>
  );
}

export default App;
