import React from "react";
import { Star, ShoppingCart } from "lucide-react";
import LocalizedPriceDisplay from "./LocalizedPriceDisplay";

const ProductDetails = ({ product }) => {
  if (!product) {
    return <div className="text-center py-8">Product not found.</div>;
  }

  const {
    name,
    description,
    image_url,
    rating,
    reviews_count,
    localized_price,
  } = product;

  return (
    <div className="bg-white p-8 rounded-lg shadow-md">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Product Image Gallery */}
        <div>
          <img
            src={image_url || "https://via.placeholder.com/600"}
            alt={name}
            className="w-full h-96 object-cover rounded-lg mb-4"
          />
          {/* Thumbnail carousel can go here */}
        </div>

        {/* Product Info and Purchase */}
        <div>
          <h1 className="text-4xl font-bold text-text-primary mb-2">{name}</h1>
          <div className="flex items-center mb-4">
            <div className="flex text-yellow-400">
              {[...Array(5)].map((_, i) => (
                <Star
                  key={i}
                  size={20}
                  fill={i < Math.floor(rating)}
                  stroke={i < Math.floor(rating) ? "currentColor" : "none"}
                />
              ))}
            </div>
            <span className="text-md text-text-secondary ml-2">
              ({reviews_count} reviews)
            </span>
          </div>

          <p className="text-text-secondary mb-6">{description}</p>

          <div className="text-3xl font-bold text-text-primary mb-6">
            {localized_price ? (
              <LocalizedPriceDisplay
                price={localized_price.price}
                currencyCode={localized_price.currency_code}
              />
            ) : (
              <span>Price not available</span>
            )}
            {localized_price && localized_price.is_converted && (
              <span className="text-lg text-text-secondary ml-2">
                {" "}
                (Converted from {localized_price.original_currency_code}{" "}
                {localized_price.original_price})
              </span>
            )}
          </div>

          <div className="flex items-center space-x-4 mb-6">
            <input
              type="number"
              defaultValue="1"
              min="1"
              className="w-20 p-2 border border-gray-300 rounded-md text-center"
            />
            <button className="flex items-center space-x-2 bg-accent text-white py-3 px-6 rounded-md hover:bg-blue-600 transition-colors duration-300">
              <ShoppingCart size={20} />
              <span>Add to Cart</span>
            </button>
          </div>

          {/* Additional details like features, specs, etc. */}
          <div className="mt-8">
            <h2 className="text-2xl font-semibold text-text-primary mb-4">
              Technical Specifications
            </h2>
            <ul className="list-disc list-inside text-text-secondary space-y-2">
              <li>40mm Bio-Cellulose Drivers</li>
              <li>40h Battery + Fast Charge</li>
              <li>Hybrid Active Noise Cancelling</li>
              <li>Spatial Audio + Bluetooth 5.4</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductDetails;
