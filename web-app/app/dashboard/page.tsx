// @ts-nocheck
'use client'

import React from 'react';
import {useSearchParams} from 'next/navigation'
import Papa from 'papaparse';

import Image from "next/image";
import Link from "next/link";

import { Loader2 } from "lucide-react"

import {
    Table,
    TableBody,
    TableCaption,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog"
import {Button} from "@/components/ui/button"
import {Textarea} from "@/components/ui/textarea"
import {ScrollArea} from "@/components/ui/scroll-area"
import {Input} from "@/components/ui/input"
import {Label} from "@/components/ui/label"
import { ToastAction } from "@/components/ui/toast"
import { useToast } from "@/components/ui/use-toast"

import hljs from 'highlight.js';
import 'highlight.js/styles/github-dark.css';

import {createClient} from '@supabase/supabase-js'
import {useState, useEffect, useRef} from "react";

const CodeBlock = ({language, value}) => {
    const codeEl = useRef(null);

    useEffect(() => {
        hljs.highlightBlock(codeEl.current);
    }, []);

    return (
        <pre className="border-white rounded-md">
      <code ref={codeEl} className={language}>
        {value}
      </code>
    </pre>
    );
};

async function getTasksByUser(email: string) {
    const supabase =
        createClient('https://eiruqjgfkgoknuhihfha.supabase.co',
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVpcnVxamdma2dva251aGloZmhhIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTI0MzQxNTcsImV4cCI6MjAwODAxMDE1N30.HKZHbuiB2r8NN367J0LkD2UgwhaqJS2f0Ux9ezCFETA')
    const {data, error} = await supabase
        .from('db_steps')
        .select()
        .eq('user_id', email)
    return data;
}


export default function Dashboard() {
    const params = useSearchParams()
    let email = params.get("email")
    if (!email) email = "guest@tidyai.tech"
    const init = [
        {
            step_id: "1_1",
            created_at: "2023-08-19T13:22:09.06096+00:00",
            user_id: "alex@example.com",
            transformation: "start",
            explanation: "This is the first step",
            df_frontend: "https://eiruqjgfkgoknuhihfha.supabase.co/storage/v1/object/public/bucket_steps/alex@example.com/df_frontend_1_1.csv",
            code: "def main():\n    print(\"Hello World!\")\n\nif __name__ == \"__main__\":\n    main()",
            latest: false,
        },
        {
            step_id: "1_2",
            created_at: "2023-08-20T14:23:09.06096+00:00",
            user_id: "alex@example.com",
            transformation: "Second State",
            explanation: "This is the second step",
            df_frontend: "https://eiruqjgfkgoknuhihfha.supabase.co/storage/v1/object/public/bucket_steps/alex@example.com/df_frontend_1_2.csv",
            code: "def main():\n    print(\"Hello World!\")\n\nif __name__ == \"__main__\":\n    main()",
            latest: false,
        },
        {
            step_id: "1_3",
            created_at: "2023-08-21T15:03:10.06096+00:00",
            user_id: "alex@example.com",
            transformation: "Third State",
            explanation: "This is the third step",
            df_frontend: "https://eiruqjgfkgoknuhihfha.supabase.co/storage/v1/object/public/bucket_steps/alex@example.com/df_frontend_2_16.csv",
            code: "def main():\n    print(\"Hello World!\")\n\nif __name__ == \"__main__\":\n    main()",
            latest: false,
        },
        {
            step_id: "1_4",
            created_at: "2023-08-21T15:03:10.06096+00:00",
            user_id: "alex@example.com",
            transformation: "Third State",
            explanation: "This is the third step",
            df_frontend: "https://eiruqjgfkgoknuhihfha.supabase.co/storage/v1/object/public/bucket_steps/alex@example.com/df_frontend_2_16.csv",
            code: "def main():\n    print(\"Hello World!\")\n\nif __name__ == \"__main__\":\n    main()",
            latest: true,
        },
    ];
    const [data, setData] = useState(init);
    const arr: unknown[] = [["a"], ["1"], ["2"], ["3"], ["4"]]
    const h = ["a"]
    const [frame, setFrame] = useState(arr)
    const [headers, setHeaders] = useState(arr)
    const [curr, setCurr] = useState("");
    const handleButtonClick = async (step_id: any) => {
        setCurr(step_id);
        const fr = await downloadAndParseCSV(data.find(obj => obj.step_id === step_id)?.df_frontend)
        if (fr) {
            setFrame(fr.data.slice(1))
            setHeaders(fr.data[0])
            console.log(headers)
        }
    };

    const { toast } = useToast()

    function AgentStepsArea() {
        // useEffect(() => {
        //     setTimeout(async () =>  {
        //         let input = await getTasksByUser(email);
        //         if(input) {
        //             setData(input)
        //         }
        //     }, 1000)
        // })


        return (
            <ScrollArea className="h-full w-full">
                <div className="p-4">
                    <h4 className="mb-4 text-sm font-medium leading-none">Agent Actions History</h4>
                    {data.map((tag) => (
                        <div key={tag.step_id}>
                            <div className="flex items-center justify-between space-x-2 mb-2" key={tag.step_id + 1000}>
                                {tag.latest ? (
                                    <Button disabled className="w-2/3">
                                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                        {tag.step_id}
                                    </Button>
                                ) : (
                                    <Button variant="outline" className="w-2/3"
                                            onClick={() => handleButtonClick(tag.step_id)}>
                                        {tag.step_id}
                                    </Button>
                                )}
                                <Dialog>
                                    <DialogTrigger asChild>
                                        <Button variant="secondary" className="w-1/3">More Information</Button>
                                    </DialogTrigger>
                                    <DialogContent className="sm:max-w-[1000px]">
                                        <DialogHeader>
                                            <DialogTitle>{tag.step_id}</DialogTitle>
                                            <DialogDescription>
                                                {tag.explanation}
                                            </DialogDescription>
                                        </DialogHeader>
                                        <div className="grid gap-4 py-4">
                                            <CodeBlock
                                                language="python"
                                                value={`
# This is a Python sample code
def fibonacci(n):
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)

def main():
    num = 10
    print("Fibonacci sequence:")
    for i in range(num):
        print(fibonacci(i))

if __name__ == "__main__":
    main()
`}
                                            />
                                        </div>
                                        <DialogFooter>
                                            <Button onClick={() => {
                                                navigator.clipboard.writeText(tag.code)
                                            }

                                            }>
                                                    Copy Code
                                            </Button>
                                            <Button asChild type="submit">
                                                <a href={tag.df_frontend} target="_blank" rel="noopener noreferrer"
                                                   download>
                                                    Download the Full Data Frame
                                                </a>
                                            </Button>
                                        </DialogFooter>
                                    </DialogContent>
                                </Dialog>
                            </div>
                            {curr === tag.step_id && (
                                <div id={tag.step_id}>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </ScrollArea>
        )
    }

    const downloadAndParseCSV = async (url: any) => {
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
        <div className="flex flex-col h-screen">
            <div className="pt-2 pb-2 m-4 mb-0 relative group">
                <div
                    className="absolute inset-0 bg-gradient-border z-0 group-hover:opacity-100 opacity-0 transition-opacity duration-500 rounded-md"></div>
                <div className="relative z-10 bg-transparent flex flex-row justify-between items-center">
                    <Link href="/">
                        <Image src="/logo-text-white.png" width={100} height={100}
                               alt="white logo"/>
                    </Link>
                    <div className="pr-2">{email}</div>
                </div>
            </div>
            <div className="flex flex-col lg:flex-row flex-grow">
                <div className="lg:w-7/12 bg-transparent p-4 border border-white rounded-sm m-4">
                    <ScrollArea className="h-full w-full">
                        <Table>
                            <TableCaption>Resulting seven rows from the selected agent action step.</TableCaption>
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
                    </ScrollArea>
                </div>
                <div className="lg:w-5/12 flex flex-col">
                    <div className="bg-transparent h-1/2 p-4 border border-white rounded-sm m-4 lg:ml-0 lg:mb-2">

                        <AgentStepsArea/>

                    </div>
                    <div className="bg-transparent h-1/2 p-4 border border-white rounded-sm m-4 lg:ml-0 lg:mt-2">
                        <ScrollArea className="h-full w-full p-4">
                            <div className="flex flex-col w-full gap-2">
                                <Textarea placeholder="Type your message here." className="flex-grow"/>
                                <Button>Send message</Button>
                            </div>
                        </ScrollArea>
                    </div>
                </div>
            </div>
        </div>
    )
}