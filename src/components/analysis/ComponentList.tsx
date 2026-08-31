"use client";

import React, { useState } from "react";
import { ComponentData, SelectionState } from "../../lib/types";
import { ConfidenceBadge } from "./ConfidenceBadge";
import { Cpu, ChevronDown, ChevronUp } from "lucide-react";

interface ComponentListProps {
  components: ComponentData[];
  selection: SelectionState;
  onSelectComponent: (id: string | null) => void;
  onSelectNet: (netId: string | null) => void;
}

export const ComponentList: React.FC<ComponentListProps> = ({
  components,
  selection,
  onSelectComponent,
  onSelectNet,
}) => {
  const [visibleCount, setVisibleCount] = useState<number>(5);

  const displayedComponents = components.slice(0, visibleCount);
  const hasMore = visibleCount < components.length;

  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    const { scrollTop, scrollHeight, clientHeight } = e.currentTarget;
    if (scrollHeight - scrollTop <= clientHeight + 20 && hasMore) {
      setVisibleCount((prev) => Math.min(components.length, prev + 5));
    }
  };

  return (
    <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-xs flex flex-col h-full">
      {/* Header Bar */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 bg-slate-50/50">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-indigo-50 text-indigo-600">
            <Cpu className="w-4 h-4" />
          </div>
          <h3 className="text-sm font-bold text-slate-900">
            4. Components ({components.length})
          </h3>
        </div>
        <span className="text-[11px] font-mono text-slate-500 bg-slate-100 px-2.5 py-1 rounded-full">
          Showing {Math.min(visibleCount, components.length)} of {components.length}
        </span>
      </div>

      {/* Table Body with Scroll Event Listener for 5-at-a-time pagination */}
      <div
        onScroll={handleScroll}
        className="overflow-y-auto max-h-[380px] divide-y divide-slate-100 text-xs"
      >
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold uppercase tracking-wider sticky top-0 z-10">
            <tr>
              <th className="py-2.5 px-4">ID</th>
              <th className="py-2.5 px-4">Type</th>
              <th className="py-2.5 px-4">Confidence</th>
              <th className="py-2.5 px-4">Nets</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {displayedComponents.map((comp) => {
              const isSelected =
                selection.type === "component" && selection.componentId === comp.id;

              return (
                <tr
                  key={comp.id}
                  onClick={() => onSelectComponent(isSelected ? null : comp.id)}
                  className={`cursor-pointer transition-colors ${
                    isSelected
                      ? "bg-indigo-50/70 font-semibold"
                      : "hover:bg-slate-50"
                  }`}
                >
                  <td className="py-2.5 px-4 font-bold text-slate-900 flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-indigo-600 shrink-0" />
                    <span>{comp.id}</span>
                  </td>

                  <td className="py-2.5 px-4 text-slate-700">
                    <span className="bg-slate-100 border border-slate-200 px-2 py-0.5 rounded text-[10px] font-medium text-slate-800">
                      {comp.type}
                    </span>
                  </td>

                  <td className="py-2.5 px-4">
                    <ConfidenceBadge confidence={comp.confidence} size="sm" />
                  </td>

                  <td className="py-2.5 px-4">
                    <div className="flex flex-wrap items-center gap-1">
                      {comp.terminals.map((t) => {
                        const termRef = `${comp.id}.${t.id}`;
                        const isNetSelected =
                          selection.type === "net" && selection.netId === t.net;

                        return (
                          <button
                            type="button"
                            key={termRef}
                            onClick={(e) => {
                              e.stopPropagation();
                              if (t.net) onSelectNet(isNetSelected ? null : t.net);
                            }}
                            className={`inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded border transition-colors text-[10px] cursor-pointer ${
                              isNetSelected
                                ? "bg-indigo-600 text-white border-indigo-600 font-bold"
                                : "bg-slate-50 hover:bg-slate-200 text-slate-700 border-slate-200"
                            }`}
                          >
                            <span>{t.id}:</span>
                            <span className="font-bold">{t.net || "NC"}</span>
                          </button>
                        );
                      })}
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      {hasMore && (
        <div className="p-3 bg-slate-50 border-t border-slate-200 flex justify-between items-center text-xs">
          <span className="text-[11px] text-slate-500 font-mono">
            Scroll down or click to load 5 more
          </span>
          <button
            type="button"
            onClick={() => setVisibleCount((prev) => Math.min(components.length, prev + 5))}
            className="px-3 py-1 bg-slate-900 hover:bg-slate-800 text-white text-[11px] font-bold rounded-lg transition-colors flex items-center gap-1 cursor-pointer"
          >
            <span>Load 5 More</span>
            <ChevronDown className="w-3.5 h-3.5" />
          </button>
        </div>
      )}
    </div>
  );
};
