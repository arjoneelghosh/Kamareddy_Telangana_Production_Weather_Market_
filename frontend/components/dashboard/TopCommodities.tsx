// Top commodities list for the dashboard
import React from "react";
import { TopCommodity } from "@/types";
import { formatCurrency, formatNumber, formatPercentage, getTrendColor, getTrendIcon } from "@/utils/formatters";
import Card from "@/components/ui/Card";

interface TopCommoditiesProps {
  commodities: TopCommodity[];
  loading?: boolean;
}

export default function TopCommodities({ commodities, loading = false }: TopCommoditiesProps) {
  return (
    <Card title="Top Commodities" subtitle="By trading volume" loading={loading}>
      <div className="space-y-3">
        {commodities.map((commodity, index) => (
          <div
            key={commodity.name}
            className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50 transition-colors duration-150"
          >
            {/* Rank badge */}
            <div className="flex-shrink-0 w-7 h-7 rounded-full bg-primary-50 text-primary-600 text-xs font-bold flex items-center justify-center">
              {index + 1}
            </div>

            {/* Commodity info */}
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-gray-800 truncate">{commodity.name}</p>
              <p className="text-xs text-gray-500">Vol: {formatNumber(commodity.volume)} MT</p>
            </div>

            {/* Price and change */}
            <div className="text-right flex-shrink-0">
              <p className="text-sm font-bold text-gray-800">{formatCurrency(commodity.price)}</p>
              <p className={`text-xs font-medium ${getTrendColor(commodity.change)}`}>
                {getTrendIcon(commodity.change)} {formatPercentage(commodity.change)}
              </p>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
