import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "LandSync AI — Digital Land Profile",
  description: "Synthetic demo for land-record consistency validation"
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
