'use client';

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import Link from "next/link"

export default function Home() {
  return (
    <main className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="space-y-8">
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold tracking-tight">LoveSims Dating Simulator</h1>
          <p className="text-xl text-muted-foreground">
            Explore dating scenarios with AI-powered agents
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>What is LoveSims?</CardTitle>
              <CardDescription>
                A unique platform for simulating dating interactions
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">
                LoveSims lets you explore different dating scenarios using AI agents. 
                Whether you want to practice your dating skills, understand different 
                personalities, or just have fun, our agents can help simulate realistic 
                dating interactions.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>How it Works</CardTitle>
              <CardDescription>
                Three ways to simulate dating scenarios
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="list-disc list-inside space-y-2 text-muted-foreground">
                <li>One-to-One: Direct conversation between two agents</li>
                <li>One-to-All: One agent interacts with all other agents</li>
                <li>All Pairs: Simulate dates between all possible agent pairs</li>
              </ul>
            </CardContent>
          </Card>
        </div>

        <Card className="mt-8">
          <CardHeader>
            <CardTitle>Ready to Start?</CardTitle>
            <CardDescription>
              Choose your preferred simulation mode and begin exploring dating scenarios
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-muted-foreground">
              Our AI agents represent different personalities and dating styles. 
              You can set up specific dating contexts, observe interactions, and 
              learn from various scenarios.
            </p>
          </CardContent>
          <CardFooter>
            <Link href="/simulation" className="w-full">
              <Button className="w-full" size="lg">
                Start Simulation
              </Button>
            </Link>
          </CardFooter>
        </Card>
      </div>
    </main>
  )
}
