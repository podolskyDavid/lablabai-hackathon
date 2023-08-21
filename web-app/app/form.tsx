'use client'

import React, {useState} from 'react';

import {useRouter} from "next/navigation";
import Link from "next/link";
import Image from "next/image";

import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from "@/components/ui/popover"
import {Input} from "@/components/ui/input"
import {Label} from "@/components/ui/label"
import {Textarea} from "@/components/ui/textarea"
import {Button} from "@/components/ui/button"


export default function Form() {
    const [email, setEmail] = useState('');
    const [file, setFile] = useState(null);
    const [description, setDescription] = useState('');
    const [taskId, setTaskId] = useState("")

    const handleFileChange = (event: any) => {
        if (event.target.files && event.target.files.length > 0) {
            setFile(event.target.files[0]);
        }
    };
    const router = useRouter();
    const submit = async (e: any) => {

        const formURL = e.target.action
        const data = new FormData()
        // @ts-ignore
        data.append('file', file);
        data.append('user_id', email);

        // POST the data to the URL of the form
        const res = await fetch(`https://agent-dnrxaaj6sq-lm.a.run.app/upload?user_id=${email}`, {
        // const res = await fetch(`http://0.0.0.0:80/upload?user_id=${email}`, {
            method: "POST",
            body: data,
            headers: {
                'accept': 'application/json',
            },
        })
        console.log(res)
        if(!res.ok) {
            throw new Error('Failed to fetch data')
        }
        const response = await res.json()
        const tid = response.task_id;
        console.log(tid)
        setTaskId(tid)
        const route = "./dashboard?email=" + email + "&taskid=" + tid;
        function func() {
            router.push(route)
        }
        func()
    }

    return (
        <form className="flex flex-col h-screen" action="./dashboard" method="post" onSubmit={submit}>
            <div className="pt-2 pb-2 m-4 mb-0 relative group">
                <div
                    className="absolute inset-0 bg-gradient-border z-0 group-hover:opacity-100 opacity-0 transition-opacity duration-500 rounded-md"></div>
                <div className="relative z-10 bg-transparent flex flex-row justify-between items-center">
                    <Link href="/">
                        <Image src="/logo-text-white.png" width={100} height={100}
                               alt="white logo"/>
                    </Link>
                    <Popover>
                        <PopoverTrigger asChild>
                            <Button className="mr-2" variant="outline">Dashboard</Button>
                        </PopoverTrigger>
                        <PopoverContent className="w-80">
                            <div className="grid gap-4">
                                <div className="space-y-2">
                                    <p className="text-sm text-muted-foreground">
                                        Type in your email to login
                                    </p>
                                </div>
                                <div className="grid gap-2">
                                    <div className="grid grid-cols-3 items-center gap-4">
                                        <Label htmlFor="width">Email</Label>
                                        <Input
                                            id="width"
                                            type="email"
                                            placeholder="guest@tidyai.tech"
                                            className="col-span-2 h-8"
                                            onChange={(e) => setEmail(e.target.value)}
                                        />
                                    </div>
                                </div>
                                <Button asChild className="">
                                    <Link href={"./dashboard?email=" + email}>
                                        Login
                                    </Link>
                                </Button>
                            </div>
                        </PopoverContent>
                    </Popover>
                </div>
            </div>
            <div className="flex flex-row pt-2 pb-2 m-4 mb-0 space-x-4">
                <div className="flex flex-col justify-center w-1/2 space-y-12 border-white border rounded-lg p-4">
                    <div className="space-y-2">
                        <h1 className="text-2xl">Enter your email:</h1>
                        <Input className="w-full" type="email" placeholder="Email"
                               onChange={(e) => setEmail(e.target.value)}/>
                    </div>

                    <div className="space-y-2">
                        <h1 className="text-2xl">Insert a data file to clean:</h1>
                        <input
                            className="block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400"
                            onChange={handleFileChange} aria-describedby="file_input_help" id="file_input" type="file"
                            accept=".csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel"/>
                        <p className="mt-1 text-sm text-gray-500 dark:text-gray-300" id="file_input_help">.csv, .xsl,
                            .xslx</p>
                    </div>

                </div>
                <div className="w-1/2  border-white border rounded-lg p-4 space-y-2">
                    <p className="text-2xl">Describe the data columns briefly:</p>
                    <Textarea className="w-full mb-4" placeholder="Type your message here."
                              onChange={(e) => setDescription(e.target.value)}/>
                </div>

            </div>
            <Button className="pt-2 pb-2 m-4 mb-0" asChild>
                <button>Submit</button>
            </Button>
        </form>
    );
};
