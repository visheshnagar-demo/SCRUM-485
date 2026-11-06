import React, { useState, Fragment, useEffect } from "react";
import { Dialog, Transition, Switch } from "@headlessui/react";
import { useCurrency } from "../../context/CurrencyContext";

const AddProductPriceModal = ({
  isOpen,
  onClose,
  onSave,
  initialData = {},
}) => {
  const {
    availableCurrencies,
    loading: currenciesLoading,
    error: currenciesError,
  } = useCurrency();
  const [currencyCode, setCurrencyCode] = useState(
    initialData.currency_code || "",
  );
  const [price, setPrice] = useState(initialData.price || "");
  const [isActive, setIsActive] = useState(initialData.is_active || true);

  useEffect(() => {
    if (
      isOpen &&
      !initialData.currency_code &&
      availableCurrencies.length > 0
    ) {
      setCurrencyCode(availableCurrencies[0].code); // Default to first available currency
    }
  }, [isOpen, initialData, availableCurrencies]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave({
      currency_code: currencyCode,
      price: parseFloat(price),
      is_active: isActive,
    });
    onClose();
  };

  if (currenciesLoading) return null; // Or a loading spinner
  if (currenciesError)
    return (
      <div className="text-error">
        Error loading currencies: {currenciesError}
      </div>
    );

  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-10" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black bg-opacity-25" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4 text-center">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
                <Dialog.Title
                  as="h3"
                  className="text-lg font-medium leading-6 text-gray-900"
                >
                  {initialData.id
                    ? "Edit Product Price"
                    : "Add New Product Price"}
                </Dialog.Title>
                <div className="mt-4">
                  <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                      <label
                        htmlFor="currencyCode"
                        className="block text-sm font-medium text-gray-700"
                      >
                        Currency
                      </label>
                      <select
                        id="currencyCode"
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-accent focus:ring-accent sm:text-sm"
                        value={currencyCode}
                        onChange={(e) => setCurrencyCode(e.target.value)}
                        required
                        disabled={!!initialData.id} // Disable currency editing for existing prices
                      >
                        {availableCurrencies.map((currency) => (
                          <option key={currency.code} value={currency.code}>
                            {currency.code} ({currency.symbol})
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label
                        htmlFor="price"
                        className="block text-sm font-medium text-gray-700"
                      >
                        Price
                      </label>
                      <input
                        type="number"
                        id="price"
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-accent focus:ring-accent sm:text-sm"
                        value={price}
                        onChange={(e) => setPrice(e.target.value)}
                        step="0.01"
                        min="0"
                        required
                      />
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-700">
                        Is Active
                      </span>
                      <Switch
                        checked={isActive}
                        onChange={setIsActive}
                        className={`${isActive ? "bg-success" : "bg-gray-200"}
                          relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-success focus:ring-offset-2`}
                      >
                        <span className="sr-only">Toggle active status</span>
                        <span
                          className={`${isActive ? "translate-x-6" : "translate-x-1"}
                            inline-block h-4 w-4 transform rounded-full bg-white transition-transform`}
                        />
                      </Switch>
                    </div>
                    <div className="mt-4 flex justify-end space-x-3">
                      <button
                        type="button"
                        className="inline-flex justify-center rounded-md border border-transparent bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
                        onClick={onClose}
                      >
                        Cancel
                      </button>
                      <button
                        type="submit"
                        className="inline-flex justify-center rounded-md border border-transparent bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2"
                      >
                        {initialData.id ? "Update" : "Add"}
                      </button>
                    </div>
                  </form>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
};

export default AddProductPriceModal;
