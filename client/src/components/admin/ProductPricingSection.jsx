import React, { useState, useEffect } from "react";
import {
  getProductPrices,
  createOrUpdateProductPrice,
  updateProductPrice,
  deleteProductPrice,
} from "../../services/api";
import CurrencyPriceTable from "./CurrencyPriceTable";
import AddProductPriceModal from "./AddProductPriceModal";
import { PlusCircle } from "lucide-react";

const ProductPricingSection = ({ productId }) => {
  const [prices, setPrices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingPrice, setEditingPrice] = useState(null);

  useEffect(() => {
    fetchProductPrices();
  }, [productId]);

  const fetchProductPrices = async () => {
    try {
      setLoading(true);
      const response = await getProductPrices(productId);
      setPrices(response.data);
    } catch (err) {
      console.error("Failed to fetch product prices:", err);
      setError("Failed to load product prices.");
    } finally {
      setLoading(false);
    }
  };

  const handleSavePrice = async (priceData) => {
    try {
      if (editingPrice) {
        await updateProductPrice(productId, editingPrice.id, priceData);
      } else {
        await createOrUpdateProductPrice(productId, priceData);
      }
      fetchProductPrices();
      setEditingPrice(null);
    } catch (err) {
      console.error("Failed to save product price:", err);
      setError("Failed to save product price.");
    }
  };

  const handleDeletePrice = async (priceId) => {
    if (window.confirm("Are you sure you want to delete this price entry?")) {
      try {
        await deleteProductPrice(productId, priceId);
        fetchProductPrices();
      } catch (err) {
        console.error("Failed to delete product price:", err);
        setError("Failed to delete product price.");
      }
    }
  };

  const handleEditPrice = (price) => {
    setEditingPrice(price);
    setIsModalOpen(true);
  };

  const handleToggleActive = async (priceId, isActive) => {
    try {
      await updateProductPrice(productId, priceId, { is_active: isActive });
      fetchProductPrices();
    } catch (err) {
      console.error("Failed to update price active status:", err);
      setError("Failed to update price active status.");
    }
  };

  if (loading)
    return <div className="text-center py-4">Loading pricing data...</div>;
  if (error)
    return <div className="text-error text-center py-4">Error: {error}</div>;

  return (
    <div className="bg-white p-6 rounded-lg shadow-md mt-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-semibold text-text-primary">
          Product Pricing
        </h2>
        <button
          onClick={() => {
            setEditingPrice(null);
            setIsModalOpen(true);
          }}
          className="flex items-center space-x-2 bg-accent text-white px-4 py-2 rounded-md hover:bg-blue-600 transition-colors"
        >
          <PlusCircle size={20} />
          <span>Add New Price</span>
        </button>
      </div>

      {prices.length === 0 ? (
        <p className="text-text-secondary">
          No prices configured for this product yet.
        </p>
      ) : (
        <CurrencyPriceTable
          prices={prices}
          onEdit={handleEditPrice}
          onDelete={handleDeletePrice}
          onToggleActive={handleToggleActive}
        />
      )}

      <AddProductPriceModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setEditingPrice(null);
        }}
        onSave={handleSavePrice}
        initialData={editingPrice}
      />
    </div>
  );
};

export default ProductPricingSection;
