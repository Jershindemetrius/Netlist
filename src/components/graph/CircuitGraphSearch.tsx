"use client";

import React, { useState } from "react";
import { CircuitGraphResponse } from "../../lib/types";
import { Search, Route, Sparkles, Zap, ArrowRight } from "lucide-react";

interface CircuitGraphSearchProps {
  data: CircuitGraphResponse;
  onSelectComponent: (id: string | null) => void;
  onSelectNet: (netId: string | null) => void;
}

export const CircuitGraphSearch: React.FC<CircuitGraphSearchProps> = ({
  data,
  onSelectComponent,
  onSelectNet,
}) => {
  const [startNode, setStartNode] = useState<string>(data.components[0]?.id || "");
  const [targetNode, setTargetNode] = useState<string>(data.components[1]?.id || "");
  const [pathResult, setPathResult] = useState<string[] | null>(null);
  const [searching, setSearching] = useState(false);

  // Real-Time AI Breadth-First Search (BFS) Graph Search Algorithm
  const runBfsGraphSearch = () => {
    if (!startNode || !targetNode || startNode === targetNode) return;

    setSearching(true);

    // Build adjacency list: component_id -> connected component_ids
    const adj: Record<string, string[]> = {};
    data.components.forEach((c) => {
      adj[c.id] = [];
    });

    // Map terminal refs to net IDs
    const termToNet: Record<string, string> = {};
    Object.entries(data.nets || {}).forEach(([netId, refs]) => {
      refs.forEach((ref) => {
        termToNet[ref] = netId;
      });
    });

    // Connect components sharing the same net
    Object.values(data.nets || {}).forEach((refs) => {
      const compIds = Array.from(new Set(refs.map((r) => r.split(".")[0])));
      for (let i = 0; i < compIds.length; i++) {
        for (let j = i + 1; j < compIds.length; j++) {
          const u = compIds[i];
          const v = compIds[j];
          if (adj[u] && !adj[u].includes(v)) adj[u].push(v);
          if (adj[v] && !adj[v].includes(u)) adj[v].push(u);
        }
      }
    });

    // BFS Queue
    const queue: string[][] = [[startNode]];
    const visited = new Set<string>([startNode]);
    let foundPath: string[] | null = null;

    while (queue.length > 0) {
      const currentPath = queue.shift()!;
      const node = currentPath[currentPath.length - 1];

      if (node === targetNode) {
        foundPath = currentPath;
        break;
      }

      for (const neighbor of adj[node] || []) {
        if (!visited.has(neighbor)) {
          visited.add(neighbor);
          queue.push([...currentPath, neighbor]);
        }
      }
    }

    setTimeout(() => {
      setPathResult(foundPath);
      setSearching(false);
      if (foundPath && foundPath.length > 0) {
        onSelectComponent(foundPath[0]);
      }
    }, 400);
  };

  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs font-sans text-xs space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-200">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-indigo-50 text-indigo-600">
            <Route className="w-4 h-4" />
          </div>
          <h4 className="font-bold text-slate-900 text-xs">
            Real-Time AI Graph Traversal & Path Search (BFS)
          </h4>
        </div>
        <span className="bg-indigo-50 text-indigo-700 font-bold px-2 py-0.5 rounded text-[10px]">
          REAL-TIME ENGINE
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 items-end">
        <div>
          <label className="block text-[11px] font-semibold text-slate-500 mb-1">Start Component</label>
          <select
            value={startNode}
            onChange={(e) => setStartNode(e.target.value)}
            className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs font-semibold text-slate-900"
          >
            {data.components.map((c) => (
              <option key={c.id} value={c.id}>
                {c.id} ({c.type})
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-[11px] font-semibold text-slate-500 mb-1">Target Component</label>
          <select
            value={targetNode}
            onChange={(e) => setTargetNode(e.target.value)}
            className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs font-semibold text-slate-900"
          >
            {data.components.map((c) => (
              <option key={c.id} value={c.id}>
                {c.id} ({c.type})
              </option>
            ))}
          </select>
        </div>

        <button
          type="button"
          onClick={runBfsGraphSearch}
          disabled={searching}
          className="bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-2 px-4 rounded-xl transition-all shadow-xs flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
        >
          <Search className="w-4 h-4" />
          <span>{searching ? "Tracing..." : "Find Path"}</span>
        </button>
      </div>

      {/* Path Results */}
      {pathResult && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-xs space-y-2">
          <div className="flex items-center justify-between font-bold text-emerald-900">
            <span className="flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-emerald-600" />
              <span>Trace Found ({pathResult.length} Nodes)</span>
            </span>
          </div>
          <div className="flex flex-wrap items-center gap-1.5 font-mono font-bold text-indigo-700">
            {pathResult.map((nodeId, idx) => (
              <React.Fragment key={nodeId}>
                <button
                  type="button"
                  onClick={() => onSelectComponent(nodeId)}
                  className="px-2.5 py-1 bg-white border border-emerald-300 rounded-lg shadow-2xs hover:bg-indigo-50 hover:text-indigo-900 cursor-pointer"
                >
                  {nodeId}
                </button>
                {idx < pathResult.length - 1 && <ArrowRight className="w-3.5 h-3.5 text-emerald-500" />}
              </React.Fragment>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
