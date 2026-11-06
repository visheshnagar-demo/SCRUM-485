import React, { createContext, useState, useEffect, useContext } from "react";
import { getCurrencies } from "../services/api";

const CurrencyContext = createContext();

export const CurrencyProvider = ({ children }) => {
  const [selectedCurrency, setSelectedCurrency] = useState(null);
  const [availableCurrencies, setAvailableCurrencies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCurrencies = async () => {
      try {
        const response = await getCurrencies(true); // Fetch only active currencies
        setAvailableCurrencies(response.data);
        // Set a default currency if none is selected (e.g., the base currency or first active)
        if (response.data.length > 0 && !selectedCurrency) {
          const baseCurrency = response.data.find((curr) => curr.is_base);
          setSelectedCurrency(baseCurrency || response.data[0]);
        }
      } catch (err) {
        console.error("Failed to fetch currencies:", err);
        setError("Failed to load currencies.");
      } finally {
        setLoading(false);
      }
    };

    fetchCurrencies();
  }, []);

  const value = {
    selectedCurrency,
    setSelectedCurrency,
    availableCurrencies,
    loading,
    error,
  };

  return (
    <CurrencyContext.Provider value={value}>
      {children}
    </CurrencyContext.Provider>
  );
};

export const useCurrency = () => {
  const context = useContext(CurrencyContext);
  if (context === undefined) {
    throw new Error("useCurrency must be used within a CurrencyProvider");
  }
  return context;
};
