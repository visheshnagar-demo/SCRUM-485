import React from "react";
import CurrencyRow from "./CurrencyRow";

const CurrencyTable = ({
  currencies,
  onEdit,
  onDelete,
  onToggleBase,
  onToggleActive,
}) => {
  return (
    <div className="bg-white shadow-md rounded-lg overflow-hidden">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Code
            </th>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Symbol
            </th>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Is Base
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
          {currencies.map((currency) => (
            <CurrencyRow
              key={currency.code}
              currency={currency}
              onEdit={onEdit}
              onDelete={onDelete}
              onToggleBase={onToggleBase}
              onToggleActive={onToggleActive}
            />
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default CurrencyTable;
