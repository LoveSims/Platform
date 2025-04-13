import { useEffect, useRef } from 'react';
import { Card } from './ui/card';
import { ScrollArea } from './ui/scroll-area';

interface Message {
  agent: string;
  response: string;
  number: number;
}

interface ChatWindowProps {
  messages: Message[];
  className?: string;
}

export function ChatWindow({ messages, className = '' }: ChatWindowProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Scroll to bottom whenever messages change
    if (scrollRef.current) {
      const scrollElement = scrollRef.current;
      // Use requestAnimationFrame to ensure DOM has updated
      requestAnimationFrame(() => {
        scrollElement.scrollTo({
          top: scrollElement.scrollHeight,
          behavior: 'smooth'
        });
      });
    }
  }, [messages]);

  return (
    <Card className={`h-[600px] ${className}`}>
      <ScrollArea ref={scrollRef} className="h-full p-4">
        <div className="space-y-4">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex flex-col ${
                message.number === 0
                  ? 'mx-auto text-center font-semibold max-w-[80%]'
                  : 'ml-4 max-w-[80%]'
              }`}
            >
              {message.number !== 0 && (
                <span className="text-sm font-medium text-muted-foreground">
                  {message.agent}
                </span>
              )}
              <div
                className={`rounded-lg p-3 ${
                  message.number === 0
                    ? 'bg-muted'
                    : message.number % 2 === 1
                    ? 'bg-[#E6F3FF] text-gray-800' // Light blue
                    : 'bg-[#FFE6F0] text-gray-800' // Light pink
                }`}
              >
                {message.number === 0
                  ? message.response
                  : message.response.split(': ')[1]}
              </div>
            </div>
          ))}
        </div>
      </ScrollArea>
    </Card>
  );
}
