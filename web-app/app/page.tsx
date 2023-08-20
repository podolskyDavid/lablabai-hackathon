import React from 'react';
import axios from 'axios';
import Form from './form';

export default async function Home() {
  async function handleSubmit(childData) {
    const {email, file, description} = childData
    if(file) {
      const formData = new FormData();
      formData.append('name', email);
      formData.append('file', file);
      formData.append('description', description);

      try {
        const response = await axios.post('/api/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        console.log('Upload successful:', response.data);
      } catch (error) {
        console.error('Error uploading file:', error);
      }
    }
  };

  return (
    <Form></Form>
  );
};
