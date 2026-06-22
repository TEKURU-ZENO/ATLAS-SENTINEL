import type { ReactNode } from "react";
import { Shell } from "../components/layout/shell";
import "./globals.css";

export const metadata = {
  title: "ATLAS Sentinel",
  description: "Industrial Safety Intelligence Operating System"
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Shell>{children}</Shell>
      </body>
    </html>
  );
}
