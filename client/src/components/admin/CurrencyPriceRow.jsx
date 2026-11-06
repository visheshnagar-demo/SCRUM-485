import React, { useState, useEffect } from "react";
import { Switch } from "@headlessui/react";
import { Save, Trash2 } from "lucide-react";

const CurrencyPriceRow = ({ priceEntry, onSave, onDelete }) => {
  const [price, setPrice] = useState(priceEntry.price);
  const [isActive, setIsActive] = useState(priceEntry.is_active);

  useEffect(() => {
    setPrice(priceEntry.price);
    setIsActive(priceEntry.is_active);
  }, [priceEntry]);

  const handleSave = () => {
    onSave(priceEntry.currency_code, {
      price: parseFloat(price),
      is_active: isActive,
    });
  };

  return (
    <tr className="border-b hover:bg-gray-50">
      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
        {priceEntry.currency_code}
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
        <input
          type="number"
          step="0.01"
          value={price}
          onChange={(e) => setPrice(e.target.value)}
          className="w-32 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
        />
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
        <Switch
          checked={isActive}
          onChange={setIsActive}
          className={`${
            isActive ? "bg-green-600" : "bg-gray-200"
          } relative inline-flex h-6 w-11 items-center rounded-full`}
        >
          <span className="sr-only">Toggle active status</span>
          <span
            className={`${
              isActive ? "translate-x-6" : "translate-x-1"
            } inline-block h-4 w-4 transform rounded-full bg-white transition`}
          />
        </Switch>
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
        <button
          onClick={handleSave}
          className="text-blue-600 hover:text-blue-900 mr-3"
          title="Save Price"
        >
          <Save size={18} />
        </button>
        <button
          onClick={() => onDelete(priceEntry.currency_code)}
          className="text-red-600 hover:text-red-900"
          title="Delete Price"
        >
          <Trash2 size={18} />
        </button>
      </td>
    </tr>
  );
};

export default CurrencyPriceRow;
