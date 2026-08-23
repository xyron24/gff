import "@/styles/globals.css";
import Navbar from "@/components/Navbar";

export const metadata = {
  title: "Mastercard AI Defense Lab | Closed-Loop Payment Security",
  description: "Autonomous Red-Team / Blue-Team AI Defense Lab for Payment Security - Mastercard Innovation Challenge 2026",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <Navbar />
        <main style={{ maxWidth: "1400px", margin: "0 auto", padding: "32px 24px" }}>
          {children}
        </main>
      </body>
    </html>
  );
}
