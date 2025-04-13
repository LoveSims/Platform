import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { useState } from 'react';

export type EvaluationType = 'self-reflection' | 'transcript-based' | 'profiles-based' | 'all';

interface EvaluationOptionsProps {
  mode: string;
  onSelect: (type: EvaluationType) => void;
  disabled?: boolean;
}

export function EvaluationOptions({ mode, onSelect, disabled }: EvaluationOptionsProps) {
  // Only show self-reflection for one-to-one and one-to-all modes
  const showSelfReflection = mode === 'one-to-one' || mode === 'one-to-all';
  const [selectedType, setSelectedType] = useState<EvaluationType>('transcript-based');

  return (
    <Card>
      <CardHeader>
        <CardTitle>Run Evaluation</CardTitle>
        <CardDescription>Choose how to evaluate the simulation results</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <RadioGroup 
          value={selectedType} 
          onValueChange={(value) => setSelectedType(value as EvaluationType)} 
          className="space-y-4"
        >
          {showSelfReflection && (
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="self-reflection" id="self-reflection" />
              <Label htmlFor="self-reflection" className="font-medium">
                Self Reflection
                <p className="text-sm text-muted-foreground">
                  Agent reflects on the interaction using post-simulation questions
                </p>
              </Label>
            </div>
          )}
          <div className="flex items-center space-x-2">
            <RadioGroupItem value="transcript-based" id="transcript-based" />
            <Label htmlFor="transcript-based" className="font-medium">
              Third-Party (Transcript)
              <p className="text-sm text-muted-foreground">
                Analyze compatibility based on conversation transcript
              </p>
            </Label>
          </div>
          <div className="flex items-center space-x-2">
            <RadioGroupItem value="profiles-based" id="profiles-based" />
            <Label htmlFor="profiles-based" className="font-medium">
              Third-Party (Profiles)
              <p className="text-sm text-muted-foreground">
                Analyze compatibility based on agent profiles and memories
              </p>
            </Label>
          </div>
          <div className="flex items-center space-x-2">
            <RadioGroupItem value="all" id="all" />
            <Label htmlFor="all" className="font-medium">
              Run All Evaluations
              <p className="text-sm text-muted-foreground">
                Perform all applicable evaluation types
              </p>
            </Label>
          </div>
        </RadioGroup>
        <Button 
          className="w-full" 
          onClick={() => onSelect(selectedType)}
          disabled={disabled}
        >
          Run Evaluation
        </Button>
      </CardContent>
    </Card>
  );
}
