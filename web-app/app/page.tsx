'use client'

import React, { useState, ChangeEvent } from 'react';
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"

interface Props {
  onSelectFile: (file: File | null) => void;
}

export default function Home() {
  const handleFileUpload = (e: ChangeEvent<HTMLInputElement>) => {
    console.log("From onFileUploadChange");
  };

  return (
    <div className="p-6 rounded-lg shadow-md flex flex-col items-center">
      <h1 className="text-5xl mb-4">QUANTILE</h1>
      <h1 className="text-2xl mb-4">Clean your data using QUADRO</h1>
      <h1 className="text-2xl mb-4">Insert a data file to start:</h1>
      <input className="block w-1/2 text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400" onChange={handleFileUpload} aria-describedby="file_input_help" id="file_input" type="file" accept=".csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel" />
      <p className="mt-1 text-sm text-gray-500 dark:text-gray-300" id="file_input_help">.csv, .xsl, .xslx</p>
      <p className="text-2xl my-4">Describe the data columns briefly:</p>
      <Textarea className="w-1/2 mb-4" placeholder="Type your message here." />
      <Button>Send message</Button>
    </div>
  );
};
