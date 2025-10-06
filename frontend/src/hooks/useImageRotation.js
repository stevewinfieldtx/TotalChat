import { useState, useCallback, useEffect } from 'react';
import api from '../services/api';

export const useImageRotation = (characterId, emotion = 'neutral') => {
  const [currentImage, setCurrentImage] = useState(null);
  const [imagePool, setImagePool] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState(null);

  // Load character's existing images on mount
  useEffect(() => {
    loadCharacterImages();
  }, [characterId]);

  const loadCharacterImages = async () => {
    try {
      const images = await api.getCharacterImages(characterId);
      setImagePool(images);
      if (images.length > 0 && !currentImage) {
        setCurrentImage(images[0]);
      }
    } catch (err) {
      console.error('Failed to load character images:', err);
    }
  };

  const rotateImage = useCallback((emotion = 'neutral') => {
    if (imagePool.length === 0) return;

    // Filter images by emotion if available
    const emotionImages = imagePool.filter(img => 
      img.emotion === emotion || !img.emotion
    );

    if (emotionImages.length === 0) {
      // Fallback to any image
      const randomIndex = Math.floor(Math.random() * imagePool.length);
      setCurrentImage(imagePool[randomIndex]);
      return;
    }

    // Get random image from emotion-filtered pool
    const randomIndex = Math.floor(Math.random() * emotionImages.length);
    setCurrentImage(emotionImages[randomIndex]);
  }, [imagePool]);

  const generateNewImage = useCallback(async (prompt, emotion = 'neutral') => {
    setIsGenerating(true);
    setError(null);

    try {
      const newImage = await api.generateImage({
        characterId,
        prompt,
        emotion
      });

      // Add to pool and set as current
      setImagePool(prev => [...prev, newImage]);
      setCurrentImage(newImage);

      return newImage;
    } catch (err) {
      const errorMessage = err.message || 'Failed to generate image';
      setError(errorMessage);
      throw err;
    } finally {
      setIsGenerating(false);
    }
  }, [characterId]);

  // Auto-rotate based on emotion changes
  useEffect(() => {
    if (emotion) {
      rotateImage(emotion);
    }
  }, [emotion, rotateImage]);

  return {
    currentImage,
    imagePool,
    isGenerating,
    error,
    rotateImage,
    generateNewImage,
    refreshImages: loadCharacterImages
  };
};

export default useImageRotation;