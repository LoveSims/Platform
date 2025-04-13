'use client';

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { ArrowLeft, Users, User, UsersRound } from "lucide-react"
import Link from "next/link"
import { useState } from "react"
import { agentList } from "@/lib/constants"
import { AgentDetails } from "@/components/agent-details"
import { ScrollArea } from "@/components/ui/scroll-area"

export default function SimulationPage() {
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto max-w-5xl px-4 py-8">
        <div className="flex items-center mb-8">
          <Link href="/">
            <Button variant="ghost" className="mr-2">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back
            </Button>
          </Link>
          <h1 className="text-2xl font-bold">Choose Simulation Mode</h1>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <Link href="/simulation/one-to-one">
            <Card className="hover:bg-accent cursor-pointer">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <User className="mr-2" />
                  One-to-One
                </CardTitle>
                <CardDescription>
                  Simulate a date between two specific agents
                </CardDescription>
              </CardHeader>
            </Card>
          </Link>

          <Link href="/simulation/one-to-all">
            <Card className="hover:bg-accent cursor-pointer">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <UsersRound className="mr-2" />
                  One-to-All
                </CardTitle>
                <CardDescription>
                  One agent dates all other agents
                </CardDescription>
              </CardHeader>
            </Card>
          </Link>

          <Link href="/simulation/all-pairs">
            <Card className="hover:bg-accent cursor-pointer">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Users className="mr-2" />
                  All Pairs
                </CardTitle>
                <CardDescription>
                  Simulate dates between all possible pairs
                </CardDescription>
              </CardHeader>
            </Card>
          </Link>
        </div>

        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Available Agents</CardTitle>
            <CardDescription>Click on an agent to view their details</CardDescription>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[200px] rounded-md border p-4">
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2">
                {agentList.map((agent) => (
                  <Button
                    key={agent}
                    variant={selectedAgent === agent ? "default" : "outline"}
                    onClick={() => setSelectedAgent(agent)}
                    className="w-full"
                  >
                    {agent}
                  </Button>
                ))}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>

        {selectedAgent && (
          <AgentDetails agentName={selectedAgent} />
        )}
      </div>
    </div>
  );
}
