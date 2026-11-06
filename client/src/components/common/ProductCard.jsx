import React from "react";
import { Link } from "react-router-dom";
import { Star } from "lucide-react";
import LocalizedPriceDisplay from "./LocalizedPriceDisplay";

const ProductCard = ({ product }) => {
  const { id, name, image_url, rating, reviews_count, localized_price } =
    product;

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300">
      <Link to={`/products/${id}`}>
        <img
          src={image_url || "https://via.placeholder.com/300"}
          alt={name}
          className="w-full h-48 object-cover"
        />
      </Link>
      <div className="p-4">
        <h3 className="text-lg font-semibold text-text-primary mb-1">
          <Link to={`/products/${id}`} className="hover:text-accent">
            {name}
          </Link>
        </h3>
        <div className="flex items-center mb-2">
          <div className="flex text-yellow-400">
            {[...Array(5)].map((_, i) => (
              <Star
                key={i}
                size={16}
                fill={i < Math.floor(rating)}
                stroke={i < Math.floor(rating) ? "currentColor" : "none"}
              />
            ))}
          </div>
          <span className="text-sm text-text-secondary ml-2">
            ({reviews_count} reviews)
          </span>
        </div>
        <div className="text-xl font-bold text-text-primary mb-3">
          {localized_price ? (
            <LocalizedPriceDisplay
              price={localized_price.price}
              currencyCode={localized_price.currency_code}
            />
          ) : (
            <span>Price not available</span>
          )}
        </div>
        <button className="w-full bg-accent text-white py-2 px-4 rounded-md hover:bg-blue-600 transition-colors duration-300">
          Add to Cart
        </button>
      </div>
    </div>
  );
};

export default ProductCard;
