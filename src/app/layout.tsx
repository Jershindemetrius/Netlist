import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "NETLIST — Hand-Drawn Circuit to Canonical Graph & Netlist",
  description: "Production Computer Vision Pipeline converting hand-drawn circuit photographs into simulation-ready SPICE netlists.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col bg-[#fafafa] text-neutral-900 selection:bg-black selection:text-white">
        {children}
      </body>
    </html>
  );
}
