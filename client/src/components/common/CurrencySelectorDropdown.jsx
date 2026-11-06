import React, { useState } from "react";
import { useCurrency } from "../../context/CurrencyContext";
import { ChevronDown } from "lucide-react";

const CurrencySelectorDropdown = () => {
  const {
    selectedCurrency,
    setSelectedCurrency,
    availableCurrencies,
    loading,
    error,
  } = useCurrency();
  const [isOpen, setIsOpen] = useState(false);

  if (loading)
    return <div className="text-text-secondary">Loading currencies...</div>;
  if (error) return <div className="text-error">Error: {error}</div>;
  if (!selectedCurrency) return null; // Or a placeholder

  const handleCurrencyChange = (currency) => {
    setSelectedCurrency(currency);
    setIsOpen(false);
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 px-4 py-2 rounded-full bg-gray-100 border border-gray-300 text-text-primary hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-accent"
      >
        <span>
          {selectedCurrency.code} ({selectedCurrency.symbol})
        </span>
        <ChevronDown
          size={16}
          className={`transform transition-transform ${isOpen ? "rotate-180" : "rotate-0"}`}
        />
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-10">
          <ul className="py-1">
            {availableCurrencies.map((currency) => (
              <li
                key={currency.code}
                onClick={() => handleCurrencyChange(currency)}
                className="px-4 py-2 text-text-primary hover:bg-gray-100 cursor-pointer flex items-center justify-between"
              >
                <span>
                  {currency.code} ({currency.symbol})
                </span>
                {selectedCurrency.code === currency.code && (
                  <span className="text-accent font-semibold">&#10003;</span>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default CurrencySelectorDropdown;
