// net/web/src/app/layout.tsx

export const metadata = { title: "OHSUpath", description: "OHSUpath Web" };
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ margin: 0, fontFamily: "ui-sans-serif,system-ui" }}>
        {children}
      </body>
    </html>
  );
}
