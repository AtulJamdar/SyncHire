import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Job Finder AI",
  description: "Automate your job search",
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
