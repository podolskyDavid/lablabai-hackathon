'use client'

import React, { useState, ChangeEvent } from 'react';
import { useRouter } from 'next/router'

interface Props {
  onSelectFile: (file: File | null) => void;
}

const Home: React.FC<Props> = ({ onSelectFile }) => {
  const router = useRouter();
  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] || null;
    if (file) {
      const reader = new FileReader();
      reader.onload = (e: ProgressEvent<FileReader>) => {
        const csvText = e.target?.result as string;
        parseCSV(csvText);
      };
      reader.readAsText(file);
    }
  };

  const [fileData, setFileData] = useState<Record<string, string>[]>([]);
  const parseCSV = (csvText: string) => {
    const lines = csvText.split("\n");
    const headers = lines[0].split(",");
    const parsedData: Record<string, string>[] = [];
    for (let i = 1; i < lines.length; i++) {
      const currentLine = lines[i].split(",");
      if (currentLine.length === headers.length) {
        const row: Record<string, string> = {};
        for (let j = 0; j < headers.length; j++) {
          row[headers[j].trim()] = currentLine[j].trim();
        }
        parsedData.push(row);
      }
    }
    // Assuming setCsvData is a state setter function
    // e.g., const [csvData, setCsvData] = useState<Record<string, string>[]>([]);
    setFileData(parsedData);
    router.push(`/editor?data=${JSON.stringify(parsedData)}`);

  };

  return (
    <div className="p-6 rounded-lg shadow-md flex flex-col items-center">
      <h1 className="text-5xl mb-4">QUANTILE</h1>
      <h1 className="text-2xl mb-4">Clean your data using QUADRO</h1>
      <h1 className="text-2xl mb-4">Insert a data file to start:</h1>
      <input className="block w-1/2 text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400" onChange={handleFileChange} aria-describedby="file_input_help" id="file_input" type="file" accept=".csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel" />
      <p className="mt-1 text-sm text-gray-500 dark:text-gray-300" id="file_input_help">.csv, .xsl, .xslx</p>
    </div>
  );
};

export default Home;
