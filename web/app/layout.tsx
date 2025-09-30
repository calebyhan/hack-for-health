import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Providers from './providers'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Healthy Eating Helper',
  description: 'Photo → nutrition breakdown → health score. AI-powered food analysis for healthier choices.',
  keywords: ['nutrition', 'food analysis', 'health', 'AI', 'meal tracking'],
  authors: [{ name: 'Healthy Eating Helper Team' }],
  creator: 'Healthy Eating Helper',
  publisher: 'Healthy Eating Helper',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL('http://localhost:3000'),
  openGraph: {
    title: 'Healthy Eating Helper',
    description: 'AI-powered food analysis for healthier choices',
    url: 'http://localhost:3000',
    siteName: 'Healthy Eating Helper',
    images: [
      {
        url: '/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'Healthy Eating Helper - AI Food Analysis',
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Healthy Eating Helper',
    description: 'AI-powered food analysis for healthier choices',
    images: ['/og-image.jpg'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="scroll-smooth">
      <body className={inter.className}>
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100">
          <div className="relative">
            {/* Background decoration */}
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_1px_1px,_theme(colors.slate.300)_1px,_transparent_0)] [background-size:20px_20px] opacity-20"></div>

            {/* Main content */}
            <div className="relative">
              <Providers>
                {children}
              </Providers>
            </div>
          </div>
        </div>
      </body>
    </html>
  )
}