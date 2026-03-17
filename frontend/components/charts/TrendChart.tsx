'use client';
// Multi-line trend chart using Recharts
import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { MultiCommodityTrendData } from "@/types";
import { formatCurrency, formatDate } from "@/utils/formatters";
import Card from "@/components/ui/Card";

interface TrendChartProps {
  data: MultiCommodityTrendData[];
  commodities: string[];
  loading?: boolean;
}

const COLORS = ["#22c55e", "#3b82f6", "#f97316", "#a855f7", "#ec4899"];

const CustomTooltip = ({ active, payload, label }: {
  active?: boolean;
  payload?: Array<{ name: string; value: number; color: string }>;
  label?: string;
}) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3 text-sm">
        <p className="font-semibold text-gray-700 mb-1">
          {label ? formatDate(label, "long") : ""}
        </p>
        {payload.map((item) => (
          <p key={item.name} style={{ color: item.color }} className="text-xs">
            {item.name}: {formatCurrency(item.value)}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

export default function TrendChart({ data, commodities, loading = false }: TrendChartProps) {
  return (
    <Card title="Price Trends" subtitle="Last 30 days" loading={loading}>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
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
          <Legend wrapperStyle={{ fontSize: 12 }} />
          {commodities.map((commodity, index) => (
            <Line
              key={commodity}
              type="monotone"
              dataKey={commodity}
              stroke={COLORS[index % COLORS.length]}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4 }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
}
