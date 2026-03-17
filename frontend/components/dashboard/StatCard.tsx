// Statistics card component for the dashboard
import React from "react";
import { StatCardProps } from "@/types";
import { formatPercentage, getTrendColor, getTrendIcon } from "@/utils/formatters";
import LoadingSpinner from "@/components/ui/LoadingSpinner";

const colorVariants: Record<string, string> = {
  primary: "bg-primary-50 text-primary-600",
  secondary: "bg-secondary-50 text-secondary-600",
  accent: "bg-accent-50 text-accent-600",
  gray: "bg-gray-100 text-gray-600",
};

export default function StatCard({
  title,
  value,
  change,
  icon,
  color = "primary",
  loading = false,
}: StatCardProps) {
  return (
    <div className="bg-white rounded-xl shadow-md hover:shadow-lg transition-shadow duration-200 p-6">
      {loading ? (
        <div className="flex items-center justify-center h-20">
          <LoadingSpinner size="md" />
        </div>
      ) : (
        <div className="flex items-start justify-between">
          {/* Icon */}
          <div className={`p-3 rounded-lg ${colorVariants[color]}`} aria-hidden="true">
            {icon}
          </div>

          {/* Trend badge */}
          {change !== undefined && (
            <span
              className={`text-xs font-semibold px-2 py-1 rounded-full ${
                change > 0
                  ? "bg-green-50 text-green-700"
                  : change < 0
                  ? "bg-red-50 text-red-700"
                  : "bg-gray-50 text-gray-600"
              }`}
            >
              {getTrendIcon(change)} {formatPercentage(change)}
            </span>
          )}
        </div>
      )}

      {!loading && (
        <div className="mt-4">
          <p className="text-2xl font-bold text-gray-800">{value}</p>
          <p className="text-sm text-gray-500 mt-0.5">{title}</p>
        </div>
      )}
    </div>
  );
}
