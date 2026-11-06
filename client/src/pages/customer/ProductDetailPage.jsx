import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import CustomerLayout from "../../components/common/CustomerLayout";
import ProductDetails from "../../components/common/ProductDetails";
import { getProduct } from "../../services/api";
import { useCurrency } from "../../context/CurrencyContext";

const ProductDetailPage = () => {
  const { productId } = useParams();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { selectedCurrency } = useCurrency();

  useEffect(() => {
    if (selectedCurrency) {
      fetchProduct(selectedCurrency.code);
    }
  }, [productId, selectedCurrency]);

  const fetchProduct = async (currencyCode) => {
    try {
      setLoading(true);
      const response = await getProduct(productId, currencyCode);
      setProduct(response.data);
    } catch (err) {
      console.error("Failed to fetch product details:", err);
      setError("Failed to load product details.");
    } finally {
      setLoading(false);
    }
  };

  if (loading)
    return (
      <CustomerLayout>
        <div className="text-center py-8">Loading product details...</div>
      </CustomerLayout>
    );
  if (error)
    return (
      <CustomerLayout>
        <div className="text-error text-center py-8">Error: {error}</div>
      </CustomerLayout>
    );
  if (!product)
    return (
      <CustomerLayout>
        <div className="text-center py-8">Product not found.</div>
      </CustomerLayout>
    );

  return (
    <CustomerLayout>
      <div className="container mx-auto px-6 py-8">
        <ProductDetails product={product} />
      </div>
    </CustomerLayout>
  );
};

export default ProductDetailPage;
