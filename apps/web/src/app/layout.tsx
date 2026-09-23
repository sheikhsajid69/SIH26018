import type { Metadata, Viewport } from "next";
import "./globals.css";

export const viewport: Viewport = {
  themeColor: "#001e2b",
  colorScheme: "light dark",
  width: "device-width",
  initialScale: 1,
};

export const metadata: Metadata = {
  metadataBase: new URL("https://landsync.ai"),
  title: {
    default: "LANDSYNC AI — Intelligent Land Record Digitalisation & Spatial Intelligence Platform",
    template: "%s | LANDSYNC AI",
  },
  description:
    "AI-assisted land record intelligence, multi-jurisdiction consistency validation, cadastral GIS spatial verification, and human-in-the-loop review platform developed for Smart India Hackathon 2026 (Problem Statement: SIH26018).",
  applicationName: "LANDSYNC AI",
  authors: [{ name: "Team Void", url: "https://github.com/sheikhsajid69/SIH26018" }],
  generator: "Next.js",
  keywords: [
    "LANDSYNC AI",
    "Smart India Hackathon",
    "SIH26018",
    "Land Records Digitization",
    "Cadastral GIS",
    "Spatial Consistency Validation",
    "Land Deed OCR",
    "Revenue Authority Adapter",
    "Digital Land Profile",
    "Mutation Intelligence",
    "Bigha Guntha Converter",
    "Team Void",
  ],
  referrer: "origin-when-cross-origin",
  creator: "Team Void (Smart India Hackathon)",
  publisher: "Team Void",
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  icons: {
    icon: [
      { url: "/icon.svg", type: "image/svg+xml" },
    ],
    shortcut: "/icon.svg",
    apple: "/icon.svg",
  },
  manifest: "/manifest.json",
  openGraph: {
    title: "LANDSYNC AI — Intelligent Land Record Digitalisation & Spatial Intelligence Platform",
    description:
      "Enterprise-grade AI land record consistency validation, cadastral GIS overlays, SHA-256 evidence provenance, and officer review workflows.",
    url: "https://landsync.ai",
    siteName: "LANDSYNC AI",
    locale: "en_IN",
    type: "website",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "LANDSYNC AI Platform — Digital Land Profile & Spatial Consistency Engine",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "LANDSYNC AI — Intelligent Land Record Digitalisation",
    description:
      "AI-assisted land record consistency validation and cadastral GIS intelligence platform for SIH 2026.",
    creator: "@TeamVoid_SIH",
    images: ["/og-image.png"],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
};

const jsonLd = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "SoftwareApplication",
      "@id": "https://landsync.ai/#software",
      name: "LANDSYNC AI",
      applicationCategory: "GovernmentApplication",
      operatingSystem: "Web Browser",
      url: "https://landsync.ai",
      description:
        "AI-assisted land record consistency validation, cadastral GIS overlays, and human-in-the-loop review platform for Smart India Hackathon 2026 (SIH26018).",
      author: {
        "@type": "Organization",
        name: "Team Void",
        url: "https://github.com/sheikhsajid69/SIH26018",
      },
      offers: {
        "@type": "Offer",
        price: "0",
        priceCurrency: "INR",
      },
      featureList: [
        "Multi-jurisdiction Indian land unit standardization (Bigha, Guntha, Cent, Kanal)",
        "Cadastral GIS polygon boundary validation & IoU spatial matching",
        "Deterministic SHA-256 evidence chain of custody",
        "Human-in-the-loop Revenue Officer discrepancy review queue",
        "14 comprehensive synthetic demonstration scenarios",
      ],
    },
    {
      "@type": "WebSite",
      "@id": "https://landsync.ai/#website",
      url: "https://landsync.ai",
      name: "LANDSYNC AI Platform",
      publisher: {
        "@type": "Organization",
        name: "Team Void",
      },
    },
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
