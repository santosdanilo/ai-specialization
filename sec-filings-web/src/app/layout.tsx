import type { Metadata } from "next";
// Corrected imports for Geist and Geist Mono
import { GeistSans } from "geist/font/sans"; // Import from 'geist/font/sans'
import { GeistMono } from "geist/font/mono"; // Import from 'geist/font/mono'
import "./globals.css";

// You no longer need to call Geist or Geist_Mono as functions
// Just assign the imported font objects directly
const geistSans = GeistSans;
const geistMono = GeistMono;

export const metadata: Metadata = {
  title: "SEC Filings RAG",
  description: "Investment intelligence using RAG over SEC filings: fundamental, momentum, and sentiment multi-stream analysis",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}