import React from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { clearAuthToken } from "../api";

const base = "flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors";
const active = "bg-slate-900 text-white";
const idle = "text-slate-700 hover:bg-slate-100";

export const Sidebar: React.FC = () => {
  const nav = useNavigate();
  return (
    <aside className="bg-white rounded-2xl shadow-sm border border-slate-200 p-4 h-fit">
      <div className="text-lg font-semibold">HappyRentals</div>
      <div className="text-xs text-slate-500 mt-1">Landlord dashboard</div>

      <nav className="mt-4 space-y-1">
        <NavLink to="/dashboard" className={({isActive}) => `${base} ${isActive ? active : idle}`}>Dashboard</NavLink>
        <NavLink to="/properties" className={({isActive}) => `${base} ${isActive ? active : idle}`}>Properties & Units</NavLink>
      </nav>

      <button className="mt-6 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm hover:bg-slate-50"
        onClick={() => { clearAuthToken(); nav("/login"); }}>
        Log out
      </button>
    </aside>
  );
};



