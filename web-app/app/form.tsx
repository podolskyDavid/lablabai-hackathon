'use client'

import React, { useState, ChangeEvent } from 'react';
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import {Input} from "@/components/ui/input"
import axios from 'axios';
import { useRouter } from "next/navigation";


export default function Form() {
  const [email, setEmail] = useState('');
  const [file, setFile] = useState(null);
  const [description, setDescription] = useState('');

  const handleFileChange = (event) => {
    if (event.target.files && event.target.files.length > 0) {
      setFile(event.target.files[0]);
    }
  };
  const router = useRouter();
  const submit = (e) => {

    const formURL = e.target.action
    const data = new FormData()

    // Turn our formData state into data we can use with a form submission
    if(file) {
      const formData = [email, file, description]
      Object.entries(formData).forEach(([key, value]) => {
        data.append(key, value);
      })
    }

    // POST the data to the URL of the form
    fetch(formURL, {
      method: "POST",
      body: data,
      headers: {
        'accept': 'application/json',
      },
    })
    const route = "./dashboard?email=" + email;
    router.push(route)
  }

  return (
    <form className="p-6 rounded-lg shadow-md flex flex-col items-center" action="./dashboard" method="post" onSubmit={submit}>
      <h1 className="text-5xl mb-4">QUANTILE</h1>
      <h1 className="text-2xl mb-4">Clean your data using QUANTILE</h1>
      <h1 className="text-2xl mb-4">Enter your email:</h1>
      <Input type="email" placeholder="Email" onChange={(e) => setEmail(e.target.value)} />
      <h1 className="text-2xl mb-4">Insert a data file to clean:</h1>
      <input className="block w-1/2 text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400" onChange={handleFileChange} aria-describedby="file_input_help" id="file_input" type="file" accept=".csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel" />
      <p className="mt-1 text-sm text-gray-500 dark:text-gray-300" id="file_input_help">.csv, .xsl, .xslx</p>
      <p className="text-2xl my-4">Describe the data columns briefly:</p>
      <Textarea className="w-1/2 mb-4" placeholder="Type your message here." onChange={(e) => setDescription(e.target.value)} />
      <button>Submit</button>
    </form>
  );
};
