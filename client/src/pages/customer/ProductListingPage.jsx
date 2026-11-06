import React, { useState, useEffect } from "react";
import CustomerLayout from "../../components/common/CustomerLayout";
import ProductCard from "../../components/common/ProductCard";
import { getProducts } from "../../services/api";
import { useCurrency } from "../../context/CurrencyContext";

const ProductListingPage = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { selectedCurrency } = useCurrency();

  useEffect(() => {
    if (selectedCurrency) {
      fetchProducts(selectedCurrency.code);
    }
  }, [selectedCurrency]);

  const fetchProducts = async (currencyCode) => {
    try {
      setLoading(true);
      const response = await getProducts({ currency: currencyCode });
      setProducts(response.data);
    } catch (err) {
      console.error("Failed to fetch products:", err);
      setError("Failed to load products.");
    } finally {
      setLoading(false);
    }
  };

  if (loading)
    return (
      <CustomerLayout>
        <div className="text-center py-8">Loading products...</div>
      </CustomerLayout>
    );
  if (error)
    return (
      <CustomerLayout>
        <div className="text-error text-center py-8">Error: {error}</div>
      </CustomerLayout>
    );

  return (
    <CustomerLayout>
      <div className="container mx-auto px-6 py-8">
        <h1 className="text-4xl font-bold text-text-primary mb-4">
          Curated Tech & Audio Essentials
        </h1>
        <p className="text-lg text-text-secondary mb-8">
          Institutional guaranteed multi-currency checkout with zero hidden
          foreign exchange fees
        </p>

        {/* Currency Notice Banner */}
        <div
          className="bg-blue-100 border-l-4 border-accent text-blue-700 p-4 mb-8"
          role="alert"
        >
          <p className="font-bold">Currency Notice:</p>
          <p>
            All prices converted live. Guaranteed checkout rate in USD, EUR,
            GBP, JPY, and CAD.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
          {products.map((product) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      </div>
    </CustomerLayout>
  );
};

export default ProductListingPage;
