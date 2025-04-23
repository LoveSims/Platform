'use client';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { ChatWindow } from '@/components/chat-window';
import { EvaluationOptions } from '@/components/evaluation-options';
import { agentList } from '@/lib/constants';
import { useState, useEffect } from 'react';
import {
  startDates,
  createEventSource,
  runDates,
  resetGame,
  runEvaluation,
  type EvaluationType,
  type EvaluationResult,
} from '@/lib/api';
import { useParams } from 'next/navigation';

const DURATION_OPTIONS = [
  { value: '6', label: '6 responses' },
  { value: '10', label: '10 responses' },
  { value: '16', label: '16 responses' },
] as const;

type DurationOptionValue = typeof DURATION_OPTIONS[number]['value'];

type AllowedMode = 'one-to-one' | 'one-to-all';

export default function SimulationModePage() {
  /* --------------------------------------------------
   * Route & sanity‑check
   * -------------------------------------------------- */
  const params = useParams();
  const mode = params.mode as string;
  const allowedModes: readonly AllowedMode[] = ['one-to-one', 'one-to-all'];
  if (!allowedModes.includes(mode as AllowedMode)) {
    return (
      <main className="min-h-screen flex items-center justify-center">
        <p className="text-red-600 text-lg font-semibold">Unsupported mode.</p>
      </main>
    );
  }

  /* --------------------------------------------------
   * State
   * -------------------------------------------------- */
  const [selectedAgents, setSelectedAgents] = useState<string[]>([]);
  const [dateContext, setDateContext] = useState('coffee chat');
  const [duration, setDuration] = useState<DurationOptionValue>('6');
  const [messages, setMessages] = useState<any[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [simulationComplete, setSimulationComplete] = useState(false);
  const [evaluationResults, setEvaluationResults] = useState<EvaluationResult[]>([]);
  const [isEvaluating, setIsEvaluating] = useState(false);

  const modeTitles: Record<AllowedMode, string> = {
    'one-to-one': 'One‑to‑One Simulation',
    'one-to-all': 'One‑to‑All Simulation',
  };

  const showEvaluation = mode === 'one-to-one';

  /* --------------------------------------------------
   * Cleanup on unmount
   * -------------------------------------------------- */
  useEffect(() => {
    return () => {
      resetGame();
    };
  }, []);

  /* --------------------------------------------------
   * Handlers
   * -------------------------------------------------- */
  const handleStartSimulation = async () => {
    try {
      setMessages([]);
      setIsRunning(true);
      setSimulationComplete(false);
      setEvaluationResults([]);

      // 1. initialise
      await startDates({
        mode,
        agents: selectedAgents,
        dateContext, // always sent now
        dateDuration: parseInt(duration, 10),
      });

      // 2. stream responses
      const eventSource = createEventSource();
      eventSource.onmessage = (evt) => {
        const data = JSON.parse(evt.data);
        setMessages((prev) => [...prev, data]);
      };
      eventSource.onerror = (err) => {
        console.error('EventSource failed:', err);
        eventSource.close();
        setIsRunning(false);
      };

      // 3. kick off dates
      const res = await runDates();
      if (res.status === 'completed') {
        setTimeout(() => {
          eventSource.close();
          setIsRunning(false);
          setSimulationComplete(true);
        }, 1_000);
      }
    } catch (e) {
      console.error('Error running simulation:', e);
      setIsRunning(false);
    }
  };

  const handleEvaluation = async (type: EvaluationType) => {
    try {
      setIsEvaluating(true);
      const results = await runEvaluation({
        type,
        mode,
        agents: selectedAgents,
        transcript: messages,
      });
      setEvaluationResults(results);
    } catch (e) {
      console.error('Error running evaluation:', e);
    } finally {
      setIsEvaluating(false);
    }
  };

  /* --------------------------------------------------
   * Render
   * -------------------------------------------------- */
  return (
    <main className="container mx-auto px-4 py-8 max-w-6xl" suppressHydrationWarning>
      <div className="space-y-8">
        {/* ----- header ----- */}
        <div className="flex items-center gap-4">
          <Link href="/simulation">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <h1 className="text-3xl font-bold tracking-tight">{modeTitles[mode as AllowedMode]}</h1>
        </div>

        {/* ----- main section ----- */}
        <div className="grid gap-6 md:grid-cols-[350px_1fr]">
          {/* settings card */}
          <Card>
            <CardHeader>
              <CardTitle>Simulation Settings</CardTitle>
              <CardDescription>Configure your dating simulation</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {mode === 'one-to-one' && (
                <>
                  <div className="space-y-2">
                    <Label>First Agent</Label>
                    <Select
                      value={selectedAgents[0]}
                      onValueChange={(val) => setSelectedAgents([val, selectedAgents[1] || ''])}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select first agent" />
                      </SelectTrigger>
                      <SelectContent>
                        {agentList.map((agent) => (
                          <SelectItem key={agent} value={agent}>
                            {agent}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Second Agent</Label>
                    <Select
                      value={selectedAgents[1]}
                      onValueChange={(val) => setSelectedAgents([selectedAgents[0] || '', val])}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select second agent" />
                      </SelectTrigger>
                      <SelectContent>
                        {agentList.map((agent) => (
                          <SelectItem key={agent} value={agent}>
                            {agent}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </>
              )}

              {mode === 'one-to-all' && (
                <div className="space-y-2">
                  <Label>Select Agent</Label>
                  <Select value={selectedAgents[0]} onValueChange={(val) => setSelectedAgents([val])}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select an agent" />
                    </SelectTrigger>
                    <SelectContent>
                      {agentList.map((agent) => (
                        <SelectItem key={agent} value={agent}>
                          {agent}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}

              {/* date context (always visible now) */}
              <div className="space-y-2">
                <Label>Date Context</Label>
                <Textarea
                  value={dateContext}
                  onChange={(e) => setDateContext(e.target.value)}
                  placeholder="Describe the date context..."
                  rows={3}
                />
              </div>

              {/* duration */}
              <div className="space-y-2">
                <Label>Responses per Date</Label>
                <Select value={duration} onValueChange={setDuration as any}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {DURATION_OPTIONS.map(({ value, label }) => (
                      <SelectItem key={value} value={value}>
                        {label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
            <CardFooter>
              <Button
                className="w-full"
                onClick={handleStartSimulation}
                disabled={
                  isRunning ||
                  (mode === 'one-to-one' && (!selectedAgents[0] || !selectedAgents[1])) ||
                  (mode === 'one-to-all' && !selectedAgents[0]) ||
                  !dateContext
                }
              >
                {isRunning ? 'Running Simulation...' : 'Start Simulation'}
              </Button>
            </CardFooter>
          </Card>

          {/* live chat */}
          <ChatWindow messages={messages} />
        </div>

        {/* ----- evaluation ----- */}
        {simulationComplete && showEvaluation && (
          <div className="space-y-6">
            <div className="grid gap-6 md:grid-cols-[350px_1fr]">
              <EvaluationOptions mode={mode} onSelect={handleEvaluation} disabled={isEvaluating} />
              {evaluationResults.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>Evaluation Results</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {evaluationResults.map((result, idx) => (
                      <div key={idx} className="space-y-2">
                        <h3 className="font-semibold capitalize">
                          {result.type === 'self-reflection'
                            ? `${result.agent}'s Self‑Reflection Analysis`
                            : `${result.type} Analysis`}
                        </h3>
                        {result.analysis && (
                          <p className="text-sm mt-2">
                            <span className="font-medium">Analysis:</span> {result.analysis}
                          </p>
                        )}
                        {result.decision && (
                          <p className="text-sm mt-2 font-semibold">
                            {result.type === 'self-reflection'
                              ? `Would ${result.agent} see them again?`
                              : 'Should they see each other again?'}{' '}
                            <span
                              className={
                                result.decision.toLowerCase() === 'yes'
                                  ? 'text-green-600'
                                  : 'text-red-600'
                              }
                            >
                              {result.decision}
                            </span>
                          </p>
                        )}
                        {result.compatibilityScore !== undefined && (
                          <p className="text-sm">Compatibility Score: {result.compatibilityScore}/100</p>
                        )}
                        {result.satisfactionScore !== undefined && (
                          <p className="text-sm">Satisfaction Score: {result.satisfactionScore}/100</p>
                        )}
                        {result.lengthFeedback && <p className="text-sm">Length Feedback: {result.lengthFeedback}</p>}
                        {/* attribute ratings */}
                        {'attributeRatings' in result && result.attributeRatings && (
                          <div className="text-sm">
                            <p className="font-medium">Attribute Ratings:</p>
                            <ul className="list-disc list-inside">
                              {Object.entries(result.attributeRatings).map(([attr, score]) => (
                                <li key={attr}>
                                  {attr}: {score as number}/100
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {/* attribute similarity */}
                        {'attributeSimilarity' in result && result.attributeSimilarity && (
                          <div className="text-sm">
                            <p className="font-medium">Attribute Similarity:</p>
                            <ul className="list-disc list-inside">
                              {Object.entries(result.attributeSimilarity).map(([attr, score]) => (
                                <li key={attr}>
                                  {attr}: {score as number}/100
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {/* key factors */}
                        {result.keyFactors && (
                          <div className="text-sm">
                            <p className="font-medium">Key Factors:</p>
                            <ul className="list-disc list-inside">
                              {result.keyFactors.map((factor, i) => (
                                <li key={i}>{factor}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    ))}
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}