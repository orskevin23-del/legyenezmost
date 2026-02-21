import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '../../components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../../components/ui/select';
import { toast } from 'sonner';
import {
  Bookmark,
  Search,
  Filter,
  Copy,
  Trash2,
  Plus,
  TrendingUp,
  Calendar,
  Hash
} from 'lucide-react';

export default function HookLibrary() {
  const { api } = useAuth();
  const { t, language } = useLanguage();
  const [hooks, setHooks] = useState([]);
  const [filteredHooks, setFilteredHooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [modeFilter, setModeFilter] = useState('all');
  const [hookTypeFilter, setHookTypeFilter] = useState('all');
  const [sortBy, setSortBy] = useState('created_at');
  const [showCreateDialog, setShowCreateDialog] = useState(false);

  // Create Hook Form State
  const [newHook, setNewHook] = useState({
    hook_text: '',
    mode: 'FAITH_EXPLICIT',
    hook_type: 'emotional_trigger',
    tags: [],
    avg_retention: 0
  });
  const [tagInput, setTagInput] = useState('');

  const hookTypes = [
    { value: 'emotional_trigger', label: t('emotional_trigger') },
    { value: 'urgency', label: t('urgency') },
    { value: 'identity_filter', label: t('identity_filter') },
    { value: 'reverse_psychology', label: t('reverse_psychology') },
    { value: 'not_for_everyone', label: t('not_for_everyone') },
    { value: 'dominance_line', label: t('dominance_line') },
    { value: 'open_loop', label: t('open_loop') }
  ];

  useEffect(() => {
    fetchHooks();
  }, [sortBy]);

  useEffect(() => {
    applyFilters();
  }, [hooks, searchQuery, modeFilter, hookTypeFilter]);

  const fetchHooks = async () => {
    try {
      const response = await api.get(`/hooks?sort_by=${sortBy}&limit=200`);
      setHooks(response.data);
    } catch (error) {
      console.error('Failed to fetch hooks:', error);
      toast.error(t('hook_load_failed'));
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...hooks];

    // Search filter
    if (searchQuery) {
      filtered = filtered.filter(hook =>
        hook.hook_text.toLowerCase().includes(searchQuery.toLowerCase()) ||
        hook.tags?.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
      );
    }

    // Mode filter
    if (modeFilter !== 'all') {
      filtered = filtered.filter(hook => hook.mode === modeFilter);
    }

    // Hook type filter
    if (hookTypeFilter !== 'all') {
      filtered = filtered.filter(hook => hook.hook_type === hookTypeFilter);
    }

    setFilteredHooks(filtered);
  };

  const handleCreateHook = async () => {
    if (!newHook.hook_text.trim()) {
      toast.error('Hook szöveg megadása kötelező!');
      return;
    }

    try {
      await api.post('/hooks', newHook);
      toast.success('Hook létrehozva!');
      setShowCreateDialog(false);
      setNewHook({
        hook_text: '',
        mode: 'FAITH_EXPLICIT',
        hook_type: 'emotional_trigger',
        tags: [],
        avg_retention: 0
      });
      fetchHooks();
    } catch (error) {
      toast.error('Hook létrehozása sikertelen');
    }
  };

  const handleDeleteHook = async (id) => {
    if (!window.confirm('Biztosan törlöd ezt a hookot?')) return;

    try {
      await api.delete(`/hooks/${id}`);
      toast.success('Hook törölve');
      fetchHooks();
    } catch (error) {
      toast.error('Törlés sikertelen');
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Vágólapra másolva!');
  };

  const addTag = () => {
    if (tagInput.trim() && !newHook.tags.includes(tagInput.trim())) {
      setNewHook({ ...newHook, tags: [...newHook.tags, tagInput.trim()] });
      setTagInput('');
    }
  };

  const removeTag = (tag) => {
    setNewHook({ ...newHook, tags: newHook.tags.filter(t => t !== tag) });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-amber-400 text-lg">Betöltés...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold text-white mb-2">
            Hook Könyvtár
          </h1>
          <p className="text-zinc-400">
            {filteredHooks.length} hook • Automatikus és manuális gyűjtemény
          </p>
        </div>
        <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
          <DialogTrigger asChild>
            <Button className="bg-amber-400 hover:bg-amber-500 text-zinc-950 font-semibold">
              <Plus size={16} className="mr-2" />
              Új Hook
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-zinc-900 border-zinc-800">
            <DialogHeader>
              <DialogTitle className="text-white">Új Hook Létrehozása</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 mt-4">
              <div>
                <Label className="text-zinc-300">Hook Szöveg</Label>
                <Input
                  value={newHook.hook_text}
                  onChange={(e) => setNewHook({ ...newHook, hook_text: e.target.value })}
                  placeholder="Weißt du, was wirklich zählt?"
                  className="bg-zinc-800 border-zinc-700 text-white mt-1"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-zinc-300">Mód</Label>
                  <Select value={newHook.mode} onValueChange={(val) => setNewHook({ ...newHook, mode: val })}>
                    <SelectTrigger className="bg-zinc-800 border-zinc-700 text-white mt-1">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-zinc-800 border-zinc-700">
                      <SelectItem value="FAITH_EXPLICIT">Faith Explicit</SelectItem>
                      <SelectItem value="STATE_BASED">State Based</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label className="text-zinc-300">Hook Típus</Label>
                  <Select value={newHook.hook_type} onValueChange={(val) => setNewHook({ ...newHook, hook_type: val })}>
                    <SelectTrigger className="bg-zinc-800 border-zinc-700 text-white mt-1">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-zinc-800 border-zinc-700">
                      {hookTypes.map(type => (
                        <SelectItem key={type.value} value={type.value}>{type.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div>
                <Label className="text-zinc-300">Tagek</Label>
                <div className="flex space-x-2 mt-1">
                  <Input
                    value={tagInput}
                    onChange={(e) => setTagInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && addTag()}
                    placeholder="pl. Hoffnung"
                    className="bg-zinc-800 border-zinc-700 text-white"
                  />
                  <Button onClick={addTag} variant="outline" className="border-zinc-700">
                    <Plus size={16} />
                  </Button>
                </div>
                {newHook.tags.length > 0 && (
                  <div className="flex flex-wrap gap-2 mt-2">
                    {newHook.tags.map(tag => (
                      <Badge key={tag} className="bg-amber-400/10 text-amber-400">
                        {tag}
                        <button onClick={() => removeTag(tag)} className="ml-2">×</button>
                      </Badge>
                    ))}
                  </div>
                )}
              </div>

              <div>
                <Label className="text-zinc-300">Átlag Retention %</Label>
                <Input
                  type="number"
                  value={newHook.avg_retention}
                  onChange={(e) => setNewHook({ ...newHook, avg_retention: parseFloat(e.target.value) })}
                  placeholder="0"
                  className="bg-zinc-800 border-zinc-700 text-white mt-1"
                />
              </div>

              <Button
                onClick={handleCreateHook}
                className="w-full bg-amber-400 hover:bg-amber-500 text-zinc-950"
              >
                Hook Létrehozása
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Filters */}
      <Card className="bg-zinc-900/50 border-zinc-800">
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Search */}
            <div className="md:col-span-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" size={18} />
                <Input
                  placeholder="Hook szöveg vagy tag keresése..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="bg-zinc-800 border-zinc-700 text-white pl-10"
                />
              </div>
            </div>

            {/* Mode Filter */}
            <div>
              <Select value={modeFilter} onValueChange={setModeFilter}>
                <SelectTrigger className="bg-zinc-800 border-zinc-700 text-white">
                  <SelectValue placeholder="Mód" />
                </SelectTrigger>
                <SelectContent className="bg-zinc-800 border-zinc-700">
                  <SelectItem value="all">Összes Mód</SelectItem>
                  <SelectItem value="FAITH_EXPLICIT">Faith Explicit</SelectItem>
                  <SelectItem value="STATE_BASED">State Based</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Hook Type Filter */}
            <div>
              <Select value={hookTypeFilter} onValueChange={setHookTypeFilter}>
                <SelectTrigger className="bg-zinc-800 border-zinc-700 text-white">
                  <SelectValue placeholder="Hook Típus" />
                </SelectTrigger>
                <SelectContent className="bg-zinc-800 border-zinc-700">
                  <SelectItem value="all">Összes Típus</SelectItem>
                  {hookTypes.map(type => (
                    <SelectItem key={type.value} value={type.value}>{type.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Sort */}
          <div className="flex items-center space-x-2 mt-4">
            <Filter size={16} className="text-zinc-500" />
            <span className="text-sm text-zinc-400">Rendezés:</span>
            <div className="flex space-x-2">
              {[
                { value: 'created_at', label: 'Dátum', icon: Calendar },
                { value: 'avg_retention', label: 'Retention %', icon: TrendingUp },
                { value: 'usage_count', label: 'Használat', icon: Hash }
              ].map(sort => (
                <Button
                  key={sort.value}
                  size="sm"
                  variant={sortBy === sort.value ? 'default' : 'outline'}
                  onClick={() => setSortBy(sort.value)}
                  className={sortBy === sort.value 
                    ? 'bg-amber-400 text-zinc-950' 
                    : 'border-zinc-700 text-zinc-400'
                  }
                >
                  <sort.icon size={14} className="mr-1" />
                  {sort.label}
                </Button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Hooks Grid */}
      {filteredHooks.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredHooks.map((hook) => (
            <Card key={hook.id} className="bg-zinc-900/50 border-zinc-800 hover:border-amber-400/50 transition-all group">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <Badge className={
                        hook.mode === 'FAITH_EXPLICIT' 
                          ? 'bg-amber-400/10 text-amber-400 border-amber-400/20' 
                          : 'bg-blue-400/10 text-blue-400 border-blue-400/20'
                      }>
                        {hook.mode === 'FAITH_EXPLICIT' ? 'Faith' : 'State'}
                      </Badge>
                      <Badge className="bg-zinc-800 text-zinc-300 text-xs">
                        {hook.hook_type}
                      </Badge>
                    </div>
                    {hook.avg_retention > 0 && (
                      <Badge className="bg-green-400/10 text-green-400 border-green-400/20 text-xs">
                        <TrendingUp size={12} className="mr-1" />
                        {hook.avg_retention.toFixed(1)}% retention
                      </Badge>
                    )}
                  </div>
                  <div className="flex space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => copyToClipboard(hook.hook_text)}
                      className="text-zinc-400 hover:text-white"
                    >
                      <Copy size={14} />
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleDeleteHook(hook.id)}
                      className="text-red-400 hover:text-red-300"
                    >
                      <Trash2 size={14} />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-white font-mono text-sm leading-relaxed mb-3">
                  {hook.hook_text}
                </p>
                
                {hook.tags && hook.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1 mb-3">
                    {hook.tags.map(tag => (
                      <Badge key={tag} className="bg-zinc-800 text-zinc-400 text-xs">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                )}

                <div className="flex items-center justify-between text-xs text-zinc-500">
                  <span>{hook.usage_count || 0}× használva</span>
                  <span>{new Date(hook.created_at).toLocaleDateString('hu-HU')}</span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card className="bg-zinc-900/50 border-zinc-800">
          <CardContent className="py-12 text-center">
            <Bookmark className="mx-auto mb-4 text-zinc-600" size={64} />
            <h3 className="text-xl font-semibold text-white mb-2">
              {searchQuery || modeFilter !== 'all' || hookTypeFilter !== 'all'
                ? 'Nincs találat'
                : 'Még nincs hook'}
            </h3>
            <p className="text-zinc-400 mb-6">
              {searchQuery || modeFilter !== 'all' || hookTypeFilter !== 'all'
                ? 'Próbálj meg más keresési feltételeket'
                : 'Generálj scripteket vagy hozz létre manuálisan hookokat'}
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
