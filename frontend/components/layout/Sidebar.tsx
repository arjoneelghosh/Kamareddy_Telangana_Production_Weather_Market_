'use client';
// Sidebar navigation component
import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  TrendingUp,
  BarChart2,
  Leaf,
  X,
  Menu,
} from "lucide-react";

const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/prediction", label: "Price Prediction", icon: TrendingUp },
  { href: "/analysis", label: "Market Analysis", icon: BarChart2 },
];

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function Sidebar({ isOpen, onClose }: SidebarProps) {
  const pathname = usePathname();

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-20 bg-black/40 lg:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed top-0 left-0 z-30 h-full w-64 bg-white shadow-xl
          transition-transform duration-300
          lg:static lg:z-auto lg:shadow-none lg:translate-x-0
          ${isOpen ? "translate-x-0" : "-translate-x-full"}
        `}
        aria-label="Sidebar navigation"
      >
        {/* Logo / brand */}
        <div className="flex items-center justify-between px-5 py-5 border-b border-gray-100">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary-500 rounded-lg flex items-center justify-center">
              <Leaf className="w-5 h-5 text-white" />
            </div>
            <div>
              <p className="text-sm font-bold text-gray-800 leading-tight">AgriMarket</p>
              <p className="text-xs text-gray-500">AI Intelligence</p>
            </div>
          </div>
          {/* Close button – mobile only */}
          <button
            onClick={onClose}
            className="lg:hidden p-1 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
            aria-label="Close sidebar"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation links */}
        <nav className="px-3 py-4 space-y-1">
          {navItems.map(({ href, label, icon: Icon }) => {
            const isActive = pathname === href;
            return (
              <Link
                key={href}
                href={href}
                onClick={onClose}
                className={`
                  flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium
                  transition-all duration-200
                  ${
                    isActive
                      ? "bg-primary-50 text-primary-700 border-l-2 border-primary-500"
                      : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                  }
                `}
                aria-current={isActive ? "page" : undefined}
              >
                <Icon
                  className={`w-5 h-5 flex-shrink-0 ${isActive ? "text-primary-600" : "text-gray-400"}`}
                />
                {label}
              </Link>
            );
          })}
        </nav>

        {/* Footer note */}
        <div className="absolute bottom-0 left-0 right-0 px-5 py-4 border-t border-gray-100">
          <p className="text-xs text-gray-400">AI Agricultural Market v0.1</p>
        </div>
      </aside>
    </>
  );
}
