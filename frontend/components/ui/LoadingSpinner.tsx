// Loading spinner component
import React from "react";

interface LoadingSpinnerProps {
  size?: "sm" | "md" | "lg";
  color?: "primary" | "white" | "gray" | "current";
}

const sizeClasses: Record<string, string> = {
  sm: "w-4 h-4 border-2",
  md: "w-8 h-8 border-2",
  lg: "w-12 h-12 border-4",
};

const colorClasses: Record<string, string> = {
  primary: "border-primary-200 border-t-primary-600",
  white: "border-white/30 border-t-white",
  gray: "border-gray-200 border-t-gray-600",
  current: "border-current/30 border-t-current",
};

export default function LoadingSpinner({
  size = "md",
  color = "primary",
}: LoadingSpinnerProps) {
  return (
    <span
      role="status"
      aria-label="Loading"
      className={`
        inline-block rounded-full animate-spin
        ${sizeClasses[size]}
        ${colorClasses[color]}
      `}
    />
  );
}
