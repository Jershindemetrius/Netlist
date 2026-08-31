"use client";

import React, { useState, useRef } from "react";
import { CircuitGraphResponse, SelectionState } from "../../lib/types";
import { Eye, EyeOff, ZoomIn, ZoomOut, RotateCcw, AlertTriangle } from "lucide-react";

interface DetectionOverlayProps {
  imageUrl: string;
  data: CircuitGraphResponse;
  selection: SelectionState;
  onSelectComponent: (id: string | null) => void;
  onSelectTerminal: (termRef: string | null) => void;
  onSelectNet: (netId: string | null) => void;
}

export const DetectionOverlay: React.FC<DetectionOverlayProps> = ({
  imageUrl,
  data,
  selection,
  onSelectComponent,
  onSelectTerminal,
  onSelectNet,
}) => {
  const [showBboxes, setShowBboxes] = useState(true);
  const [showTerminals, setShowTerminals] = useState(true);
  const [showWires, setShowWires] = useState(true);
  const [showJunctions, setShowJunctions] = useState(true);
  const [zoom, setZoom] = useState(1.0);

  const containerRef = useRef<HTMLDivElement>(null);

  // Map terminal refs to net IDs
  const termToNet: Record<string, string> = {};
  Object.entries(data.nets || {}).forEach(([netId, termRefs]) => {
    termRefs.forEach((ref) => {
      termToNet[ref] = netId;
    });
  });

  return (
    <div className="w-full bg-white border border-neutral-200 rounded-xl overflow-hidden shadow-sm flex flex-col h-full">
      {/* Controls Bar */}
      <div className="flex flex-wrap items-center justify-between gap-2 px-4 py-2.5 bg-neutral-50 border-b border-neutral-200">
        <div className="flex items-center gap-2">
          <span className="font-mono text-xs font-bold text-neutral-900 uppercase tracking-wide">
            Overlay Layers:
          </span>

          <button
            type="button"
            onClick={() => setShowBboxes(!showBboxes)}
            className={`px-2.5 py-1 rounded text-xs font-mono font-medium border transition-colors ${
              showBboxes
                ? "bg-black text-white border-black"
                : "bg-white text-neutral-600 border-neutral-300 hover:bg-neutral-100"
            }`}
          >
            Components ({data.components?.length || 0})
          </button>

          <button
            type="button"
            onClick={() => setShowTerminals(!showTerminals)}
            className={`px-2.5 py-1 rounded text-xs font-mono font-medium border transition-colors ${
              showTerminals
                ? "bg-black text-white border-black"
                : "bg-white text-neutral-600 border-neutral-300 hover:bg-neutral-100"
            }`}
          >
            Terminals
          </button>

          <button
            type="button"
            onClick={() => setShowWires(!showWires)}
            className={`px-2.5 py-1 rounded text-xs font-mono font-medium border transition-colors ${
              showWires
                ? "bg-black text-white border-black"
                : "bg-white text-neutral-600 border-neutral-300 hover:bg-neutral-100"
            }`}
          >
            Wires ({data.wires?.length || 0})
          </button>

          <button
            type="button"
            onClick={() => setShowJunctions(!showJunctions)}
            className={`px-2.5 py-1 rounded text-xs font-mono font-medium border transition-colors ${
              showJunctions
                ? "bg-black text-white border-black"
                : "bg-white text-neutral-600 border-neutral-300 hover:bg-neutral-100"
            }`}
          >
            Junctions
          </button>
        </div>

        <div className="flex items-center gap-1.5">
          <button
            type="button"
            onClick={() => setZoom((z) => Math.max(0.6, z - 0.2))}
            className="p-1.5 rounded border border-neutral-300 bg-white text-neutral-700 hover:bg-neutral-100"
            title="Zoom Out"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>
          <span className="font-mono text-xs font-semibold px-2">{Math.round(zoom * 100)}%</span>
          <button
            type="button"
            onClick={() => setZoom((z) => Math.min(2.5, z + 0.2))}
            className="p-1.5 rounded border border-neutral-300 bg-white text-neutral-700 hover:bg-neutral-100"
            title="Zoom In"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>
          <button
            type="button"
            onClick={() => setZoom(1.0)}
            className="p-1.5 rounded border border-neutral-300 bg-white text-neutral-700 hover:bg-neutral-100 ml-1"
            title="Reset Zoom"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Overlay Canvas Viewport */}
      <div
        ref={containerRef}
        className="relative flex-1 bg-neutral-900/5 overflow-auto flex items-center justify-center p-4 min-h-[420px]"
      >
        <div
          className="relative inline-block transition-transform duration-150 origin-center"
          style={{ transform: `scale(${zoom})` }}
        >
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={imageUrl}
            alt="Circuit Analysis View"
            className="max-w-none block rounded border border-neutral-300 shadow bg-white"
          />

          {/* SVG Overlay Layer */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none">
            {/* Wires Overlay */}
            {showWires &&
              data.wires?.map((wire) => {
                const pointsStr = wire.points.map((p) => `${p[0]},${p[1]}`).join(" ");
                const isUncertain = wire.confidence < 0.70;
                return (
                  <polyline
                    key={wire.id}
                    points={pointsStr}
                    fill="none"
                    stroke={isUncertain ? "#f59e0b" : "#2563eb"}
                    strokeWidth={isUncertain ? "3" : "2"}
                    strokeDasharray={isUncertain ? "4 4" : "none"}
                    opacity="0.85"
                  />
                );
              })}

            {/* Junctions Overlay */}
            {showJunctions &&
              data.junctions?.map((junc) => (
                <circle
                  key={junc.id}
                  cx={junc.position[0]}
                  cy={junc.position[1]}
                  r="4"
                  fill="#10b981"
                  stroke="#ffffff"
                  strokeWidth="1.5"
                />
              ))}
          </svg>

          {/* Interactive Bounding Boxes & Terminals Overlay */}
          {data.components.map((comp) => {
            const isSelectedComp =
              selection.type === "component" && selection.componentId === comp.id;
            const isRelatedToSelectedNet =
              selection.type === "net" &&
              comp.terminals.some((t) => termToNet[`${comp.id}.${t.id}`] === selection.netId);

            const [xmin, ymin, xmax, ymax] = comp.bbox;
            const width = xmax - xmin;
            const height = ymax - ymin;

            const isLowConf = comp.confidence < 0.70;

            return (
              <React.Fragment key={comp.id}>
                {/* Bounding Box */}
                {showBboxes && (
                  <div
                    onClick={(e) => {
                      e.stopPropagation();
                      onSelectComponent(comp.id);
                    }}
                    style={{
                      left: `${xmin}px`,
                      top: `${ymin}px`,
                      width: `${width}px`,
                      height: `${height}px`,
                    }}
                    className={`absolute cursor-pointer border-2 transition-all rounded ${
                      isSelectedComp
                        ? "border-black bg-black/10 ring-4 ring-black/20 z-30"
                        : isRelatedToSelectedNet
                        ? "border-emerald-600 bg-emerald-500/10 ring-2 ring-emerald-500/30 z-20"
                        : isLowConf
                        ? "border-amber-500 bg-amber-500/10 z-10 hover:border-black"
                        : "border-black/60 bg-black/5 hover:border-black hover:bg-black/10 z-10"
                    }`}
                  >
                    {/* Component Label Tag */}
                    <div className="absolute -top-6 left-0 bg-black text-white text-[10px] font-mono font-bold px-1.5 py-0.5 rounded shadow flex items-center gap-1 whitespace-nowrap">
                      <span>{comp.id}</span>
                      <span className="opacity-75 font-normal">({comp.type})</span>
                      {isLowConf && <AlertTriangle className="w-3 h-3 text-amber-400 ml-0.5" />}
                    </div>
                  </div>
                )}

                {/* Component Terminals */}
                {showTerminals &&
                  comp.terminals.map((t) => {
                    const termRef = `${comp.id}.${t.id}`;
                    const netId = termToNet[termRef] || t.net;
                    const isSelectedTerm =
                      selection.type === "terminal" && selection.terminalId === termRef;
                    const isSelectedNetTerm =
                      selection.type === "net" && selection.netId === netId;
                    const isTermLowConf = (t.confidence ?? comp.confidence) < 0.70;

                    return (
                      <div
                        key={termRef}
                        onClick={(e) => {
                          e.stopPropagation();
                          if (netId) onSelectNet(netId);
                          else onSelectTerminal(termRef);
                        }}
                        title={`${termRef} → ${netId || "No Net"} (${Math.round((t.confidence ?? 1) * 100)}%)`}
                        style={{
                          left: `${t.position[0] - 6}px`,
                          top: `${t.position[1] - 6}px`,
                        }}
                        className={`absolute w-3 h-3 rounded-full cursor-pointer border-2 transition-all z-40 ${
                          isSelectedTerm || isSelectedNetTerm
                            ? "bg-emerald-500 border-black scale-125 ring-4 ring-emerald-300"
                            : isTermLowConf
                            ? "bg-amber-500 border-red-600 animate-pulse"
                            : "bg-white border-black hover:scale-125 hover:bg-black"
                        }`}
                      />
                    );
                  })}
              </React.Fragment>
            );
          })}
        </div>
      </div>
    </div>
  );
};
