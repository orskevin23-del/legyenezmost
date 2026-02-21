import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { toast } from 'sonner';
import { Save, Key, User, LogOut, Eye, EyeOff } from 'lucide-react';

export default function Settings() {
  const { user, logout } = useAuth();
  const { t } = useLanguage();
  const [apiKeys, setApiKeys] = useState({
    openai: '',
    elevenlabs: '',
    elevenlabs_voice_id: '',
    pexels: ''
  });
  const [showKeys, setShowKeys] = useState({
    openai: false,
    elevenlabs: false,
    pexels: false
  });

  useEffect(() => {
    // Load from localStorage
    const saved = localStorage.getItem('api_keys');
    if (saved) {
      setApiKeys(JSON.parse(saved));
    }
  }, []);

  const handleSaveKeys = () => {
    localStorage.setItem('api_keys', JSON.stringify(apiKeys));
    toast.success(t('keys_saved'));
  };

  const toggleShowKey = (key) => {
    setShowKeys({ ...showKeys, [key]: !showKeys[key] });
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold text-white mb-2">
          {t('settings_title')}
        </h1>
        <p className="text-zinc-400">
          {t('settings_subtitle')}
        </p>
      </div>

      {/* Profile Card */}
      <Card className="bg-zinc-900/50 border-zinc-800">
        <CardHeader>
          <CardTitle className="text-white flex items-center">
            <User size={20} className="mr-2" />
            {t('profile')}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-4">
            <div className="w-20 h-20 bg-amber-400 rounded-full flex items-center justify-center text-zinc-950 text-3xl font-bold">
              {user?.name?.charAt(0).toUpperCase() || 'U'}
            </div>
            <div>
              <h3 className="text-xl font-semibold text-white">{user?.name}</h3>
              <p className="text-zinc-400">{user?.email}</p>
              <p className="text-xs text-zinc-500 mt-1">
                {t('created_at')}: {new Date(user?.created_at).toLocaleDateString('hu-HU')}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* API Keys */}
      <Card className="bg-zinc-900/50 border-zinc-800">
        <CardHeader>
          <CardTitle className="text-white flex items-center">
            <Key size={20} className="mr-2" />
            {t('api_keys')}
          </CardTitle>
          <p className="text-sm text-amber-400 mt-2">
            {t('api_keys_warning')}
          </p>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* OpenAI */}
          <div>
            <Label className="text-zinc-300">OpenAI API Key</Label>
            <div className="relative mt-1">
              <Input
                type={showKeys.openai ? 'text' : 'password'}
                value={apiKeys.openai}
                onChange={(e) => setApiKeys({ ...apiKeys, openai: e.target.value })}
                placeholder="sk-proj-..."
                className="bg-zinc-800 border-zinc-700 text-white pr-10"
              />
              <button
                onClick={() => toggleShowKey('openai')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-500 hover:text-white"
              >
                {showKeys.openai ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          {/* ElevenLabs */}
          <div>
            <Label className="text-zinc-300">ElevenLabs API Key</Label>
            <div className="relative mt-1">
              <Input
                type={showKeys.elevenlabs ? 'text' : 'password'}
                value={apiKeys.elevenlabs}
                onChange={(e) => setApiKeys({ ...apiKeys, elevenlabs: e.target.value })}
                placeholder="sk_..."
                className="bg-zinc-800 border-zinc-700 text-white pr-10"
              />
              <button
                onClick={() => toggleShowKey('elevenlabs')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-500 hover:text-white"
              >
                {showKeys.elevenlabs ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          {/* ElevenLabs Voice ID */}
          <div>
            <Label className="text-zinc-300">ElevenLabs Voice ID</Label>
            <Input
              type="text"
              value={apiKeys.elevenlabs_voice_id}
              onChange={(e) => setApiKeys({ ...apiKeys, elevenlabs_voice_id: e.target.value })}
              placeholder="CBPNfSFlxFnoBab9ZbDZ"
              className="bg-zinc-800 border-zinc-700 text-white mt-1"
            />
          </div>

          {/* Pexels */}
          <div>
            <Label className="text-zinc-300">Pexels API Key</Label>
            <div className="relative mt-1">
              <Input
                type={showKeys.pexels ? 'text' : 'password'}
                value={apiKeys.pexels}
                onChange={(e) => setApiKeys({ ...apiKeys, pexels: e.target.value })}
                placeholder="..."
                className="bg-zinc-800 border-zinc-700 text-white pr-10"
              />
              <button
                onClick={() => toggleShowKey('pexels')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-500 hover:text-white"
              >
                {showKeys.pexels ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          <Button
            onClick={handleSaveKeys}
            className="w-full bg-amber-400 hover:bg-amber-500 text-zinc-950 font-semibold"
          >
            <Save size={16} className="mr-2" />
            {t('save_keys')}
          </Button>

          <p className="text-xs text-zinc-500 text-center">
            A backend a .env fájlból tölti be a kulcsokat. Ez csak referencia céljára.
          </p>
        </CardContent>
      </Card>

      {/* Logout */}
      <Card className="bg-red-400/5 border-red-400/20">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-white mb-1">{t('logout')}</h3>
              <p className="text-sm text-zinc-400">
                {t('logout_subtitle')}
              </p>
            </div>
            <Button
              onClick={() => {
                logout();
                toast.success(t('logout_success'));
              }}
              variant="destructive"
              className="bg-red-500 hover:bg-red-600"
            >
              <LogOut size={16} className="mr-2" />
              {t('logout')}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
