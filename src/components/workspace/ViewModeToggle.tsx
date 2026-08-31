"use client";

import React from "react";
import { LayoutGrid, Image as ImageIcon, Layers, Network, FileCode } from "lucide-react";
import { ActiveTab } from "../../lib/types";

interface ViewModeToggleProps {
  activeTab: ActiveTab;
  onChangeTab: (tab: ActiveTab) => void;
}

export const ViewModeToggle: React.FC<ViewModeToggleProps> = ({
  activeTab,
  onChangeTab,
}) => {
  const tabs: { id: ActiveTab; label: string; icon: React.FC<{ className?: string }> }[] = [
    { id: "split", label: "3-Column Workspace View", icon: LayoutGrid },
    { id: "diagram", label: "Original Diagram", icon: ImageIcon },
    { id: "overlay", label: "Detection Overlay", icon: Layers },
    { id: "graph", label: "Circuit Graph", icon: Network },
    { id: "netlist", label: "Netlist View", icon: FileCode },
  ];

  return (
    <div className="inline-flex items-center rounded-xl border border-neutral-300 bg-neutral-100 p-1 shadow-sm font-mono text-xs font-semibold">
      {tabs.map((tab) => {
        const Icon = tab.icon;
        const isActive = activeTab === tab.id;

        return (
          <button
            key={tab.id}
            type="button"
            onClick={() => onChangeTab(tab.id)}
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all ${
              isActive
                ? "bg-black text-white shadow-sm font-bold"
                : "text-neutral-600 hover:text-black hover:bg-neutral-200/60"
            }`}
          >
            <Icon className="w-3.5 h-3.5" />
            <span>{tab.label}</span>
          </button>
        );
      })}
    </div>
  );
};
