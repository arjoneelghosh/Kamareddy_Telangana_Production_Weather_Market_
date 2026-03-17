// Card container component
import React from "react";
import { CardProps } from "@/types";
import LoadingSpinner from "./LoadingSpinner";

export default function Card({ title, subtitle, children, className = "", loading = false }: CardProps) {
  return (
    <div
      className={`bg-white rounded-xl shadow-md hover:shadow-lg transition-shadow duration-200 ${className}`}
    >
      {(title || subtitle) && (
        <div className="px-6 pt-6 pb-4 border-b border-gray-100">
          {title && <h3 className="text-lg font-semibold text-gray-800">{title}</h3>}
          {subtitle && <p className="text-sm text-gray-500 mt-0.5">{subtitle}</p>}
        </div>
      )}
      <div className="p-6">
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <LoadingSpinner size="md" />
          </div>
        ) : (
          children
        )}
      </div>
    </div>
  );
}
