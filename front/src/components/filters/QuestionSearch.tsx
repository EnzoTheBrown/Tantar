
import React from 'react';
import { Input } from '../ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';

interface QuestionSearchProps {
  question: string;
  k: number;
  setQuestion: (value: string) => void;
  setK: (value: number) => void;
}

export const QuestionSearch: React.FC<QuestionSearchProps> = ({
  question,
  k,
  setQuestion,
  setK,
}) => {
  return (
    <div className="space-y-3">
      <label className="text-sm font-medium">Recherche par question</label>
      <div className="flex items-center space-x-2">
        <Input
          placeholder="Posez une question sur les événements..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />
        <Select value={k.toString()} onValueChange={(value) => setK(parseInt(value))}>
          <SelectTrigger className="w-24">
            <SelectValue placeholder="Top K" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="5">Top 5</SelectItem>
            <SelectItem value="10">Top 10</SelectItem>
            <SelectItem value="20">Top 20</SelectItem>
            <SelectItem value="50">Top 50</SelectItem>
          </SelectContent>
        </Select>
      </div>
    </div>
  );
};
