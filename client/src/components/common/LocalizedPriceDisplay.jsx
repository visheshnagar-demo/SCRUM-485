import React from "react";
import { useCurrency } from "../../context/CurrencyContext";

const LocalizedPriceDisplay = ({ price, currencyCode }) => {
  const { selectedCurrency, availableCurrencies } = useCurrency();

  // Fallback to the provided currencyCode if selectedCurrency is not set or doesn't match
  const displayCurrency =
    selectedCurrency &&
    (selectedCurrency.code === currencyCode || !currencyCode)
      ? selectedCurrency
      : availableCurrencies.find((curr) => curr.code === currencyCode);

  if (!displayCurrency) {
    return (
      <span>
        {price} {currencyCode}
      </span>
    ); // Fallback to raw display if currency not found
  }

  // Basic formatting, can be enhanced with Intl.NumberFormat for full localization
  return (
    <span>
      {displayCurrency.symbol} {parseFloat(price).toFixed(2)}
    </span>
  );
};

export default LocalizedPriceDisplay;
