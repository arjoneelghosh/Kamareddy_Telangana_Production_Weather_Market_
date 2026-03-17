'use client';
// Dual-axis composed chart: Arrival volume vs Price
import React from "react";
import {
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { ArrivalData } from "@/types";
import { formatCurrency, formatNumber } from "@/utils/formatters";
import Card from "@/components/ui/Card";

interface ArrivalVsPriceChartProps {
  data: ArrivalData[];
  loading?: boolean;
}

const CustomTooltip = ({ active, payload, label }: {
  active?: boolean;
  payload?: Array<{ name: string; value: number; color: string }>;
  label?: string;
}) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3 text-sm">
        <p className="font-semibold text-gray-700 mb-1">{label}</p>
        {payload.map((item) => (
          <p key={item.name} style={{ color: item.color }} className="text-xs">
            {item.name === "Arrival Volume"
              ? `Arrival: ${formatNumber(item.value)} MT`
              : `Price: ${formatCurrency(item.value)}`}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

export default function ArrivalVsPriceChart({ data, loading = false }: ArrivalVsPriceChartProps) {
  return (
    <Card
      title="Arrival vs Price"
      subtitle="Inverse correlation between supply and price"
      loading={loading}
    >
      <ResponsiveContainer width="100%" height={280}>
        <ComposedChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="month" tick={{ fontSize: 11, fill: "#6b7280" }} tickLine={false} />
          <YAxis
            yAxisId="left"
            tickFormatter={(val) => `${(val / 1000).toFixed(0)}k`}
            tick={{ fontSize: 11, fill: "#6b7280" }}
            tickLine={false}
            axisLine={false}
            label={{ value: "MT", angle: -90, position: "insideLeft", fontSize: 10, fill: "#9ca3af" }}
          />
          <YAxis
            yAxisId="right"
            orientation="right"
            tickFormatter={(val) => `₹${(val / 1000).toFixed(1)}k`}
            tick={{ fontSize: 11, fill: "#6b7280" }}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Bar
            yAxisId="left"
            dataKey="arrival"
            fill="#bfdbfe"
            radius={[3, 3, 0, 0]}
            name="Arrival Volume"
          />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="price"
            stroke="#f97316"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4 }}
            name="Price"
          />
        </ComposedChart>
      </ResponsiveContainer>
    </Card>
  );
}
