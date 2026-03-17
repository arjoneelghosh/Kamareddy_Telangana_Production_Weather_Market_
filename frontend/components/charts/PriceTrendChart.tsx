'use client';
// Area chart for price trends
import React from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { PriceTrendData } from "@/types";
import { formatCurrency, formatDate } from "@/utils/formatters";
import Card from "@/components/ui/Card";

interface PriceTrendChartProps {
  data: PriceTrendData[];
  commodity?: string;
  loading?: boolean;
}

const CustomTooltip = ({ active, payload, label }: {
  active?: boolean;
  payload?: Array<{ value: number }>;
  label?: string;
}) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3 text-sm">
        <p className="text-gray-500 text-xs">{label ? formatDate(label, "long") : ""}</p>
        <p className="font-bold text-primary-700 mt-0.5">{formatCurrency(payload[0].value)}</p>
      </div>
    );
  }
  return null;
};

export default function PriceTrendChart({
  data,
  commodity = "Price",
  loading = false,
}: PriceTrendChartProps) {
  return (
    <Card
      title={`${commodity} Price Trend`}
      subtitle="Historical price movement"
      loading={loading}
    >
      <ResponsiveContainer width="100%" height={280}>
        <AreaChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
          <defs>
            <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#22c55e" stopOpacity={0.2} />
              <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis
            dataKey="date"
            tickFormatter={(val) => formatDate(val, "short")}
            tick={{ fontSize: 11, fill: "#6b7280" }}
            tickLine={false}
          />
          <YAxis
            tickFormatter={(val) => `₹${(val / 1000).toFixed(1)}k`}
            tick={{ fontSize: 11, fill: "#6b7280" }}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip content={<CustomTooltip />} />
          <Area
            type="monotone"
            dataKey="price"
            stroke="#22c55e"
            strokeWidth={2}
            fill="url(#priceGradient)"
            dot={false}
            activeDot={{ r: 4, fill: "#22c55e" }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </Card>
  );
}
