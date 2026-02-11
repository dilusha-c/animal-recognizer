import '../styles/globals.css'
import type { AppProps } from 'next/app'
import Head from 'next/head'
import { Analytics } from '@vercel/analytics/react'

export default function App({ Component, pageProps }: AppProps) {
  return (
    <>
      <Head>
        <title>Animal Recognizer</title>
        <meta name="description" content="Identify animals from images using an AI-powered model." />
        <link rel="icon" href="/logo.png" />
      </Head>
      <Component {...pageProps} />
      <Analytics />
    </>
  )
}
