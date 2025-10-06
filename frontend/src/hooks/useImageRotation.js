import { useEffect, useState } from 'react';

// Rotate through a provided array of image URLs
export const useImageRotation = (images = [], intervalMs = 5000) => {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    if (!images || images.length === 0) return;
    if (index >= images.length) setIndex(0);
    const id = setInterval(() => {
      setIndex((i) => (i + 1) % images.length);
    }, Math.max(1000, intervalMs));
    return () => clearInterval(id);
  }, [images, intervalMs, index]);

  const currentImage = images && images.length > 0 ? images[index] : null;
  return currentImage;
};

export default useImageRotation;