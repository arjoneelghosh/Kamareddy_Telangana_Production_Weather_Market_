// Reusable Button component
import React from "react";
import { ButtonProps } from "@/types";
import LoadingSpinner from "./LoadingSpinner";

const variantClasses: Record<string, string> = {
  primary:
    "bg-primary-500 hover:bg-primary-600 text-white border border-primary-500 hover:border-primary-600",
  secondary:
    "bg-secondary-500 hover:bg-secondary-600 text-white border border-secondary-500 hover:border-secondary-600",
  outline:
    "bg-transparent hover:bg-gray-50 text-gray-700 border border-gray-300 hover:border-gray-400",
  ghost: "bg-transparent hover:bg-gray-100 text-gray-700 border border-transparent",
  danger: "bg-red-500 hover:bg-red-600 text-white border border-red-500 hover:border-red-600",
};

const sizeClasses: Record<string, string> = {
  sm: "px-3 py-1.5 text-sm",
  md: "px-4 py-2 text-sm",
  lg: "px-6 py-3 text-base",
};

export default function Button({
  variant = "primary",
  size = "md",
  loading = false,
  icon,
  children,
  disabled,
  className = "",
  ...props
}: ButtonProps) {
  const isDisabled = disabled || loading;

  return (
    <button
      disabled={isDisabled}
      className={`
        inline-flex items-center justify-center gap-2 font-medium rounded-lg
        transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500
        disabled:opacity-60 disabled:cursor-not-allowed
        ${variantClasses[variant]}
        ${sizeClasses[size]}
        ${className}
      `}
      {...props}
    >
      {loading ? (
        <LoadingSpinner size="sm" color="current" />
      ) : (
        icon && <span className="flex-shrink-0">{icon}</span>
      )}
      {children}
    </button>
  );
}
