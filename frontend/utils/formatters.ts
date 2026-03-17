// Utility formatting functions for AI Agricultural Market Intelligence System

import { format } from "date-fns";

/**
 * Format a number as Indian Rupee currency
 */
export function formatCurrency(value: number, locale: string = "en-IN"): string {
  return new Intl.NumberFormat(locale, {
    style: "currency",
    currency: "INR",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
}

/**
 * Format a number with thousand separators
 */
export function formatNumber(value: number, locale: string = "en-IN"): string {
  return new Intl.NumberFormat(locale).format(value);
}

/**
 * Format a number as a percentage with +/- sign
 */
export function formatPercentage(value: number, decimals: number = 1): string {
  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toFixed(decimals)}%`;
}

/**
 * Format a date using date-fns
 * @param date - Date string, number, or Date object
 * @param formatStr - 'short' | 'long' | custom format string
 */
export function formatDate(
  date: string | number | Date,
  formatStr: "short" | "long" | string = "short"
): string {
  const dateObj = typeof date === "string" || typeof date === "number" ? new Date(date) : date;

  if (formatStr === "short") {
    return format(dateObj, "dd MMM");
  } else if (formatStr === "long") {
    return format(dateObj, "dd MMMM yyyy");
  }
  return format(dateObj, formatStr);
}

/**
 * Get a Tailwind CSS color class based on trend direction
 */
export function getTrendColor(trend: number): string {
  if (trend > 0) return "text-green-600";
  if (trend < 0) return "text-red-600";
  return "text-gray-500";
}

/**
 * Get an arrow symbol based on trend direction
 */
export function getTrendIcon(trend: number): string {
  if (trend > 0) return "↑";
  if (trend < 0) return "↓";
  return "→";
}

/**
 * Get background color class for trend
 */
export function getTrendBgColor(trend: number): string {
  if (trend > 0) return "bg-green-50 text-green-700";
  if (trend < 0) return "bg-red-50 text-red-700";
  return "bg-gray-50 text-gray-600";
}
