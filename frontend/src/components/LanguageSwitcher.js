import React from 'react';
import { useLanguage } from '../contexts/LanguageContext';
import { Globe } from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select';

const languages = [
  { code: 'hu', name: 'Magyar', flag: '🇭🇺' },
  { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
  { code: 'en', name: 'English', flag: '🇬🇧' },
  { code: 'pl', name: 'Polski', flag: '🇵🇱' },
  { code: 'nl', name: 'Nederlands', flag: '🇳🇱' },
];

export default function LanguageSwitcher() {
  const { language, setLanguage } = useLanguage();

  return (
    <div className="fixed top-4 right-4 z-50 flex items-center gap-2 bg-zinc-900/90 backdrop-blur-sm px-3 py-2 rounded-lg border border-zinc-700">
      <Globe size={18} className="text-amber-400" />
      <Select value={language} onValueChange={setLanguage}>
        <SelectTrigger className="w-[140px] bg-zinc-800 border-zinc-700 text-white">
          <SelectValue>
            {languages.find(l => l.code === language)?.flag} {languages.find(l => l.code === language)?.name}
          </SelectValue>
        </SelectTrigger>
        <SelectContent className="bg-zinc-800 border-zinc-700">
          {languages.map((lang) => (
            <SelectItem key={lang.code} value={lang.code} className="text-white hover:bg-zinc-700">
              <span className="flex items-center gap-2">
                <span>{lang.flag}</span>
                <span>{lang.name}</span>
              </span>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
