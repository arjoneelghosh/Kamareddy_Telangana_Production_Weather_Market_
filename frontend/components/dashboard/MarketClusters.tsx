// Market clusters display component
import React from "react";
import { MarketCluster } from "@/types";
import { formatCurrency } from "@/utils/formatters";
import Card from "@/components/ui/Card";
import { MapPin, Store } from "lucide-react";

interface MarketClustersProps {
  clusters: MarketCluster[];
  loading?: boolean;
}

const clusterColors = [
  "from-primary-400 to-primary-600",
  "from-secondary-400 to-secondary-600",
  "from-accent-400 to-accent-600",
  "from-purple-400 to-purple-600",
];

export default function MarketClusters({ clusters, loading = false }: MarketClustersProps) {
  return (
    <Card title="Market Clusters" subtitle="Regional market overview" loading={loading}>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {clusters.map((cluster, index) => (
          <div
            key={cluster.name}
            className={`bg-gradient-to-br ${clusterColors[index % clusterColors.length]} rounded-xl p-4 text-white`}
          >
            <h4 className="font-semibold text-sm mb-2">{cluster.name}</h4>

            <div className="flex items-center gap-1 mb-1">
              <Store className="w-3.5 h-3.5 opacity-80" />
              <span className="text-xs opacity-90">{cluster.markets} markets</span>
            </div>

            <div className="flex items-center gap-1 mb-2">
              <MapPin className="w-3.5 h-3.5 opacity-80" />
              <span className="text-xs opacity-90 truncate">{cluster.region}</span>
            </div>

            <p className="text-base font-bold">{formatCurrency(cluster.avgPrice)}</p>
            <p className="text-xs opacity-75">Average price</p>
          </div>
        ))}
      </div>
    </Card>
  );
}
