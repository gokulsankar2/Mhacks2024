import React, { useEffect, memo, useRef, useState } from 'react';

const key = 'home';

export function HomePage() {
  const videoRef = useRef(null);
  const [capturing, setCapturing] = useState(false);
  const intervalRef = useRef(null);

  useEffect(() => {
    async function initCamera() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (err) {
        console.error('Error accessing camera:', err);
      }
    }
    initCamera();

    return () => {
      if (intervalRef.current !== null) {
        clearInterval(intervalRef.current);
      }
      if (videoRef.current && videoRef.current.srcObject) {
        const stream = videoRef.current.srcObject;
        const tracks = stream.getTracks();
        tracks.forEach(track => track.stop());
      }
    };
  }, []);

  const handleStartCapturing = () => {
    setCapturing(true);
    intervalRef.current = setInterval(takePhotoAndUpload, 1000);
  };

  const handleStopCapturing = () => {
    setCapturing(false);
    clearInterval(intervalRef.current);
    intervalRef.current = null;
  };

  const takePhotoAndUpload = async () => {
    if (!videoRef.current) return;

    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;

    context.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(async (blob) => {
      if (blob) {
        await handleUpload(blob);
      }
    }, 'image/jpeg');
  };

  const handleUpload = async (blob) => {
    const data = new FormData();
    const filename = `photo_${Date.now()}.jpg`;
    data.append('image', blob, filename);

    try {
      const response = await fetch('http://localhost:5000/upload', {
        method: 'POST',
        body: data,
      });

      if (!response.ok) {
        const errorMessage = await response.text();
        console.error('Error: ', errorMessage);
      }
    } catch (error) {
      console.error('Error: ', error);
    }
  };

  return (
    <div>
      <div style={{ textAlign: 'center', margin: '20px 0' }}>
        {capturing ? (
          <button onClick={handleStopCapturing} style={{ backgroundColor: 'blue', color: 'white', padding: '10px 20px', margin: '0 10px' }}>
            Stop
          </button>
        ) : (
          <button onClick={handleStartCapturing} style={{ backgroundColor: 'blue', color: 'white', padding: '10px 20px', margin: '0 10px' }}>
            Start Capturing
          </button>
        )}
      </div>
      <video ref={videoRef} autoPlay style={{ width: '100%', height: 'auto' }} />
    </div>
  );
}

export default memo(HomePage);