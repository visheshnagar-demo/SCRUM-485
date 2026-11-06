import React, { useState } from "react";
import { Dialog, Transition, Switch } from "@headlessui/react";
import { Fragment } from "react";

const AddCurrencyModal = ({ isOpen, onClose, onSave, initialData = {} }) => {
  const [code, setCode] = useState(initialData.code || "");
  const [symbol, setSymbol] = useState(initialData.symbol || "");
  const [isBase, setIsBase] = useState(initialData.is_base || false);
  const [isActive, setIsActive] = useState(initialData.is_active || true);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave({ code, symbol, is_base: isBase, is_active: isActive });
    onClose();
  };

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
                  {initialData.id ? "Edit Currency" : "Add New Currency"}
                </Dialog.Title>
                <div className="mt-4">
                  <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                      <label
                        htmlFor="code"
                        className="block text-sm font-medium text-gray-700"
                      >
                        Currency Code (ISO 4217)
                      </label>
                      <input
                        type="text"
                        id="code"
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-accent focus:ring-accent sm:text-sm"
                        value={code}
                        onChange={(e) => setCode(e.target.value.toUpperCase())}
                        maxLength="3"
                        required
                        disabled={!!initialData.id} // Disable code editing for existing currencies
                      />
                    </div>
                    <div>
                      <label
                        htmlFor="symbol"
                        className="block text-sm font-medium text-gray-700"
                      >
                        Symbol
                      </label>
                      <input
                        type="text"
                        id="symbol"
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-accent focus:ring-accent sm:text-sm"
                        value={symbol}
                        onChange={(e) => setSymbol(e.target.value)}
                        maxLength="10"
                        required
                      />
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-700">
                        Is Base Currency
                      </span>
                      <Switch
                        checked={isBase}
                        onChange={setIsBase}
                        className={`${isBase ? "bg-accent" : "bg-gray-200"}
                          relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2`}
                      >
                        <span className="sr-only">Set as base currency</span>
                        <span
                          className={`${isBase ? "translate-x-6" : "translate-x-1"}
                            inline-block h-4 w-4 transform rounded-full bg-white transition-transform`}
                        />
                      </Switch>
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

export default AddCurrencyModal;
