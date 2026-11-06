import React from "react";
import Header from "./Header";
import SidebarNav from "./SidebarNav";

const AdminLayout = ({ children }) => {
  return (
    <div className="flex h-screen bg-gray-100">
      <SidebarNav />
      <div className="flex flex-col flex-1 overflow-hidden">
        <Header isAdmin={true} />
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-200">
          <div className="container mx-auto px-6 py-8">{children}</div>
        </main>
      </div>
    </div>
  );
};

export default AdminLayout;
