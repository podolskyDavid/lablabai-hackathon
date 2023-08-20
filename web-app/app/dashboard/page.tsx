'use client'

import React from 'react';
import {useRouter, useSearchParams, useParams } from 'next/navigation'
import Papa from 'papaparse';

import {
    Table,
    TableBody,
    TableCaption,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"
import {Button} from "@/components/ui/button"
import {Textarea} from "@/components/ui/textarea"
import { ScrollArea } from "@/components/ui/scroll-area"
import { createClient } from '@supabase/supabase-js'
import { useState, useEffect } from "react";


async function getTasksByUser(email: string) {
    const supabase = createClient('https://eiruqjgfkgoknuhihfha.supabase.co', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVpcnVxamdma2dva251aGloZmhhIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTI0MzQxNTcsImV4cCI6MjAwODAxMDE1N30.HKZHbuiB2r8NN367J0LkD2UgwhaqJS2f0Ux9ezCFETA')
    const {data, error} = await supabase
    .from('db_steps')
    .select()
    .eq('user_id', email)
    return data;
}


export default function Dashboard() {
    const init = [{ step_id: "1_1", created_at: "2023-08-19T13:22:09.06096+00:00", user_id: "alex@example.com", transformation: "start", df_frontend: "https://eiruqjgfkgoknuhihfha.supabase.co/storage/v1/object/public/bucket_steps/alex@example.com/df_frontend_1_1.csv" }];
    const [data, setData] = useState(init);
    const arr: unknown[] = [["a"],["1"],["2"],["3"],["4"]]
    const h = ["a"]
    const [frame, setFrame] = useState(arr)
    const [headers, setHeaders] = useState(arr)
    const [curr, setCurr] = useState("");
    const handleButtonClick = async (step_id:any) => {
        setCurr(step_id);
        const fr = await downloadAndParseCSV(data.find(obj => obj.step_id === step_id)?.df_frontend)
        if(fr) {
            setFrame(fr.data.slice(1))
            setHeaders(fr.data[0])
            console.log(headers)
        }
    };
    function AgentStepsArea() {
        useEffect(() => {
            setTimeout(async () =>  {
                let input = await getTasksByUser("coder@example.com");
                if(input) {
                    setData(input)
                }
            }, 1000)
        })



        return (
            <ScrollArea className="h-full w-full">
                <div className="p-4">
                    <h4 className="mb-4 text-sm font-medium leading-none">Agent Actions History</h4>
                    {data.map((tag) => (
                        <div key={tag.step_id}>
                            <div className="flex items-center justify-between mb-2" key={tag.step_id + 1000}>
                                <Button variant="outline" className="w-full" onDoubleClick={() => handleButtonClick(tag.step_id)}>{tag.step_id}</Button>
                            </div>
                            {curr === tag.step_id && (
                                <div id={tag.step_id}>
                                <p>{tag.transformation}</p>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </ScrollArea>
        )
    }

    const downloadAndParseCSV = async (url:any) => {
        try {
          const response = await fetch(url);
          const csvData = await response.text();
          const parsed = Papa.parse(csvData);
          console.log(parsed);
          return parsed;
        } catch (error) {
          console.error('Error downloading or parsing the CSV file:', error);
        }
      };


    return (
        <div className="flex flex-col lg:flex-row h-screen">
            <div className="lg:w-7/12 bg-transparent p-4 border border-white rounded-sm m-4">
                <Table>
                    <TableCaption>A list of your recent invoices.</TableCaption>
                    <TableHeader>
                        <TableRow>
                            {headers && headers.map((rowData, index) =>
                                (<TableHead key={index}>
                                {rowData.toString()}
                              </TableHead>))}
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {frame &&
                            frame.map((rowData, index) => (
                                <TableRow key={index}>
                                  {rowData && rowData.map((cellData, cellIndex) => (
                                    <TableCell key={cellIndex}>{cellData}</TableCell>
                                  ))}
                                </TableRow>
                              ))}
                    </TableBody>
                </Table>
            </div>
            <div className="lg:w-5/12 flex flex-col">
                <div className="bg-transparent h-1/2 p-4 border border-white rounded-sm m-4 ml-0 mb-2">

                    <AgentStepsArea />

                </div>
                <div className="bg-transparent h-1/2 p-4 border border-white rounded-sm m-4 ml-0 mt-2">
                    <div className="flex flex-col w-full gap-2">
                        <Textarea placeholder="Type your message here." className="flex-grow"/>
                        <Button>Send message</Button>
                    </div>
                </div>
            </div>
        </div>
    )
}
