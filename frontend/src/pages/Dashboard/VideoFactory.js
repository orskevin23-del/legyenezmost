import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
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
  Mic
} from 'lucide-react';

export default function VideoFactory() {
  const { api } = useAuth();
  const [scripts, setScripts] = useState([]);
  const [videos, setVideos] = useState([]);
  const [selectedScript, setSelectedScript] = useState('');
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

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
              <CardTitle className="text-white flex items-center">
                <Film className="mr-2 text-amber-400" size={20} />
                Script Kiválasztása
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label className="text-zinc-300">Válassz scriptet</Label>
                <Select value={selectedScript} onValueChange={setSelectedScript}>
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

              {selectedScriptData && (
                <div className="p-4 bg-zinc-800/50 rounded-lg border border-zinc-700">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold text-white">{selectedScriptData.topic}</h4>
                    <Badge className="bg-amber-400/10 text-amber-400">
                      {selectedScriptData.character_count} karakter
                    </Badge>
                  </div>
                  <p className="text-sm text-zinc-400 font-mono leading-relaxed">
                    {selectedScriptData.script}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Voice Settings */}
          <Card className="bg-zinc-900/50 border-zinc-800">
            <CardHeader>
              <CardTitle className="text-white flex items-center">
                <Mic className="mr-2 text-blue-400" size={20} />
                Hang Beállítások (ElevenLabs)
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
                  <Label className="text-zinc-300">Custom Voice ID</Label>
                  <Input
                    placeholder="pl. CBPNfSFlxFnoBab9ZbDZ"
                    value={customVoiceId}
                    onChange={(e) => setCustomVoiceId(e.target.value)}
                    className="bg-zinc-800 border-zinc-700 text-white mt-1"
                  />
                  <p className="text-xs text-zinc-500 mt-1">
                    Add meg a saját ElevenLabs Voice ID-det
                  </p>
                </div>
              )}

              <div>
                <div className="flex items-center justify-between mb-2">
                  <Label className="text-zinc-300">Stability</Label>
                  <span className="text-sm text-amber-400">{voiceSettings.stability.toFixed(2)}</span>
                </div>
                <Slider
                  value={[voiceSettings.stability]}
                  onValueChange={([val]) => setVoiceSettings({ ...voiceSettings, stability: val })}
                  min={0}
                  max={1}
                  step={0.05}
                  className="w-full"
                />
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <Label className="text-zinc-300">Similarity Boost</Label>
                  <span className="text-sm text-amber-400">{voiceSettings.similarity_boost.toFixed(2)}</span>
                </div>
                <Slider
                  value={[voiceSettings.similarity_boost]}
                  onValueChange={([val]) => setVoiceSettings({ ...voiceSettings, similarity_boost: val })}
                  min={0}
                  max={1}
                  step={0.05}
                  className="w-full"
                />
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <Label className="text-zinc-300">Style</Label>
                  <span className="text-sm text-amber-400">{voiceSettings.style.toFixed(2)}</span>
                </div>
                <Slider
                  value={[voiceSettings.style]}
                  onValueChange={([val]) => setVoiceSettings({ ...voiceSettings, style: val })}
                  min={0}
                  max={1}
                  step={0.05}
                  className="w-full"
                />
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <Label className="text-zinc-300">Speed (Sebesség)</Label>
                  <span className="text-sm text-amber-400">{voiceSettings.speed.toFixed(2)}x</span>
                </div>
                <Slider
                  value={[voiceSettings.speed]}
                  onValueChange={([val]) => setVoiceSettings({ ...voiceSettings, speed: val })}
                  min={0.25}
                  max={4.0}
                  step={0.1}
                  className="w-full"
                />
                <p className="text-xs text-zinc-500 mt-1">
                  Hang sebessége (0.25x = lassú, 4.0x = gyors)
                </p>
              </div>

              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="speaker-boost"
                  checked={voiceSettings.use_speaker_boost}
                  onChange={(e) => setVoiceSettings({ ...voiceSettings, use_speaker_boost: e.target.checked })}
                  className="rounded"
                />
                <Label htmlFor="speaker-boost" className="text-zinc-300 cursor-pointer">
                  Speaker Boost (ajánlott)
                </Label>
              </div>
            </CardContent>
          </Card>

          {/* Video Settings */}
          <Card className="bg-zinc-900/50 border-zinc-800">
            <CardHeader>
              <CardTitle className="text-white flex items-center">
                <ImageIcon className="mr-2 text-green-400" size={20} />
                Videó Beállítások
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label className="text-zinc-300">B-roll Keresés (Pexels)</Label>
                <Input
                  placeholder="pl. faith, spirituality, peaceful (üres = auto topic)"
                  value={brollSearch}
                  onChange={(e) => setBrollSearch(e.target.value)}
                  className="bg-zinc-800 border-zinc-700 text-white mt-1"
                />
                <p className="text-xs text-zinc-500 mt-1">
                  Ha üresen hagyod, a script topic-ját használja
                </p>
              </div>

              <div>
                <Label className="text-zinc-300">Háttérzene URL (opcionális)</Label>
                <Input
                  placeholder="https://example.com/music.mp3"
                  value={backgroundMusic}
                  onChange={(e) => setBackgroundMusic(e.target.value)}
                  className="bg-zinc-800 border-zinc-700 text-white mt-1"
                />
                <p className="text-xs text-zinc-500 mt-1">
                  Stock music vagy saját URL (MP3)
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Generate Button */}
          <Button
            onClick={handleGenerateVideo}
            disabled={!selectedScript || generating}
            className="w-full bg-gradient-to-r from-amber-400 to-amber-600 hover:from-amber-500 hover:to-amber-700 text-zinc-950 font-semibold h-14 text-lg"
          >
            {generating ? (
              <>
                <Loader2 className="mr-2 animate-spin" size={20} />
                Generálás folyamatban...
              </>
            ) : (
              <>
                <Wand2 className="mr-2" size={20} />
                Videó Generálás Indítása
              </>
            )}
          </Button>
        </div>

        {/* Info Panel */}
        <div className="space-y-6">
          <Card className="bg-gradient-to-br from-blue-400/10 to-blue-600/5 border-blue-400/20">
            <CardHeader>
              <CardTitle className="text-blue-400 text-lg">
                Videó Pipeline
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div className="flex items-start space-x-3">
                <span className="flex items-center justify-center w-6 h-6 bg-blue-400/10 text-blue-400 rounded-full font-semibold text-xs shrink-0">1</span>
                <div>
                  <p className="text-white font-medium">TTS Generálás</p>
                  <p className="text-zinc-400 text-xs">ElevenLabs custom voice + word timestamps</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <span className="flex items-center justify-center w-6 h-6 bg-blue-400/10 text-blue-400 rounded-full font-semibold text-xs shrink-0">2</span>
                <div>
                  <p className="text-white font-medium">B-roll Letöltés</p>
                  <p className="text-zinc-400 text-xs">Pexels 9:16 vertical videók (2-3mp clips)</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <span className="flex items-center justify-center w-6 h-6 bg-blue-400/10 text-blue-400 rounded-full font-semibold text-xs shrink-0">3</span>
                <div>
                  <p className="text-white font-medium">FFmpeg Assembly</p>
                  <p className="text-zinc-400 text-xs">Karaoke feliratok + audio mixing</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <span className="flex items-center justify-center w-6 h-6 bg-blue-400/10 text-blue-400 rounded-full font-semibold text-xs shrink-0">4</span>
                <div>
                  <p className="text-white font-medium">MP4 Export</p>
                  <p className="text-zinc-400 text-xs">9:16 formátum, 25-35mp, H.264</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-zinc-900/50 border-zinc-800">
            <CardHeader>
              <CardTitle className="text-white text-lg">
                Karaoke Feliratok
              </CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-zinc-400">
              <p className="mb-2">A feliratok automatikusan generálódnak:</p>
              <ul className="space-y-1 text-xs">
                <li>• Fehér alap szín</li>
                <li>• Citromsárga highlight az aktív szónál</li>
                <li>• Safe zones (YouTube UI elkerülése)</li>
                <li>• Word-level timing (ElevenLabs timestamps)</li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Video Queue/History */}
      <Card className="bg-zinc-900/50 border-zinc-800">
        <CardHeader>
          <CardTitle className="text-white">
            Generált Videók ({videos.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {videos.length > 0 ? (
            <div className="space-y-3">
              {videos.map((video) => (
                <div
                  key={video.id}
                  className="p-4 bg-zinc-800/50 rounded-lg border border-zinc-700 flex items-center justify-between"
                >
                  <div className="flex items-center space-x-4 flex-1">
                    {getStatusIcon(video.status)}
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <p className="font-medium text-white">Video #{video.id.slice(0, 8)}</p>
                        {getStatusBadge(video.status)}
                      </div>
                      <div className="flex items-center space-x-4 text-xs text-zinc-500">
                        <span>{new Date(video.created_at).toLocaleString('hu-HU')}</span>
                        {video.duration && <span>{video.duration.toFixed(1)}s</span>}
                      </div>
                      {video.error && (
                        <p className="text-xs text-red-400 mt-1">Hiba: {video.error}</p>
                      )}
                    </div>
                  </div>

                  {video.status === 'completed' && video.video_url && (
                    <Button
                      size="sm"
                      className="bg-green-500 hover:bg-green-600 text-white"
                      onClick={() => handleDownload(video.id)}
                    >
                      <Download size={14} className="mr-1" />
                      Letöltés
                    </Button>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <Film className="mx-auto mb-4 text-zinc-600" size={64} />
              <h3 className="text-xl font-semibold text-white mb-2">
                Még nincs generált videó
              </h3>
              <p className="text-zinc-400">
                Válassz egy scriptet és indítsd el a videó generálást!
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
