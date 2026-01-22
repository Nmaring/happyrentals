import React from "react";
import { Sidebar } from "./Sidebar";

export const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div className="min-h-screen bg-slate-50 text-slate-900">
    <div className="mx-auto max-w-6xl px-4 py-6">
      <div className="grid grid-cols-1 md:grid-cols-[240px_1fr] gap-6">
        <Sidebar />
        <main className="bg-white rounded-2xl shadow-sm border border-slate-200 p-5">{children}</main>
      </div>
    </div>
  </div>
);
