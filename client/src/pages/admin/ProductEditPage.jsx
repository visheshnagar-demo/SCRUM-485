import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import AdminLayout from "../../components/common/AdminLayout";
import ProductPricingSection from "../../components/admin/ProductPricingSection";
import { getProduct, updateProduct } from "../../services/api";

const ProductEditPage = () => {
  const { productId } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    category: "",
    image_url: "",
    is_active: true,
  });

  useEffect(() => {
    fetchProductDetails();
  }, [productId]);

  const fetchProductDetails = async () => {
    try {
      setLoading(true);
      const response = await getProduct(productId);
      setProduct(response.data);
      setFormData({
        name: response.data.name || "",
        description: response.data.description || "",
        category: response.data.category || "",
        image_url: response.data.image_url || "",
        is_active: response.data.is_active,
      });
    } catch (err) {
      console.error("Failed to fetch product details:", err);
      setError("Failed to load product details.");
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await updateProduct(productId, formData);
      alert("Product updated successfully!");
      navigate("/admin/products"); // Redirect to product listing or similar
    } catch (err) {
      console.error("Failed to update product:", err);
      setError("Failed to update product.");
    }
  };

  if (loading)
    return (
      <AdminLayout>
        <div className="text-center py-4">Loading product...</div>
      </AdminLayout>
    );
  if (error)
    return (
      <AdminLayout>
        <div className="text-error text-center py-4">Error: {error}</div>
      </AdminLayout>
    );
  if (!product)
    return (
      <AdminLayout>
        <div className="text-center py-4">Product not found.</div>
      </AdminLayout>
    );

  return (
    <AdminLayout>
      <h1 className="text-3xl font-bold text-text-primary mb-6">
        Edit Product: {product.name}
      </h1>

      <div className="bg-white p-6 rounded-lg shadow-md mb-6">
        <h2 className="text-2xl font-semibold text-text-primary mb-4">
          Product Details
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label
              htmlFor="name"
              className="block text-sm font-medium text-gray-700"
            >
              Product Name
            </label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-accent focus:ring-accent sm:text-sm"
              required
            />
          </div>
          <div>
            <label
              htmlFor="description"
              className="block text-sm font-medium text-gray-700"
            >
              Description
            </label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows="4"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-accent focus:ring-accent sm:text-sm"
            ></textarea>
          </div>
          <div>
            <label
              htmlFor="category"
              className="block text-sm font-medium text-gray-700"
            >
              Category
            </label>
            <input
              type="text"
              id="category"
              name="category"
              value={formData.category}
              onChange={handleChange}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-accent focus:ring-accent sm:text-sm"
            />
          </div>
          <div>
            <label
              htmlFor="image_url"
              className="block text-sm font-medium text-gray-700"
            >
              Image URL
            </label>
            <input
              type="text"
              id="image_url"
              name="image_url"
              value={formData.image_url}
              onChange={handleChange}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-accent focus:ring-accent sm:text-sm"
            />
          </div>
          <div className="flex items-center">
            <input
              type="checkbox"
              id="is_active"
              name="is_active"
              checked={formData.is_active}
              onChange={handleChange}
              className="h-4 w-4 text-accent focus:ring-accent border-gray-300 rounded"
            />
            <label
              htmlFor="is_active"
              className="ml-2 block text-sm text-gray-900"
            >
              Is Active
            </label>
          </div>
          <div className="flex justify-end">
            <button
              type="submit"
              className="bg-accent text-white px-6 py-2 rounded-md hover:bg-blue-600 transition-colors"
            >
              Save Product Details
            </button>
          </div>
        </form>
      </div>

      <ProductPricingSection productId={productId} />
    </AdminLayout>
  );
};

export default ProductEditPage;
