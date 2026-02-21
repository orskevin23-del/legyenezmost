import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Switch } from '../../components/ui/switch';
import { Badge } from '../../components/ui/badge';
import { toast } from 'sonner';
import { Sparkles, Copy, CheckCircle, XCircle, Plus, X } from 'lucide-react';

export default function ScriptGenerator() {
  const { api } = useAuth();
  const { t } = useLanguage();
  const [topic, setTopic] = useState('');
  const [keywords, setKeywords] = useState([]);
  const [keywordInput, setKeywordInput] = useState('');
  const [mode, setMode] = useState('FAITH_EXPLICIT');
  const [useAnalytics, setUseAnalytics] = useState(false);
  const [loading, setLoading] = useState(false);
  const [generatedScript, setGeneratedScript] = useState(null);
  const [insights, setInsights] = useState(null);

  useEffect(() => {
    if (useAnalytics) {
      fetchInsights();
    }
  }, [useAnalytics]);

  const fetchInsights = async () => {
    try {
      const res = await api.get('/notion-analytics/insights');
      setInsights(res.data);
    } catch (error) {
      console.error('Failed to fetch insights:', error);
    }
  };

  const addKeyword = () => {
    if (keywordInput.trim() && !keywords.includes(keywordInput.trim())) {
      setKeywords([...keywords, keywordInput.trim()]);
      setKeywordInput('');
    }
  };

  const removeKeyword = (keyword) => {
    setKeywords(keywords.filter(k => k !== keyword));
  };

  const generateScript = async () => {
    if (!topic.trim()) {
      toast.error(t('topic_required') || 'Please enter a topic!');
      return;
    }

    setLoading(true);

    try {
      const endpoint = useAnalytics ? '/scripts/generate-optimized' : '/scripts/generate';
      const res = await api.post(endpoint, {
        topic,
        mode,
        keywords,
        use_analytics: useAnalytics,
        top_n_examples: 3
      });

      setGeneratedScript(res.data);
      toast.success(t('script_success') || 'Script generated successfully!');
    } catch (error) {
      toast.error(error.response?.data?.detail || t('script_failed') || 'Script generation failed');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success(t('copied') || 'Copied to clipboard!');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold text-white mb-2">
          {t('script_generator')}
        </h1>
        <p className="text-zinc-400">
          {t('script_generator_subtitle')}
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Panel */}
        <Card className="bg-zinc-900 border-zinc-800">
          <CardHeader>
            <CardTitle className="text-white flex items-center">
              <Sparkles className="mr-2 text-amber-400" size={20} />
              {t('settings')}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* ML Analytics Toggle */}
            <div className="p-4 bg-gradient-to-r from-amber-400/10 to-amber-600/5 border border-amber-400/20 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <div>
                  <h4 className="font-semibold text-amber-400 text-sm">
                    {t('ml_optimized_generation') || 'ML-Optimized Generation'}
                  </h4>
                  <p className="text-xs text-zinc-400 mt-1">
                    {t('use_top_patterns') || 'Use top performing patterns from analytics data'}
                  </p>
                </div>
                <Switch
                  checked={useAnalytics}
                  onCheckedChange={setUseAnalytics}
                  className="data-[state=checked]:bg-amber-400"
                  disabled={!insights || insights.total_scripts === 0}
                />
              </div>
              
              {useAnalytics && insights && (
                <div className="mt-3 pt-3 border-t border-amber-400/20">
                  <p className="text-xs text-zinc-500 mb-2">{t('top_patterns') || 'Top Performing Patterns'}:</p>
                  <div className="space-y-1">
                    {insights.hook_effectiveness?.top_hooks_by_swipe_rate?.slice(0, 2).map((hook, idx) => (
                      <div key={idx} className="text-xs text-amber-400/80">
                        • "{hook.hook_title.substring(0, 40)}..." ({hook.swipe_rate?.toFixed(1)}% {t('swipe_rate')})
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {(!insights || insights.total_scripts === 0) && (
                <p className="text-xs text-yellow-400 mt-2">
                  ⚠️ {t('analytics_disabled')}
                </p>
              )}
            </div>

            {/* Topic Input */}
            <div>
              <Label className="text-zinc-300">{t('topic')}</Label>
              <Input
                placeholder={t('topic_placeholder')}
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                className="bg-zinc-800 border-zinc-700 text-white mt-1"
              />
            </div>

            {/* Keywords */}
            <div>
              <Label className="text-zinc-300">{t('keywords')}</Label>
              <div className="flex space-x-2 mt-1">
                <Input
                  placeholder={t('keyword_placeholder') || 'e.g. hope'}
                  value={keywordInput}
                  onChange={(e) => setKeywordInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && addKeyword()}
                  className="bg-zinc-800 border-zinc-700 text-white"
                />
                <Button onClick={addKeyword} variant="outline" className="border-zinc-700">
                  <Plus size={16} />
                </Button>
              </div>
              {keywords.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-2">
                  {keywords.map((keyword) => (
                    <Badge
                      key={keyword}
                      className="bg-amber-400/10 text-amber-400 border-amber-400/20"
                    >
                      {keyword}
                      <button onClick={() => removeKeyword(keyword)} className="ml-2">
                        <X size={12} />
                      </button>
                    </Badge>
                  ))}
                </div>
              )}
            </div>

            {/* Mode Selection */}
            <div>
              <Label className="text-zinc-300">{t('mode')}</Label>
              <div className="grid grid-cols-2 gap-2 mt-1">
                <Button
                  variant={mode === 'FAITH_EXPLICIT' ? 'default' : 'outline'}
                  onClick={() => setMode('FAITH_EXPLICIT')}
                  className={mode === 'FAITH_EXPLICIT' ? 'bg-amber-400 text-zinc-950' : 'border-zinc-700'}
                >
                  Faith Explicit
                </Button>
                <Button
                  variant={mode === 'STATE_BASED' ? 'default' : 'outline'}
                  onClick={() => setMode('STATE_BASED')}
                  className={mode === 'STATE_BASED' ? 'bg-amber-400 text-zinc-950' : 'border-zinc-700'}
                >
                  State Based
                </Button>
              </div>
            </div>

            {/* Generate Button */}
            <Button
              onClick={generateScript}
              disabled={loading}
              className="w-full bg-amber-400 hover:bg-amber-500 text-zinc-950 font-semibold h-12"
            >
              {loading ? (
                <>{t('generating')}</>
              ) : (
                <>
                  <Sparkles className="mr-2" size={20} />
                  {useAnalytics ? (t('ml_generate') || 'ML-Optimized Generation') : t('generate')}
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Output Panel */}
        <Card className="bg-zinc-900 border-zinc-800">
          <CardHeader>
            <CardTitle className="text-white">{t('generated_script')}</CardTitle>
          </CardHeader>
          <CardContent>
            {generatedScript ? (
              <div className="space-y-4">
                {/* ML Optimization Badge */}
                {generatedScript.ml_optimized && (
                  <div className="flex items-center p-3 bg-amber-400/10 border border-amber-400/20 rounded-lg">
                    <Sparkles className="text-amber-400 mr-2" size={16} />
                    <span className="text-sm text-amber-400 font-medium">
                      {t('generated_with_analytics')}
                    </span>
                  </div>
                )}

                {/* Hook Info */}
                <div className="p-4 bg-amber-400/5 border border-amber-400/20 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-sm font-semibold text-amber-400">{t('hook')}</h4>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => copyToClipboard(generatedScript.hook_text)}
                      className="text-amber-400 hover:text-amber-300"
                    >
                      <Copy size={14} />
                    </Button>
                  </div>
                  <p className="font-mono text-sm text-white mb-2">{generatedScript.hook_text}</p>
                  <div className="flex flex-wrap gap-2">
                    <Badge className="bg-blue-500/10 text-blue-400 border-blue-400/20">
                      {generatedScript.hook_type}
                    </Badge>
                    {generatedScript.tags?.map((tag) => (
                      <Badge key={tag} className="bg-zinc-700 text-zinc-300">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </div>

                {/* Full Script */}
                <div className="p-4 bg-zinc-800 border border-zinc-700 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-sm font-semibold text-white">{t('full_script')}</h4>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => copyToClipboard(generatedScript.script)}
                      className="text-zinc-400 hover:text-white"
                    >
                      <Copy size={14} />
                    </Button>
                  </div>
                  <p className="font-mono text-sm text-zinc-300 whitespace-pre-wrap leading-relaxed">
                    {generatedScript.script}
                  </p>
                </div>

                {/* Character Count */}
                <div className="flex items-center justify-between p-3 bg-zinc-800 rounded-lg">
                  <span className="text-sm text-zinc-400">{t('character_count')}</span>
                  <div className="flex items-center space-x-2">
                    <span className={`font-semibold ${
                      generatedScript.character_count <= 350 ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {generatedScript.character_count} / 350
                    </span>
                    {generatedScript.character_count <= 350 ? (
                      <CheckCircle className="text-green-400" size={16} />
                    ) : (
                      <XCircle className="text-red-400" size={16} />
                    )}
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-12 text-zinc-500">
                <Sparkles className="mx-auto mb-4 text-zinc-600" size={48} />
                <p>{t('no_script_yet') || 'No script generated yet.'}</p>
                <p className="text-sm mt-1">{t('enter_topic_generate') || 'Enter a topic and click Generate!'}</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
