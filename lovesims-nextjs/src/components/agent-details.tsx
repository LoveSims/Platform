'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { ScrollArea } from './ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';

interface AgentDetailsProps {
  agentName: string;
}

interface AgentData {
  profile: string;
  memories: string[];
  error?: string;
}

export function AgentDetails({ agentName }: AgentDetailsProps) {
  const [data, setData] = useState<AgentData>({ profile: '', memories: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAgentDetails = async () => {
      setLoading(true);
      try {
        const response = await fetch(`http://127.0.0.1:5000/agent/${agentName}`);
        const jsonData = await response.json();
        setData(jsonData);
      } catch (error) {
        console.error('Error fetching agent details:', error);
        setData({ profile: 'Failed to load agent details', memories: [] });
      } finally {
        setLoading(false);
      }
    };

    if (agentName) {
      fetchAgentDetails();
    }
  }, [agentName]);

  // Process the profile text into sections
  const processProfile = (text: string) => {
    const lines = text.split('\n').filter(line => line.trim());
    const sections: { [key: string]: string[] } = {
      'Basic Info': [],
      'Personality': [],
      'Background': [],
      'Other': []
    };
    
    let currentSection = 'Basic Info';
    
    for (const line of lines) {
      if (line.toLowerCase().includes('personality') || line.toLowerCase().includes('characteristics')) {
        currentSection = 'Personality';
        continue;
      }
      if (line.toLowerCase().includes('background') || line.toLowerCase().includes('history')) {
        currentSection = 'Background';
        continue;
      }
      sections[currentSection].push(line);
    }

    return sections;
  };

  const profileSections = processProfile(data.profile);

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>{agentName}</CardTitle>
        <CardDescription>Agent Profile & Memories</CardDescription>
      </CardHeader>
      <CardContent>
        {loading ? (
          <p>Loading agent details...</p>
        ) : (
          <Tabs defaultValue="profile" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="profile">Profile</TabsTrigger>
              <TabsTrigger value="memories">Memories</TabsTrigger>
            </TabsList>
            <TabsContent value="profile">
              <ScrollArea className="h-[400px] w-full rounded-md border p-4">
                <div className="space-y-6">
                  {Object.entries(profileSections).map(([section, lines]) => (
                    lines.length > 0 && (
                      <div key={section} className="space-y-2">
                        <h3 className="font-semibold text-lg">{section}</h3>
                        {lines.map((line, i) => (
                          <p key={i} className="text-sm text-muted-foreground">
                            {line}
                          </p>
                        ))}
                      </div>
                    )
                  ))}
                </div>
              </ScrollArea>
            </TabsContent>
            <TabsContent value="memories">
              <ScrollArea className="h-[400px] w-full rounded-md border p-4">
                <div className="space-y-4">
                  {data.memories.map((memory, index) => (
                    <div 
                      key={index} 
                      className="p-4 rounded-lg bg-muted hover:bg-muted/80 transition-colors"
                    >
                      <div className="flex items-start gap-3">
                        <span className="text-muted-foreground text-sm font-mono">
                          {String(index + 1).padStart(2, '0')}
                        </span>
                        <p className="text-sm leading-relaxed">
                          {memory}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </TabsContent>
          </Tabs>
        )}
      </CardContent>
    </Card>
  );
}
