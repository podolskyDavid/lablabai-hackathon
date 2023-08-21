'use client'

import React, {FC} from 'react';
import {useSearchParams} from 'next/navigation'
import Papa from 'papaparse';

import Image from "next/image";
import Link from "next/link";

import {Loader2} from "lucide-react"
import {ListStart} from 'lucide-react';

export const dynamic = 'force-dynamic';

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
import {ToastAction} from "@/components/ui/toast"
import {useToast} from "@/components/ui/use-toast"

import hljs from 'highlight.js';
import 'highlight.js/styles/github-dark.css';

import {createClient} from '@supabase/supabase-js'
import {useState, useEffect, useRef} from "react";

const CodeBlock: FC<{ language: string, value: string }> = ({language, value}) => {
    const codeEl = useRef<HTMLElement | null>(null);

    useEffect(() => {
        if (codeEl && codeEl.current) {
            hljs.highlightBlock(codeEl.current);
        }
    }, []);

    return (
        <pre className="border-white rounded-md overflow-x-scroll">
            <code ref={codeEl} className={language}>
                {value}
            </code>
        </pre>
    );
}

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
    console.log(email)
    let tid = params.get("taskid")
    console.log(tid)
    if (!email) email = "guest@tidyai.tech"
    const init: any[] | (() => any[]) = [];
    const [data, setData] = useState(init);
    const arr: unknown[] = [["Stephen","Tyler","7452 Terrace At the Plaza road","SomeTown","SD", "91234"], ["John Da Man","Repici","120 Jefferson St.","Riverside", "NJ","08075"], ["Jack","McGinnis","220 hobo Av.","Phila", "PA","09119"], ["John","Doe","120 jefferson st.","Riverside", "NJ", "08075"], ["Joan the bone", "Anne","Jet","9th", "at Terrace plc","Desert City","CO","00123"], ["Andrew", "John", "1st Str.", "New York", "NY", "10000"]]
    const h = ["First Name","Last Name","Address 1","Address 2", "State", "Postcode"]
    const [frames, setFrames] = useState([{}, {}])
    const [frame, setFrame] = useState(arr)
    const [df, setDf] = useState<any[] | null>(null);
    const [headers, setHeaders] = useState(h)
    const [curr, setCurr] = useState("");
    const [cnt, setCnt] = useState(0);

    const queue = 0;
    const [queueData, setQueueData] = useState(queue);
    const handleQueueDataButtonClick = () => {
        setQueueData(prevQueueData => prevQueueData + 1);
    };

    useEffect(() => {
        // const eventSource = new EventSource(`http://0.0.0.0:80/stream?task_id=${tid}`);
        const eventSource = new EventSource(`https://agent-dnrxaaj6sq-lm.a.run.app/stream?task_id=${tid}`);
        // const eventSource = new EventSource(`https://agent-dnrxaaj6sq-lm.a.run.app/stream?task_id=${tid}`);
        eventSource.addEventListener("open", (e) => {
            console.log("open")
        })
        eventSource.addEventListener(`Code executed (new_step_count)`, async (e) => {
            let d = [...data]
            let json_parsed = JSON.parse(e.data)
            console.log(json_parsed)

            let df = await downloadAndParseCSV(json_parsed.df_frontend_url);
            setDf(df);
        })
        eventSource.addEventListener(`Explanation and code generated (new_code_and_explanation)`, async (e) => {
            // let d = [...data]
            // let json_parsed = JSON.parse(e.data)
        })
    });

    const handleButtonClick = async (step_id: any) => {
        setCurr(step_id);
        const fr = await downloadAndParseCSV(data.find(obj => obj.step_id === step_id)?.df_frontend)
        if (fr) {
            setFrame(fr.slice(1));
            setHeaders(fr[0] as string[]);
            console.log(headers);
        }
    };

    const {toast} = useToast()

    function AgentStepsArea() {
        useEffect(() => {
            setTimeout(async () =>  {
                let input = await getTasksByUser(email || "default@email.com");
                console.log(input)
                if(input) {
                    setData(input)
                }
            }, 50000)
        })


        return (
            <ScrollArea className="h-full w-full">
                <div className="p-4">
                    <h4 className="mb-4 text-sm font-medium leading-none">Agents Actions History</h4>
                    {data.map((tag) => (
                        <div key={tag.step_id}>
                            <div className="flex items-center justify-between space-x-2 mb-2" key={tag.step_id + 1000}>
                                {tag.latest ? (
                                    <Button disabled className="w-2/3 bg-green-400">
                                        <Loader2 className="mr-2 h-4 w-4 animate-spin"/>
                                        Step {tag.explanation} is running...
                                    </Button>
                                ) : (
                                    <Button variant="outline" className="w-2/3"
                                            onClick={() => handleButtonClick(tag.step_id)}>
                                        Step {tag.explanation}
                                    </Button>
                                )}

                                <Dialog>
                                    <DialogTrigger asChild>
                                        <Button variant="secondary" className="w-1/3">More Info</Button>
                                    </DialogTrigger>
                                    <DialogContent className="sm:max-w-[700px] overflow-auto max-h-screen">
                                        <DialogHeader>
                                            <DialogTitle>{tag.explanation}</DialogTitle>
                                            <DialogDescription>
                                                {tag.explanation}
                                            </DialogDescription>
                                        </DialogHeader>
                                        <div className="grid gap-4 py-4">
                                            <div className="font-semibold">Executed code:</div>
                                            <CodeBlock
                                                language="python"
                                                value={tag.code}
                                            />
                                        </div>
                                        <DialogFooter className="">
                                            <div className="flex flex-row align justify-end space-x-2">
                                                <Button onClick={() => {
                                                    navigator.clipboard.writeText(tag.code)
                                                }

                                                }>
                                                    Copy Code
                                                </Button>
                                                <Button asChild type="submit">
                                                    <a href={tag.df_after_url} target="_blank" rel="noopener noreferrer"
                                                       download>
                                                        Download the Full Data Frame
                                                    </a>
                                                </Button>
                                            </div>
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
                    <div className="max-h-4 space-y-2 mt-10">
                        {
                            Array.from({length: queueData}, (_, index) => (
                                <Button
                                    disabled
                                    key={index}
                                    variant="outline"
                                    className="w-full bg-yellow-500 text-black"
                                    onClick={() => handleButtonClick(index + 1)}
                                >
                                    <ListStart className="mr-2 h-4 w-4"/>
                                    Backlog {index + 1}
                                </Button>
                            ))
                        }
                    </div>

                </div>
            </ScrollArea>
        )
    }

    const downloadAndParseCSV = async (url: any): Promise<any> => {
        try {
            const response = await fetch(url);
            const csvData = await response.text();
            const parsed = Papa.parse(csvData, {header: true, dynamicTyping: true,})
            console.log(parsed.data[0]);
            console.log(parsed.meta.delimiter);
            let result = parsed.data.slice(0, 7);
            return result
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
            <div className="flex flex-col lg:flex-row flex-grow h-screen w-screen">
                <div className="lg:w-7/12 bg-transparent p-4 border border-white rounded-sm m-4">
                    <ScrollArea className="h-full w-full">
                        {df && (
                            <Table>
                                <TableHeader>
                                    <TableRow>
                                        {df && Object.keys(df[0]).map((key, index) => (
                                            <TableHead key={index}>{key}</TableHead>
                                        ))}
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {df && df.map((row: { [key: string]: any }, index: number) => (
                                        <TableRow key={index}>
                                            {Object.values(row).map((value, index) => (
                                                <TableCell key={index}>{value}</TableCell>
                                            ))}
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        )}
                    </ScrollArea>
                </div>
                <div className="lg:w-5/12 flex flex-col">
                    <div
                        className="bg-transparent h-1/2 p-4 border border-white rounded-sm sm:mt-0 lg:mt-4 m-4 lg:ml-0 lg:mb-2 overflow-auto">
                        <AgentStepsArea/>
                    </div>
                    <div
                        className="bg-transparent h-1/2 p-4 border border-white rounded-sm sm:mt-0 m-4 lg:ml-0 lg:mt-2">
                        <ScrollArea className="h-full w-full p-4">
                            <div className="flex flex-col w-full gap-2">
                                <h4 className="mb-1 text-sm font-medium leading-none">Provide further instructions to
                                    the agents.</h4>
                                <h4 className="mb-4 text-sm font-medium leading-none text-red-600">Bidirectional
                                    communication with agents is still under development.</h4>
                                <Textarea placeholder="Type your message here." className="flex-grow mb-2"/>
                                <Button onClick={handleQueueDataButtonClick}>Send message</Button>
                            </div>
                        </ScrollArea>
                    </div>
                </div>
            </div>
        </div>
    )
}