import React from 'react';

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

const tags = Array.from({ length: 15 }).map(
    (_, i, a) => `v1.2.0-beta.${a.length - i}`
)

export function AgentStepsArea() {
    return (
        <ScrollArea className="h-full w-full">
            <div className="p-4">
                <h4 className="mb-4 text-sm font-medium leading-none">Agent Actions History</h4>
                {tags.map((tag) => (
                    <div className="flex items-center justify-between mb-2" key={tag}>
                        <Button variant="outline" className="w-full">{tag}</Button>
                    </div>
                ))}
            </div>
        </ScrollArea>
    )
}

const invoices = [
    {
        invoice: "INV001",
        paymentStatus: "Paid",
        totalAmount: "$250.00",
        paymentMethod: "Credit Card",
    },
    {
        invoice: "INV002",
        paymentStatus: "Pending",
        totalAmount: "$150.00",
        paymentMethod: "PayPal",
    },
    {
        invoice: "INV003",
        paymentStatus: "Unpaid",
        totalAmount: "$350.00",
        paymentMethod: "Bank Transfer",
    },
    {
        invoice: "INV004",
        paymentStatus: "Paid",
        totalAmount: "$450.00",
        paymentMethod: "Credit Card",
    },
    {
        invoice: "INV005",
        paymentStatus: "Paid",
        totalAmount: "$550.00",
        paymentMethod: "PayPal",
    },
    {
        invoice: "INV006",
        paymentStatus: "Pending",
        totalAmount: "$200.00",
        paymentMethod: "Bank Transfer",
    },
    {
        invoice: "INV007",
        paymentStatus: "Unpaid",
        totalAmount: "$300.00",
        paymentMethod: "Credit Card",
    },
]


export default function Dashboard() {
    return (
        <div className="flex flex-col lg:flex-row h-screen">
            <div className="lg:w-7/12 bg-transparent p-4 border border-white rounded-sm m-4">
                <Table>
                    <TableCaption>A list of your recent invoices.</TableCaption>
                    <TableHeader>
                        <TableRow>
                            <TableHead className="w-[100px]">Invoice</TableHead>
                            <TableHead>Status</TableHead>
                            <TableHead>Method</TableHead>
                            <TableHead className="text-right">Amount</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {invoices.map((invoice) => (
                            <TableRow key={invoice.invoice}>
                                <TableCell className="font-medium">{invoice.invoice}</TableCell>
                                <TableCell>{invoice.paymentStatus}</TableCell>
                                <TableCell>{invoice.paymentMethod}</TableCell>
                                <TableCell className="text-right">{invoice.totalAmount}</TableCell>
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