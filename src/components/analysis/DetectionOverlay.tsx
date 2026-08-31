"use client";

import React, { useState, useRef } from "react";
import { CircuitGraphResponse, SelectionState } from "../../lib/types";
import { ZoomIn, ZoomOut, RotateCcw, AlertTriangle, Layers, Maximize2, X, FileText, Image as ImageIcon } from "lucide-react";
import { exportGraphAsJpeg, exportReportAsPdf } from "../../lib/export";

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
  const [isFullscreen, setIsFullscreen] = useState(false);

  const containerRef = useRef<HTMLDivElement>(null);

  // Map terminal refs to net IDs
  const termToNet: Record<string, string> = {};
  Object.entries(data.nets || {}).forEach(([netId, termRefs]) => {
    termRefs.forEach((ref) => {
      termToNet[ref] = netId;
    });
  });

  const renderOverlayContent = () => (
    <div
      className="relative inline-block transition-transform duration-150 origin-center"
      style={{ transform: `scale(${zoom})` }}
    >
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src={imageUrl}
        alt="Circuit Analysis View"
        className="max-w-none block rounded-lg border border-slate-200 shadow-xs bg-white"
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
                stroke={isUncertain ? "#f59e0b" : "#4f46e5"}
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
                className={`absolute cursor-pointer border-2 transition-all rounded-lg ${
                  isSelectedComp
                    ? "border-indigo-600 bg-indigo-500/10 ring-4 ring-indigo-500/20 z-30 shadow-md"
                    : isRelatedToSelectedNet
                    ? "border-emerald-600 bg-emerald-500/10 ring-2 ring-emerald-500/30 z-20"
                    : isLowConf
                    ? "border-amber-500 bg-amber-500/10 z-10 hover:border-indigo-600"
                    : "border-slate-800/70 bg-slate-900/5 hover:border-indigo-600 hover:bg-indigo-500/10 z-10"
                }`}
              >
                {/* Component Label Tag */}
                <div className="absolute -top-6 left-0 bg-slate-900 text-white text-[11px] font-semibold px-2 py-0.5 rounded-md shadow-xs flex items-center gap-1 whitespace-nowrap">
                  <span>{comp.id}</span>
                  <span className="opacity-75 text-[10px]">({comp.type})</span>
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
                        ? "bg-emerald-500 border-white scale-125 ring-4 ring-emerald-300 shadow-xs"
                        : isTermLowConf
                        ? "bg-amber-500 border-rose-600 animate-pulse"
                        : "bg-white border-slate-900 hover:scale-125 hover:bg-indigo-600 hover:border-white"
                    }`}
                  />
                );
              })}
          </React.Fragment>
        );
      })}
    </div>
  );

  return (
    <>
      <div className="w-full bg-white border border-slate-200 rounded-xl overflow-hidden shadow-xs flex flex-col h-full">
        {/* Controls Bar */}
        <div className="flex flex-wrap items-center justify-between gap-2 px-4 py-2.5 bg-slate-50 border-b border-slate-200 text-xs font-semibold">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-indigo-50 text-indigo-600">
              <Layers className="w-4 h-4" />
            </div>
            <span className="text-slate-800 font-semibold mr-1">Overlay:</span>

            <button
              type="button"
              onClick={() => setShowBboxes(!showBboxes)}
              className={`px-2.5 py-1 rounded-lg text-xs font-medium border transition-colors cursor-pointer ${
                showBboxes
                  ? "bg-indigo-600 text-white border-indigo-600 shadow-2xs"
                  : "bg-white text-slate-600 border-slate-200 hover:bg-slate-100"
              }`}
            >
              Components ({data.components?.length || 0})
            </button>

            <button
              type="button"
              onClick={() => setShowTerminals(!showTerminals)}
              className={`px-2.5 py-1 rounded-lg text-xs font-medium border transition-colors cursor-pointer ${
                showTerminals
                  ? "bg-indigo-600 text-white border-indigo-600 shadow-2xs"
                  : "bg-white text-slate-600 border-slate-200 hover:bg-slate-100"
              }`}
            >
              Terminals
            </button>
          </div>

          <div className="flex items-center gap-1.5">
            <button
              type="button"
              onClick={() => setZoom((z) => Math.max(0.6, z - 0.2))}
              className="p-1.5 rounded-lg border border-slate-200 bg-white text-slate-700 hover:bg-slate-100 cursor-pointer"
              title="Zoom Out"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <span className="text-xs font-semibold text-slate-600 px-1">{Math.round(zoom * 100)}%</span>
            <button
              type="button"
              onClick={() => setZoom((z) => Math.min(2.5, z + 0.2))}
              className="p-1.5 rounded-lg border border-slate-200 bg-white text-slate-700 hover:bg-slate-100 cursor-pointer"
              title="Zoom In"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>

            <button
              type="button"
              onClick={() => exportGraphAsJpeg("detection-overlay-canvas")}
              className="p-1.5 rounded-lg border border-slate-200 bg-white text-slate-700 hover:bg-slate-100 cursor-pointer"
              title="Download JPEG"
            >
              <ImageIcon className="w-3.5 h-3.5 text-emerald-600" />
            </button>

            <button
              type="button"
              onClick={() => exportReportAsPdf("detection-overlay-canvas")}
              className="p-1.5 rounded-lg border border-slate-200 bg-white text-slate-700 hover:bg-slate-100 cursor-pointer"
              title="Download PDF"
            >
              <FileText className="w-3.5 h-3.5 text-indigo-600" />
            </button>

            <button
              type="button"
              onClick={() => setIsFullscreen(true)}
              className="p-1.5 rounded-lg border border-slate-200 bg-white text-slate-700 hover:bg-slate-100 cursor-pointer ml-1"
              title="Full Screen View"
            >
              <Maximize2 className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Overlay Canvas Viewport */}
        <div
          id="detection-overlay-canvas"
          ref={containerRef}
          className="relative flex-1 bg-slate-100/50 overflow-auto flex items-center justify-center p-4 min-h-[420px]"
        >
          {renderOverlayContent()}
        </div>
      </div>

      {/* Full Screen Modal Overlay */}
      {isFullscreen && (
        <div className="fixed inset-0 z-50 bg-slate-900/80 backdrop-blur-xs flex items-center justify-center p-4 md:p-8 animate-in fade-in duration-200">
          <div className="bg-white rounded-2xl w-full h-full max-w-7xl max-h-[92vh] flex flex-col overflow-hidden shadow-2xl border border-slate-200">
            <div className="flex items-center justify-between px-6 py-4 bg-slate-900 text-white border-b border-slate-800">
              <div className="flex items-center gap-3">
                <Layers className="w-5 h-5 text-indigo-400" />
                <h3 className="font-bold text-base">Full Screen Detection Overlay</h3>
              </div>
              <div className="flex items-center gap-3">
                <button
                  type="button"
                  onClick={() => exportGraphAsJpeg("fullscreen-overlay-canvas")}
                  className="px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-white font-semibold rounded-xl text-xs flex items-center gap-1.5 cursor-pointer"
                >
                  <ImageIcon className="w-4 h-4 text-emerald-400" />
                  <span>Download JPEG</span>
                </button>
                <button
                  type="button"
                  onClick={() => exportReportAsPdf("fullscreen-overlay-canvas")}
                  className="px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-xl text-xs flex items-center gap-1.5 cursor-pointer"
                >
                  <FileText className="w-4 h-4" />
                  <span>Download PDF</span>
                </button>
                <button
                  type="button"
                  onClick={() => setIsFullscreen(false)}
                  className="p-2 hover:bg-slate-800 rounded-xl text-slate-300 hover:text-white cursor-pointer"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>
            <div id="fullscreen-overlay-canvas" className="flex-1 bg-slate-100/50 p-6 overflow-auto flex items-center justify-center">
              {renderOverlayContent()}
            </div>
          </div>
        </div>
      )}
    </>
  );
};
