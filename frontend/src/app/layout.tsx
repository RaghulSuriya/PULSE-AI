import type { Metadata } from "next";
import "./globals.css";
import { Navigation } from "@/components/navigation";

export const metadata: Metadata = {
  title: "PULSE AI - Personal Unified Life Scheduling & Execution Agent",
  description: "Everything important in your digital life. One intelligent plan for your day.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-background text-gray-100 min-h-screen flex antialiased">
        <Navigation />
        <main className="flex-1 ml-64 p-8 min-h-screen max-w-7xl">
          {children}
        </main>
      </body>
    </html>
  );
}
