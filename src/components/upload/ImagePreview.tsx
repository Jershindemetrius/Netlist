"use client";

import React from "react";
import { Play, RotateCcw, FileText, CheckCircle2 } from "lucide-react";

interface ImagePreviewProps {
  imageUrl: string;
  file?: File | Blob | null;
  onAnalyze: () => void;
  onReset: () => void;
  isAnalyzing: boolean;
}

export const ImagePreview: React.FC<ImagePreviewProps> = ({
  imageUrl,
  file,
  onAnalyze,
  onReset,
  isAnalyzing,
}) => {
  const fileName = file && "name" in file ? file.name : "circuit_diagram.png";
  const fileSize = file && "size" in file ? `${(file.size / 1024 / 1024).toFixed(2)} MB` : "Sample File";

  return (
    <div className="w-full max-w-4xl mx-auto my-6 bg-white border border-neutral-200 rounded-xl shadow-sm overflow-hidden">
      <div className="flex items-center justify-between px-6 py-4 border-b border-neutral-200 bg-neutral-50/50">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-neutral-100 rounded-md border border-neutral-200">
            <FileText className="w-5 h-5 text-black" />
          </div>
          <div>
            <h4 className="font-mono text-sm font-bold text-neutral-900">{fileName}</h4>
            <p className="font-mono text-xs text-neutral-500">{fileSize} • Ready for analysis</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={onReset}
            disabled={isAnalyzing}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-mono font-medium text-neutral-600 hover:text-black border border-neutral-300 rounded-md hover:bg-neutral-100 transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Change</span>
          </button>

          <button
            type="button"
            onClick={onAnalyze}
            disabled={isAnalyzing}
            className="inline-flex items-center gap-2 bg-black hover:bg-neutral-800 text-white font-mono text-sm px-6 py-2 rounded-lg font-bold shadow-sm transition-all duration-150 active:scale-95 disabled:opacity-50"
          >
            <Play className="w-4 h-4 fill-white" />
            <span>{isAnalyzing ? "Analyzing..." : "Analyze Circuit"}</span>
          </button>
        </div>
      </div>

      <div className="p-6 bg-neutral-900/5 flex items-center justify-center min-h-[380px] max-h-[550px] overflow-auto">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={imageUrl}
          alt="Circuit Diagram Preview"
          className="max-h-[500px] object-contain rounded-lg border border-neutral-200 shadow-md bg-white"
        />
      </div>
    </div>
  );
};
