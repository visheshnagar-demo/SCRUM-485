import React from "react";
import { Switch } from "@headlessui/react";
import { Pencil, Trash2 } from "lucide-react";

const CurrencyRow = ({
  currency,
  onEdit,
  onDelete,
  onToggleBase,
  onToggleActive,
}) => {
  return (
    <tr className="border-b hover:bg-gray-50">
      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
        {currency.code}
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
        {currency.symbol}
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
        <Switch
          checked={currency.is_base}
          onChange={() => onToggleBase(currency.code)}
          className={`${
            currency.is_base ? "bg-blue-600" : "bg-gray-200"
          } relative inline-flex h-6 w-11 items-center rounded-full`}
        >
          <span className="sr-only">Set as base currency</span>
          <span
            className={`${
              currency.is_base ? "translate-x-6" : "translate-x-1"
            } inline-block h-4 w-4 transform rounded-full bg-white transition`}
          />
        </Switch>
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
        <Switch
          checked={currency.is_active}
          onChange={() => onToggleActive(currency.code)}
          className={`${
            currency.is_active ? "bg-green-600" : "bg-gray-200"
          } relative inline-flex h-6 w-11 items-center rounded-full`}
        >
          <span className="sr-only">Toggle active status</span>
          <span
            className={`${
              currency.is_active ? "translate-x-6" : "translate-x-1"
            } inline-block h-4 w-4 transform rounded-full bg-white transition`}
          />
        </Switch>
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
        <button
          onClick={() => onEdit(currency)}
          className="text-indigo-600 hover:text-indigo-900 mr-3"
          title="Edit Currency"
        >
          <Pencil size={18} />
        </button>
        <button
          onClick={() => onDelete(currency.code)}
          className="text-red-600 hover:text-red-900"
          title="Delete Currency"
        >
          <Trash2 size={18} />
        </button>
      </td>
    </tr>
  );
};

export default CurrencyRow;
