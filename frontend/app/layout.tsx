import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Agricultural Market Intelligence",
  description: "Modern dashboard for agricultural market insights and price predictions",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
