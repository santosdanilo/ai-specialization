import type { Metadata } from "next";
import { GeistSans } from "geist/font/sans";
import { GeistMono } from "geist/font/mono";
import { ThemeProvider } from "@/shared/components/ui/theme-provider";
import "./globals.css";

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
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${GeistSans.variable} ${GeistMono.variable} antialiased`}
      >
        <ThemeProvider>{children}</ThemeProvider>
      </body>
    </html>
  );
}
