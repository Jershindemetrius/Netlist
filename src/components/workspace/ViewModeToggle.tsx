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
    { id: "split", label: "3-Column Workspace", icon: LayoutGrid },
    { id: "diagram", label: "Original Schematic", icon: ImageIcon },
    { id: "overlay", label: "Detection Overlay", icon: Layers },
    { id: "graph", label: "Circuit Graph", icon: Network },
    { id: "netlist", label: "SPICE Netlist", icon: FileCode },
  ];

  return (
    <div className="inline-flex items-center rounded-2xl border border-slate-200 bg-slate-100 p-1 shadow-2xs text-xs font-semibold">
      {tabs.map((tab) => {
        const Icon = tab.icon;
        const isActive = activeTab === tab.id;

        return (
          <button
            key={tab.id}
            type="button"
            onClick={() => onChangeTab(tab.id)}
            className={`inline-flex items-center gap-2 px-3.5 py-1.5 rounded-xl transition-all cursor-pointer ${
              isActive
                ? "bg-white text-slate-900 shadow-xs font-bold"
                : "text-slate-600 hover:text-slate-900 hover:bg-slate-200/50"
            }`}
          >
            <Icon className="w-4 h-4 text-indigo-600" />
            <span>{tab.label}</span>
          </button>
        );
      })}
    </div>
  );
};
