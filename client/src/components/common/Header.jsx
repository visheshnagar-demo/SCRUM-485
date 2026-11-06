import React from "react";
import { Link } from "react-router-dom";
import { Search, ShoppingCart, User } from "lucide-react";
import CurrencySelectorDropdown from "./CurrencySelectorDropdown";

const Header = ({ isAdmin }) => {
  return (
    <header className="bg-white shadow-md p-4 flex items-center justify-between">
      <div className="flex items-center">
        <Link to="/" className="text-2xl font-bold text-primary mr-8">
          AURA STORE
        </Link>
        {!isAdmin && (
          <nav className="hidden md:flex space-x-6">
            <Link to="/" className="text-text-primary hover:text-accent">
              Home
            </Link>
            <Link to="/products" className="text-accent font-semibold">
              Products
            </Link>
            <Link
              to="/categories"
              className="text-text-primary hover:text-accent"
            >
              Categories
            </Link>
          </nav>
        )}
      </div>

      <div className="flex items-center space-x-4">
        {!isAdmin && (
          <div className="relative hidden md:block">
            <input
              type="text"
              placeholder="Search products, electronics, gear..."
              className="pl-10 pr-4 py-2 rounded-full bg-gray-100 border border-gray-300 focus:outline-none focus:ring-2 focus:ring-accent"
            />
            <Search
              className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"
              size={20}
            />
          </div>
        )}

        <CurrencySelectorDropdown />

        {!isAdmin && (
          <div className="flex items-center space-x-4">
            <div className="relative">
              <ShoppingCart className="text-text-primary" size={24} />
              <span className="absolute -top-2 -right-2 bg-accent text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                2
              </span>
            </div>
            <Link
              to="/profile"
              className="flex items-center space-x-2 text-text-primary hover:text-accent"
            >
              <User size={24} />
              <span className="hidden md:block">Sign In</span>
            </Link>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
