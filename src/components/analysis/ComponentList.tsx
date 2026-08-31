"use client";

import React from "react";
import { ComponentData, SelectionState } from "../../lib/types";
import { ConfidenceBadge } from "./ConfidenceBadge";
import { Cpu, Zap, AlertTriangle } from "lucide-react";

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
  return (
    <div className="bg-white border border-neutral-200 rounded-xl overflow-hidden shadow-sm">
      <div className="flex items-center justify-between px-6 py-4 border-b border-neutral-200 bg-neutral-50/50">
        <div className="flex items-center gap-2">
          <Cpu className="w-5 h-5 text-black" />
          <h3 className="font-mono text-sm font-bold text-neutral-900 uppercase tracking-wider">
            Detected Components ({components.length})
          </h3>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left font-mono text-xs">
          <thead className="bg-neutral-100/70 border-b border-neutral-200 text-neutral-600 font-bold uppercase tracking-wider">
            <tr>
              <th className="py-3 px-4">ID</th>
              <th className="py-3 px-4">Type / Class</th>
              <th className="py-3 px-4">Value</th>
              <th className="py-3 px-4">Confidence</th>
              <th className="py-3 px-4">Terminals & Electrical Nets</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-200">
            {components.map((comp) => {
              const isSelected =
                selection.type === "component" && selection.componentId === comp.id;
              const isLowConf = comp.confidence < 0.70;

              return (
                <tr
                  key={comp.id}
                  onClick={() => onSelectComponent(isSelected ? null : comp.id)}
                  className={`cursor-pointer transition-colors ${
                    isSelected
                      ? "bg-neutral-100 font-semibold"
                      : "hover:bg-neutral-50/80"
                  }`}
                >
                  <td className="py-3 px-4 font-bold text-neutral-900 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-black" />
                    <span>{comp.id}</span>
                  </td>

                  <td className="py-3 px-4 text-neutral-700 font-mono">
                    <span className="bg-neutral-100 border border-neutral-300 px-2 py-0.5 rounded text-[11px]">
                      {comp.type}
                    </span>
                  </td>

                  <td className="py-3 px-4 text-neutral-600 font-mono">
                    {comp.value || "—"}
                  </td>

                  <td className="py-3 px-4">
                    <ConfidenceBadge confidence={comp.confidence} size="sm" />
                  </td>

                  <td className="py-3 px-4">
                    <div className="flex flex-wrap items-center gap-1.5">
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
                            className={`inline-flex items-center gap-1 px-2 py-0.5 rounded border transition-colors text-[11px] ${
                              isNetSelected
                                ? "bg-black text-white border-black font-bold"
                                : "bg-neutral-50 hover:bg-neutral-200 text-neutral-800 border-neutral-300"
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
    </div>
  );
};
