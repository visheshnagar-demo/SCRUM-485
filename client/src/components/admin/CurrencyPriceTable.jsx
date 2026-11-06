import React from "react";
import { Switch } from "@headlessui/react";
import { Edit, Trash2 } from "lucide-react";
import LocalizedPriceDisplay from "../common/LocalizedPriceDisplay";

const CurrencyPriceTable = ({ prices, onEdit, onDelete, onToggleActive }) => {
  return (
    <div className="bg-white shadow-md rounded-lg overflow-hidden">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Currency Code
            </th>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Price
            </th>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Is Active
            </th>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {prices.map((priceEntry) => (
            <tr key={priceEntry.id}>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {priceEntry.currency_code}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <LocalizedPriceDisplay
                  price={priceEntry.price}
                  currencyCode={priceEntry.currency_code}
                />
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <Switch
                  checked={priceEntry.is_active}
                  onChange={(checked) => onToggleActive(priceEntry.id, checked)}
                  className={`${priceEntry.is_active ? "bg-success" : "bg-gray-200"}
                    relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-success focus:ring-offset-2`}
                >
                  <span className="sr-only">Toggle active status</span>
                  <span
                    className={`${priceEntry.is_active ? "translate-x-6" : "translate-x-1"}
                      inline-block h-4 w-4 transform rounded-full bg-white transition-transform`}
                  />
                </Switch>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button
                  onClick={() => onEdit(priceEntry)}
                  className="text-accent hover:text-blue-900 mr-3"
                >
                  <Edit size={20} />
                </button>
                <button
                  onClick={() => onDelete(priceEntry.id)}
                  className="text-error hover:text-red-900"
                >
                  <Trash2 size={20} />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default CurrencyPriceTable;
