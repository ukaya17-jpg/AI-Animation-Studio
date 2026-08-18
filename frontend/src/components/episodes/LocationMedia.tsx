import { useEffect, useRef, useState } from 'react'

type LocationMediaProps = {
  videoSrc: string
  imageSrc: string
  alt: string
  className: string
}

/** Ambient location loop that only plays while scrolled into view; falls back to a still image on load failure. */
export function LocationMedia({ videoSrc, imageSrc, alt, className }: LocationMediaProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const [videoFailed, setVideoFailed] = useState(false)

  useEffect(() => {
    const video = videoRef.current
    if (!video || videoFailed) return

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          void video.play().catch(() => {})
        } else {
          video.pause()
        }
      },
      { threshold: 0.25 },
    )
    observer.observe(video)
    return () => observer.disconnect()
  }, [videoFailed])

  if (videoFailed) {
    return <img src={imageSrc} alt={alt} className={className} />
  }

  return (
    <video
      ref={videoRef}
      className={className}
      src={videoSrc}
      poster={imageSrc}
      aria-label={alt}
      muted
      loop
      playsInline
      preload="none"
      onError={() => setVideoFailed(true)}
    >
      <img src={imageSrc} alt={alt} className={className} />
    </video>
  )
}
