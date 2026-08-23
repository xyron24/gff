import "@/styles/globals.css";
import Navbar from "@/components/Navbar";

export const metadata = {
  title: "Mastercard AI Defense Lab | Mission-Critical Payment Security Operations",
  description: "Enterprise closed-loop Red-Team/Blue-Team AI Defense Console for Payment Security - Mastercard Innovation Challenge 2026",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#090A0F] text-[#F1F5F9] antialiased min-h-screen flex flex-col font-sans selection:bg-[#FF5F00]/30 selection:text-white">
        <Navbar />
        <main className="flex-1 w-full p-2 sm:p-3 overflow-x-hidden">
          {children}
        </main>
      </body>
    </html>
  );
}
