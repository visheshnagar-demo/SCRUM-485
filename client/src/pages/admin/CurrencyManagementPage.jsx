import React, { useState, useEffect } from "react";
import AdminLayout from "../../components/common/AdminLayout";
import CurrencyTable from "../../components/admin/CurrencyTable";
import AddCurrencyModal from "../../components/admin/AddCurrencyModal";
import {
  getCurrencies,
  createCurrency,
  updateCurrency,
  deleteCurrency,
} from "../../services/api";
import { PlusCircle } from "lucide-react";

const CurrencyManagementPage = () => {
  const [currencies, setCurrencies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingCurrency, setEditingCurrency] = useState(null);

  useEffect(() => {
    fetchCurrencies();
  }, []);

  const fetchCurrencies = async () => {
    try {
      setLoading(true);
      const response = await getCurrencies();
      setCurrencies(response.data);
    } catch (err) {
      console.error("Failed to fetch currencies:", err);
      setError("Failed to load currencies.");
    } finally {
      setLoading(false);
    }
  };

  const handleSaveCurrency = async (currencyData) => {
    try {
      if (editingCurrency) {
        await updateCurrency(editingCurrency.id, currencyData);
      } else {
        await createCurrency(currencyData);
      }
      fetchCurrencies();
      setEditingCurrency(null);
    } catch (err) {
      console.error("Failed to save currency:", err);
      setError("Failed to save currency.");
    }
  };

  const handleDeleteCurrency = async (currencyId) => {
    if (window.confirm("Are you sure you want to delete this currency?")) {
      try {
        await deleteCurrency(currencyId);
        fetchCurrencies();
      } catch (err) {
        console.error("Failed to delete currency:", err);
        setError("Failed to delete currency.");
      }
    }
  };

  const handleEditCurrency = (currency) => {
    setEditingCurrency(currency);
    setIsModalOpen(true);
  };

  const handleToggleBase = async (currencyId) => {
    const currentCurrency = currencies.find((c) => c.id === currencyId);
    if (!currentCurrency) return;

    if (currentCurrency.is_base) {
      alert(
        "Cannot unset the base currency directly. Please designate another currency as base first.",
      );
      return;
    }

    if (
      window.confirm(
        "Are you sure you want to set this currency as the primary base currency? This will unset the current base currency.",
      )
    ) {
      try {
        // First, unset current base currency if any
        const currentBase = currencies.find((c) => c.is_base);
        if (currentBase && currentBase.id !== currencyId) {
          await updateCurrency(currentBase.id, { is_base: false });
        }
        // Then set the new base currency
        await updateCurrency(currencyId, { is_base: true });
        fetchCurrencies();
      } catch (err) {
        console.error("Failed to update base currency:", err);
        setError("Failed to update base currency.");
      }
    }
  };

  const handleToggleActive = async (currencyId) => {
    const currentCurrency = currencies.find((c) => c.id === currencyId);
    if (!currentCurrency) return;

    try {
      await updateCurrency(currencyId, {
        is_active: !currentCurrency.is_active,
      });
      fetchCurrencies();
    } catch (err) {
      console.error("Failed to update currency active status:", err);
      setError("Failed to update currency active status.");
    }
  };

  if (loading)
    return (
      <AdminLayout>
        <div className="text-center py-4">Loading currencies...</div>
      </AdminLayout>
    );
  if (error)
    return (
      <AdminLayout>
        <div className="text-error text-center py-4">Error: {error}</div>
      </AdminLayout>
    );

  return (
    <AdminLayout>
      <h1 className="text-3xl font-bold text-text-primary mb-6">
        Currency Management
      </h1>

      <div className="flex justify-end mb-4">
        <button
          onClick={() => {
            setEditingCurrency(null);
            setIsModalOpen(true);
          }}
          className="flex items-center space-x-2 bg-accent text-white px-4 py-2 rounded-md hover:bg-blue-600 transition-colors"
        >
          <PlusCircle size={20} />
          <span>Add New Currency</span>
        </button>
      </div>

      {currencies.length === 0 ? (
        <p className="text-text-secondary">No currencies defined yet.</p>
      ) : (
        <CurrencyTable
          currencies={currencies}
          onEdit={handleEditCurrency}
          onDelete={handleDeleteCurrency}
          onToggleBase={handleToggleBase}
          onToggleActive={handleToggleActive}
        />
      )}

      <AddCurrencyModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setEditingCurrency(null);
        }}
        onSave={handleSaveCurrency}
        initialData={editingCurrency}
      />
    </AdminLayout>
  );
};

export default CurrencyManagementPage;
