import "./globals.css";
import type { Metadata } from "next";
import { Inter } from "next/font/google";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "NETLIST — Circuit Diagram Graph & SPICE Extraction Engine",
  description: "Computer vision and graph extraction platform converting hand-drawn circuit schematics into canonical node graphs and simulation-ready SPICE netlists.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={inter.variable}>
      <body className={`${inter.className} min-h-screen flex flex-col bg-slate-50 text-slate-900 selection:bg-slate-900 selection:text-white antialiased`}>
        {children}
      </body>
    </html>
  );
}
