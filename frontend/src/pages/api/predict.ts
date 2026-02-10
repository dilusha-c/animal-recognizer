// pages/api/predict.ts
import type { NextApiRequest, NextApiResponse } from 'next';
import { IncomingForm } from 'formidable';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

export const config = {
  api: {
    bodyParser: false,
  },
};

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  // Use system temp directory instead of public folder
  const tempDir = path.join(os.tmpdir(), 'animal-recognizer-uploads');
  
  // Ensure temp directory exists
  if (!fs.existsSync(tempDir)) {
    fs.mkdirSync(tempDir, { recursive: true });
  }

  const form = new IncomingForm({ 
    uploadDir: tempDir,
    keepExtensions: true,
    filter: (part) => {
      const isImage = part.mimetype?.includes('image') ?? false;
      const allowedExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'];
      const hasValidExtension = allowedExtensions.some(ext => 
        part.originalFilename?.toLowerCase().endsWith(ext) ?? false
      );
      return isImage && hasValidExtension;
    }
  });
  
  form.parse(req, async (err: Error | null, fields: Record<string, unknown>, files: Record<string, unknown>) => {
    if (err) {
      console.error('Form parsing error:', err);
      return res.status(400).json({ error: 'Failed to parse form data' });
    }

    if (!files.image) {
      return res.status(400).json({ error: 'No image file provided' });
    }

    const imageFile = Array.isArray(files.image) ? files.image[0] : files.image;
    const imagePath = imageFile.filepath;
    
    try {
      // Read image from temp location
      const imageBuffer = fs.readFileSync(imagePath);
      
      // Delete image from temp directory immediately after reading
      fs.unlinkSync(imagePath);
      
      // Get backend API URL from env or use default
      const backendUrl = (process.env.NEXT_PUBLIC_API_URL || 'https://dmdchamika1-animal-recognizer-api.hf.space').replace(/\/$/, '');
      
      // Create FormData and send to backend
      const formData = new FormData();
      formData.append('file', new Blob([imageBuffer], { type: 'image/*' }), 'image.jpg');
      
      console.log('Sending request to:', `${backendUrl}/predict`);
      
      const backendResponse = await fetch(`${backendUrl}/predict`, {
        method: 'POST',
        body: formData,
      });
      
      if (!backendResponse.ok) {
        const errorText = await backendResponse.text();
        console.error('Backend error:', errorText);
        return res.status(backendResponse.status).json({ 
          error: 'Backend prediction failed',
          details: errorText 
        });
      }
      
      const data = await backendResponse.json();
      console.log('Backend response:', data);
      
      res.status(200).json({ prediction: data.prediction });
    } catch (err) {
      console.error('Prediction error:', err);
      res.status(500).json({ 
        error: 'Prediction failed', 
        details: err instanceof Error ? err.message : 'Unknown error'
      });
    }
  });
}
