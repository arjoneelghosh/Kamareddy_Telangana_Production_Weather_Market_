'use client';
// Bar chart for seasonal price patterns
import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { SeasonalData } from "@/types";
import { formatCurrency, formatNumber } from "@/utils/formatters";
import Card from "@/components/ui/Card";

interface SeasonalPatternChartProps {
  data: SeasonalData[];
  loading?: boolean;
}

// Colors representing seasons: winter (blue), spring (green), summer (orange), autumn (yellow)
const seasonColors = [
  "#93c5fd", "#93c5fd", // Jan, Feb – winter
  "#86efac", "#86efac", "#86efac", // Mar, Apr, May – spring
  "#fda4af", "#fda4af", "#fda4af", // Jun, Jul, Aug – summer
  "#fcd34d", "#fcd34d", "#fcd34d", // Sep, Oct, Nov – autumn
  "#93c5fd", // Dec – winter
];

const CustomTooltip = ({ active, payload, label }: {
  active?: boolean;
  payload?: Array<{ name: string; value: number }>;
  label?: string;
}) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3 text-sm">
        <p className="font-semibold text-gray-700 mb-1">{label}</p>
        {payload.map((item) => (
          <p key={item.name} className="text-xs text-gray-600">
            {item.name === "Average Price"
              ? `Avg Price: ${formatCurrency(item.value)}`
              : `Volume: ${formatNumber(item.value)} MT`}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

export default function SeasonalPatternChart({ data, loading = false }: SeasonalPatternChartProps) {
  return (
    <Card
      title="Seasonal Price Patterns"
      subtitle="Monthly average price and volume"
      loading={loading}
    >
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="month" tick={{ fontSize: 11, fill: "#6b7280" }} tickLine={false} />
          <YAxis
            tickFormatter={(val) => `₹${(val / 1000).toFixed(1)}k`}
            tick={{ fontSize: 11, fill: "#6b7280" }}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Bar dataKey="avgPrice" name="Average Price" radius={[3, 3, 0, 0]}>
            {data.map((_, index) => (
              <Cell key={`cell-${index}`} fill={seasonColors[index % seasonColors.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </Card>
  );
}
