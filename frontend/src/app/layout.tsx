import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Intentify AI — Autonomous Prompt Intelligence Platform",
  description: "Enterprise prompt intelligence converting raw intent into calibrated 9-part Master Prompts via local tensor pipelines.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full antialiased dark">
      <body className="min-h-full flex flex-col bg-slate-950 text-slate-100 font-sans selection:bg-indigo-500 selection:text-white">
        {children}
      </body>
    </html>
  );
}
