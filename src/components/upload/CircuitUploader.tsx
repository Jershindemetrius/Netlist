"use client";

import React, { useRef, useState } from "react";
import { Upload, FileImage, Sparkles, AlertCircle } from "lucide-react";

interface CircuitUploaderProps {
  onImageSelect: (file: File) => void;
  onLoadDemo: () => void;
  isAnalyzing: boolean;
}

export const CircuitUploader: React.FC<CircuitUploaderProps> = ({
  onImageSelect,
  onLoadDemo,
  isAnalyzing,
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [dragError, setDragError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    setDragError(null);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      const file = files[0];
      if (file.type.startsWith("image/")) {
        onImageSelect(file);
      } else {
        setDragError("Please upload a valid image file (PNG, JPG, JPEG, WebP).");
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onImageSelect(e.target.files[0]);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto my-6">
      {/* Technical Outer Card matching Screenshot 2 */}
      <div className="corner-brackets relative bg-white border border-neutral-300 p-8 md:p-12 shadow-sm rounded-none text-center">
        {/* Corner Marks (bottom) */}
        <div className="absolute -bottom-0.5 -left-0.5 w-3 h-3 border-b-2 border-l-2 border-black pointer-events-none" />
        <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 border-b-2 border-r-2 border-black pointer-events-none" />

        <h1 className="text-3xl md:text-5xl font-sans font-black tracking-tight text-neutral-950 mb-4">
          Convert a circuit drawing into a graph.
        </h1>

        <p className="max-w-2xl mx-auto font-mono text-sm text-neutral-600 mb-8 leading-relaxed">
          Upload a photograph of a hand-drawn electronic schematic. NETLIST detects components, terminals, wires, and electrical connectivity.
        </p>

        {/* Inner Drop Box Container matching Screenshot 2 */}
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`relative cursor-pointer border border-neutral-300 p-10 transition-all duration-150 ${
            isDragOver
              ? "bg-neutral-100 border-black"
              : "bg-neutral-50/80 hover:bg-neutral-100/60 hover:border-neutral-800"
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="image/png, image/jpeg, image/jpg, image/webp"
            onChange={handleFileChange}
            className="hidden"
          />

          {/* Inner Drop Labels */}
          <div className="absolute top-3 left-4 font-mono text-[11px] font-bold text-neutral-400 uppercase tracking-widest">
            INPUT
          </div>
          <div className="absolute top-3 right-4 font-mono text-[11px] font-bold text-neutral-400 uppercase tracking-widest">
            IMAGE
          </div>
          <div className="absolute bottom-3 right-4 font-mono text-[11px] font-bold text-lime-600 uppercase tracking-widest">
            READY
          </div>

          <div className="flex flex-col items-center justify-center py-6">
            {/* Diamond Upload Icon Box */}
            <div className="w-14 h-14 border border-neutral-400 rotate-45 flex items-center justify-center mb-6 bg-white shadow-sm group-hover:border-black">
              <Upload className="w-6 h-6 text-neutral-800 -rotate-45" />
            </div>

            <span className="font-mono text-sm font-bold text-neutral-900 uppercase tracking-wider">
              DROP A CIRCUIT IMAGE HERE
            </span>
          </div>
        </div>

        {dragError && (
          <div className="mt-4 inline-flex items-center gap-2 text-xs font-mono font-bold text-red-600 bg-red-50 border border-red-200 px-3 py-1.5 rounded">
            <AlertCircle className="w-4 h-4" />
            <span>{dragError}</span>
          </div>
        )}

        {/* Action Buttons matching Screenshot 2 */}
        <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            disabled={isAnalyzing}
            className="bg-black hover:bg-neutral-900 text-white font-mono text-sm font-bold px-8 py-3 rounded-none shadow-sm transition-all active:scale-95"
          >
            [ Select Image ]
          </button>

          <button
            type="button"
            onClick={onLoadDemo}
            disabled={isAnalyzing}
            className="bg-white hover:bg-neutral-100 text-black border border-neutral-400 font-mono text-sm font-bold px-8 py-3 rounded-none shadow-sm transition-all active:scale-95"
          >
            [ Demo Circuit ]
          </button>
        </div>
      </div>
    </div>
  );
};
