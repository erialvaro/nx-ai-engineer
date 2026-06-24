import type { ReactNode } from 'react';

export const metadata = {
  title: '{{project_title}}',
  description: 'Cloud-agnostic foundation scaffolded by NX AI Engineer',
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
