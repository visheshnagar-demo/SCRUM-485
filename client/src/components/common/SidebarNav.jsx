import React from "react";
import { Link } from "react-router-dom";
import { DollarSign, Package, Settings } from "lucide-react";

const SidebarNav = () => {
  return (
    <div className="w-64 bg-primary text-white flex flex-col p-4">
      <div className="text-2xl font-bold mb-8">Admin Panel</div>
      <nav className="flex-1">
        <ul>
          <li className="mb-4">
            <Link
              to="/admin/currencies"
              className="flex items-center space-x-2 hover:text-accent"
            >
              <DollarSign size={20} />
              <span>Currency Management</span>
            </Link>
          </li>
          <li className="mb-4">
            <Link
              to="/admin/products"
              className="flex items-center space-x-2 hover:text-accent"
            >
              <Package size={20} />
              <span>Product Management</span>
            </Link>
          </li>
          <li className="mb-4">
            <Link
              to="/admin/settings"
              className="flex items-center space-x-2 hover:text-accent"
            >
              <Settings size={20} />
              <span>Settings</span>
            </Link>
          </li>
        </ul>
      </nav>
    </div>
  );
};

export default SidebarNav;
