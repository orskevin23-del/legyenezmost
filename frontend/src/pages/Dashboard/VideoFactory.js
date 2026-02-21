import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Textarea } from '../../components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../../components/ui/select';
import { Slider } from '../../components/ui/slider';
import { toast } from 'sonner';
import {
  Play,
  Film,
  Wand2,
  Download,
  Clock,
  CheckCircle,
  XCircle,
  Loader2,
  Music,
  Image as ImageIcon,
  Mic,
  Edit,
  Save,
  X
} from 'lucide-react';

export default function VideoFactory() {
  const { api } = useAuth();
  const [scripts, setScripts] = useState([]);
  const [videos, setVideos] = useState([]);
  const [selectedScript, setSelectedScript] = useState('');
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  // Script Editing State
  const [isEditingScript, setIsEditingScript] = useState(false);
  const [editedScriptText, setEditedScriptText] = useState('');

  // Voice Settings
  const [voiceOption, setVoiceOption] = useState('default'); // 'default' or 'custom'
  const [voiceId, setVoiceId] = useState('BsX9EcVskRzn0UFZ9dmh'); // Default voice
  const [customVoiceId, setCustomVoiceId] = useState('');
  const [voiceSettings, setVoiceSettings] = useState({
    stability: 0.7,
    similarity_boost: 0.75,
    style: 0.5,
    speed: 1.0,
    use_speaker_boost: true
  });

  // Popular ElevenLabs voices
  const popularVoices = [
    { id: 'BsX9EcVskRzn0UFZ9dmh', name: 'Alapértelmezett (Saját hang)', language: 'Multilingual' },
    { id: '21m00Tcm4TlvDq8ikWAM', name: 'Rachel (Female)', language: 'English' },
    { id: 'pNInz6obpgDQGcFmaJgB', name: 'Adam (Male)', language: 'English' },
    { id: 'EXAVITQu4vr4xnSDxMaL', name: 'Bella (Female)', language: 'English' },
    { id: 'ErXwobaYiN019PkySvjV', name: 'Antoni (Male)', language: 'English' },
    { id: 'VR6AewLTigWG4xSOukaG', name: 'Arnold (Male)', language: 'English' },
  ];

  // Video Settings
  const [brollSearch, setBrollSearch] = useState('');
  const [backgroundMusic, setBackgroundMusic] = useState('');

  useEffect(() => {
    fetchData();
    loadVoicePreferences();
    const interval = setInterval(fetchVideos, 10000); // Poll every 10s
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      await Promise.all([fetchScripts(), fetchVideos()]);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchScripts = async () => {
    try {
      const response = await api.get('/scripts?limit=50');
      setScripts(response.data);
    } catch (error) {
      console.error('Failed to fetch scripts:', error);
    }
  };

  const fetchVideos = async () => {
    try {
      const response = await api.get('/videos?limit=20');
      setVideos(response.data);
    } catch (error) {
      console.error('Failed to fetch videos:', error);
    }
  };

  // Load saved voice preferences
  const loadVoicePreferences = async () => {
    try {
      const response = await api.get('/voice-preferences');
      if (response.data) {
        const pref = response.data;
        setCustomVoiceId(pref.voice_id);
        setVoiceId(pref.voice_id);
        setVoiceSettings(pref.voice_settings);
        setVoiceOption('custom'); // Auto-select custom if we have saved preferences
        toast.success('Betöltöttem a mentett hang beállításokat!');
      }
    } catch (error) {
      console.log('No saved voice preferences found');
    }
  };

  // Save voice preferences
  const saveVoicePreferences = async () => {
    try {
      const finalVoiceId = voiceOption === 'custom' ? customVoiceId : voiceId;
      
      await api.post('/voice-preferences', {
        voice_id: finalVoiceId,
        voice_settings: voiceSettings,
        is_default: true
      });

      toast.success('Hang beállítások elmentve! Legközelebb automatikusan betöltődnek.');
    } catch (error) {
      toast.error('Hiba a mentés során: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleDownload = async (videoId) => {
    try {
      toast.info('Letöltés indul...');
      
      const response = await api.get(`/videos/${videoId}/download`, {
        responseType: 'blob'
      });
      
      // Create blob URL and trigger download
      const blob = new Blob([response.data], { type: 'video/mp4' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `legyenez_${videoId.slice(0, 8)}.mp4`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      toast.success('Letöltés sikeres!');
    } catch (error) {
      console.error('Download failed:', error);
      toast.error('Letöltés sikertelen: ' + (error.response?.data?.detail || error.message));
    }
  };

  // Start editing script
  const startEditingScript = () => {
    const scriptData = scripts.find(s => s.id === selectedScript);
    if (scriptData) {
      setEditedScriptText(scriptData.script);
      setIsEditingScript(true);
    }
  };

  // Cancel editing
  const cancelEditingScript = () => {
    setIsEditingScript(false);
    setEditedScriptText('');
  };

  // Save edited script
  const saveEditedScript = async () => {
    try {
      await api.put(`/scripts/${selectedScript}`, {
        script: editedScriptText
      });

      // Update local state
      setScripts(scripts.map(s => 
        s.id === selectedScript 
          ? { ...s, script: editedScriptText, character_count: editedScriptText.length }
          : s
      ));

      setIsEditingScript(false);
      toast.success('Script sikeresen frissítve!');
    } catch (error) {
      toast.error('Hiba a mentés során: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleGenerateVideo = async () => {
    if (!selectedScript) {
      toast.error('Válassz ki egy scriptet!');
      return;
    }

    // Determine final voice ID
    const finalVoiceId = voiceOption === 'custom' ? customVoiceId : voiceId;

    if (!finalVoiceId) {
      toast.error('Válassz voice-t vagy adj meg custom Voice ID-t!');
      return;
    }

    setGenerating(true);

    try {
      await api.post('/videos/generate', {
        script_id: selectedScript,
        voice_id: finalVoiceId,
        voice_settings: voiceSettings,
        background_music: backgroundMusic || null,
        b_roll_search: brollSearch || null
      });

      toast.success('Videó generálás elindult! Ez eltarthat néhány percig...');
      
      // Refresh videos list
      setTimeout(() => {
        fetchVideos();
      }, 2000);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Videó generálás sikertelen');
    } finally {
      setGenerating(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'queued':
        return <Clock className="text-yellow-400" size={20} />;
      case 'processing':
        return <Loader2 className="text-blue-400 animate-spin" size={20} />;
      case 'completed':
        return <CheckCircle className="text-green-400" size={20} />;
      case 'failed':
        return <XCircle className="text-red-400" size={20} />;
      default:
        return <Clock className="text-zinc-500" size={20} />;
    }
  };

  const getStatusBadge = (status) => {
    const colors = {
      queued: 'bg-yellow-400/10 text-yellow-400 border-yellow-400/20',
      processing: 'bg-blue-400/10 text-blue-400 border-blue-400/20',
      completed: 'bg-green-400/10 text-green-400 border-green-400/20',
      failed: 'bg-red-400/10 text-red-400 border-red-400/20'
    };

    const labels = {
      queued: 'Sorban',
      processing: 'Generálás...',
      completed: 'Kész',
      failed: 'Hiba'
    };

    return (
      <Badge className={colors[status] || colors.queued}>
        {labels[status] || status}
      </Badge>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-amber-400 text-lg">Betöltés...</div>
      </div>
    );
  }

  const selectedScriptData = scripts.find(s => s.id === selectedScript);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold text-white mb-2">
          Videó Gyár
        </h1>
        <p className="text-zinc-400">
          AI-powered videó generálás: TTS + B-roll + karaoke feliratok
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Settings Panel */}
        <div className="lg:col-span-2 space-y-6">
          {/* Script Selection */}
          <Card className="bg-zinc-900/50 border-zinc-800">
            <CardHeader>
              <CardTitle className="text-white flex items-center justify-between">
                <div className="flex items-center">
                  <Film className="mr-2 text-amber-400" size={20} />
                  Script Kiválasztása
                </div>
                {selectedScriptData && !isEditingScript && (
                  <Button
                    onClick={startEditingScript}
                    variant="ghost"
                    size="sm"
                    className="text-amber-400 hover:text-amber-300"
                  >
                    <Edit size={16} className="mr-1" />
                    Szerkesztés
                  </Button>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label className="text-zinc-300">Válassz scriptet</Label>
                <Select value={selectedScript} onValueChange={setSelectedScript} disabled={isEditingScript}>
                  <SelectTrigger className="bg-zinc-800 border-zinc-700 text-white mt-1">
                    <SelectValue placeholder="Válassz egy scriptet..." />
                  </SelectTrigger>
                  <SelectContent className="bg-zinc-800 border-zinc-700 max-h-[300px]">
                    {scripts.map(script => (
                      <SelectItem key={script.id} value={script.id}>
                        {script.topic} ({script.character_count} kar.)
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {selectedScriptData && !isEditingScript && (
                <div className="p-4 bg-zinc-800/50 rounded-lg border border-zinc-700">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold text-white">{selectedScriptData.topic}</h4>
                    <Badge className="bg-amber-400/10 text-amber-400">
                      {selectedScriptData.character_count} karakter
                    </Badge>
                  </div>
                  <p className="text-sm text-zinc-400 font-mono leading-relaxed whitespace-pre-wrap">
                    {selectedScriptData.script}
                  </p>
                </div>
              )}

              {/* Script Editor */}
              {isEditingScript && (
                <div className="space-y-3">
                  <div>
                    <Label className="text-zinc-300 mb-2">Script szövege</Label>
                    <Textarea
                      value={editedScriptText}
                      onChange={(e) => setEditedScriptText(e.target.value)}
                      className="bg-zinc-800 border-zinc-700 text-white min-h-[200px] font-mono"
                      placeholder="Írd be a script szövegét..."
                    />
                    <p className="text-sm text-zinc-500 mt-1">
                      Karakterek: {editedScriptText.length}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      onClick={saveEditedScript}
                      className="bg-green-600 hover:bg-green-700"
                    >
                      <Save size={16} className="mr-1" />
                      Mentés
                    </Button>
                    <Button
                      onClick={cancelEditingScript}
                      variant="outline"
                      className="border-zinc-700"
                    >
                      <X size={16} className="mr-1" />
                      Mégse
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Voice Settings */}
          <Card className="bg-zinc-900/50 border-zinc-800">
            <CardHeader>
              <CardTitle className="text-white flex items-center justify-between">
                <div className="flex items-center">
                  <Mic className="mr-2 text-blue-400" size={20} />
                  Hang Beállítások (ElevenLabs)
                </div>
                <Button
                  onClick={saveVoicePreferences}
                  variant="ghost"
                  size="sm"
                  className="text-blue-400 hover:text-blue-300"
                >
                  <Save size={16} className="mr-1" />
                  Beállítások Mentése
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Voice Selection */}
              <div>
                <Label className="text-zinc-300">Voice Kiválasztás</Label>
                <div className="grid grid-cols-2 gap-2 mt-2">
                  <button
                    onClick={() => setVoiceOption('default')}
                    className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                      voiceOption === 'default'
                        ? 'bg-amber-400 text-zinc-950'
                        : 'bg-zinc-800 text-zinc-300 hover:bg-zinc-700'
                    }`}
                  >
                    Népszerű Voice-ok
                  </button>
                  <button
                    onClick={() => setVoiceOption('custom')}
                    className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                      voiceOption === 'custom'
                        ? 'bg-amber-400 text-zinc-950'
                        : 'bg-zinc-800 text-zinc-300 hover:bg-zinc-700'
                    }`}
                  >
                    Saját Voice ID
                  </button>
                </div>
              </div>

              {/* Popular Voices Dropdown */}
              {voiceOption === 'default' && (
                <div>
                  <Label className="text-zinc-300">Válassz Voice-t</Label>
                  <Select value={voiceId} onValueChange={setVoiceId}>
                    <SelectTrigger className="bg-zinc-800 border-zinc-700 text-white mt-1">
                      <SelectValue placeholder="Válassz hangot..." />
                    </SelectTrigger>
                    <SelectContent className="bg-zinc-800 border-zinc-700">
                      {popularVoices.map(voice => (
                        <SelectItem key={voice.id} value={voice.id}>
                          {voice.name} - {voice.language}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}

              {/* Custom Voice ID Input */}
              {voiceOption === 'custom' && (
                <div>
                  <Label className="text-zinc-300">Saját Voice ID (ElevenLabs)</Label>
                  <Input
                    type="text"
                    value={customVoiceId}
                    onChange={(e) => setCustomVoiceId(e.target.value)}
                    placeholder="Pl: BsX9EcVskRzn0UFZ9dmh"
                    className="bg-zinc-800 border-zinc-700 text-white mt-1"
                  />
                  <p className="text-xs text-zinc-500 mt-1">
                    Találd meg a Voice ID-t az ElevenLabs dashboard-on
                  </p>
                </div>
              )}

              {/* Voice Settings Sliders */}
              <div className="space-y-4 pt-2">
                <div>
                  <div className="flex justify-between mb-2">
                    <Label className="text-zinc-300">Stability</Label>
                    <span className="text-zinc-400 text-sm">{voiceSettings.stability.toFixed(2)}</span>
                  </div>
                  <Slider
                    value={[voiceSettings.stability]}
                    onValueChange={([value]) => setVoiceSettings({...voiceSettings, stability: value})}
                    min={0}
                    max={1}
                    step={0.05}
                    className="w-full"
                  />
                </div>

                <div>
                  <div className="flex justify-between mb-2">
                    <Label className="text-zinc-300">Similarity Boost</Label>
                    <span className="text-zinc-400 text-sm">{voiceSettings.similarity_boost.toFixed(2)}</span>
                  </div>
                  <Slider
                    value={[voiceSettings.similarity_boost]}
                    onValueChange={([value]) => setVoiceSettings({...voiceSettings, similarity_boost: value})}
                    min={0}
                    max={1}
                    step={0.05}
                    className="w-full"
                  />
                </div>

                <div>
                  <div className="flex justify-between mb-2">
                    <Label className="text-zinc-300">Style</Label>
                    <span className="text-zinc-400 text-sm">{voiceSettings.style.toFixed(2)}</span>
                  </div>
                  <Slider
                    value={[voiceSettings.style]}
                    onValueChange={([value]) => setVoiceSettings({...voiceSettings, style: value})}
                    min={0}
                    max={1}
                    step={0.05}
                    className="w-full"
                  />
                </div>

                <div>
                  <div className="flex justify-between mb-2">
                    <Label className="text-zinc-300">Speed (Sebesség)</Label>
                    <span className="text-zinc-400 text-sm">{voiceSettings.speed.toFixed(2)}x</span>
                  </div>
                  <Slider
                    value={[voiceSettings.speed]}
                    onValueChange={([value]) => setVoiceSettings({...voiceSettings, speed: value})}
                    min={0.25}
                    max={2.0}
                    step={0.05}
                    className="w-full"
                  />
                  <p className="text-xs text-zinc-500 mt-1">
                    0.25x (nagyon lassú) - 2.0x (nagyon gyors)
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* B-roll & Music Settings */}
          <Card className="bg-zinc-900/50 border-zinc-800">
            <CardHeader>
              <CardTitle className="text-white flex items-center">
                <ImageIcon className="mr-2 text-purple-400" size={20} />
                B-roll és Zene
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label className="text-zinc-300">B-roll Keresési Kulcsszó</Label>
                <Input
                  type="text"
                  value={brollSearch}
                  onChange={(e) => setBrollSearch(e.target.value)}
                  placeholder="Pl: faith prayer spiritual (opcionális)"
                  className="bg-zinc-800 border-zinc-700 text-white mt-1"
                />
              </div>

              <div>
                <Label className="text-zinc-300">Háttérzene URL (opcionális)</Label>
                <Input
                  type="text"
                  value={backgroundMusic}
                  onChange={(e) => setBackgroundMusic(e.target.value)}
                  placeholder="https://example.com/music.mp3"
                  className="bg-zinc-800 border-zinc-700 text-white mt-1"
                />
              </div>
            </CardContent>
          </Card>

          {/* Generate Button */}
          <Button
            onClick={handleGenerateVideo}
            disabled={generating || !selectedScript || isEditingScript}
            className="w-full bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-white font-semibold py-6 text-lg"
          >
            {generating ? (
              <>
                <Loader2 className="mr-2 animate-spin" size={20} />
                Generálás folyamatban...
              </>
            ) : (
              <>
                <Play className="mr-2" size={20} />
                Videó Generálás Indítása
              </>
            )}
          </Button>
        </div>

        {/* Generated Videos List */}
        <div className="space-y-4">
          <Card className="bg-zinc-900/50 border-zinc-800 sticky top-6">
            <CardHeader>
              <CardTitle className="text-white">Generált Videók</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 max-h-[800px] overflow-y-auto">
              {videos.length === 0 ? (
                <p className="text-zinc-500 text-center py-4">
                  Még nincs videó generálva
                </p>
              ) : (
                videos.map(video => (
                  <div
                    key={video.id}
                    className="p-3 bg-zinc-800/50 rounded-lg border border-zinc-700 space-y-2"
                  >
                    <div className="flex items-center justify-between">
                      {getStatusIcon(video.status)}
                      {getStatusBadge(video.status)}
                    </div>
                    
                    <div className="text-sm">
                      <p className="text-zinc-400 truncate">
                        ID: {video.id.slice(0, 8)}...
                      </p>
                      {video.duration && (
                        <p className="text-zinc-500 text-xs">
                          {video.duration.toFixed(1)}s
                        </p>
                      )}
                    </div>

                    {video.status === 'completed' && (
                      <Button
                        onClick={() => handleDownload(video.id)}
                        size="sm"
                        className="w-full bg-green-600 hover:bg-green-700"
                      >
                        <Download size={16} className="mr-1" />
                        Letöltés
                      </Button>
                    )}

                    {video.status === 'failed' && video.error && (
                      <p className="text-xs text-red-400 break-words">
                        {video.error}
                      </p>
                    )}
                  </div>
                ))
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
