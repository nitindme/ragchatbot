import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Delhi Police Chatbot - AI-powered Document Assistant',
  description: 'AI-powered chatbot with document knowledge',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
