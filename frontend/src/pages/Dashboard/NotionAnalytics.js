import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Button } from '../../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Input } from '../../components/ui/input';
import { Badge } from '../../components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '../../components/ui/dialog';
import { toast } from 'sonner';
import {
  Upload,
  Download,
  FileSpreadsheet,
  TrendingUp,
  Zap,
  BookOpen,
  Trash2,
  Info
} from 'lucide-react';

export default function NotionAnalytics() {
  const { api } = useAuth();
  const [uploading, setUploading] = useState(false);
  const [analyticsData, setAnalyticsData] = useState([]);
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showGuide, setShowGuide] = useState(false);
  const [guideData, setGuideData] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [dataRes, insightsRes] = await Promise.all([
        api.get('/notion-analytics/data?limit=50'),
        api.get('/notion-analytics/insights')
      ]);
      setAnalyticsData(dataRes.data);
      setInsights(insightsRes.data);
    } catch (error) {
      console.error('Failed to fetch analytics data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.name.endsWith('.csv')) {
      toast.error('Csak CSV fájlokat lehet feltölteni!');
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await api.post('/notion-analytics/import-csv', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      toast.success(`${response.data.imported_count} sor sikeresen importálva!`);
      
      if (response.data.errors && response.data.errors.length > 0) {
        toast.warning(`${response.data.errors.length} hiba történt az importálás során`);
      }

      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Import sikertelen');
    } finally {
      setUploading(false);
      e.target.value = null;
    }
  };

  const handleExport = async () => {
    try {
      const response = await api.get('/notion-analytics/export-csv', {
        responseType: 'blob'
      });

      const blob = new Blob([response.data], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `analytics_export_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      toast.success('CSV exportálva!');
    } catch (error) {
      toast.error('Export sikertelen');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Biztosan törlöd ezt az analytics adatot?')) return;

    try {
      await api.delete(`/notion-analytics/data/${id}`);
      toast.success('Adat törölve');
      fetchData();
    } catch (error) {
      toast.error('Törlés sikertelen');
    }
  };

  const fetchAlgorithmGuide = async () => {
    try {
      const response = await api.get('/notion-analytics/algorithm-guide');
      setGuideData(response.data);
      setShowGuide(true);
    } catch (error) {
      toast.error('Útmutató betöltése sikertelen');
    }
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
            Notion Analytics
          </h1>
          <p className="text-zinc-400">CSV import/export és ML insights</p>
        </div>
        <Button
          onClick={fetchAlgorithmGuide}
          variant="outline"
          className="border-amber-400/20 text-amber-400 hover:bg-amber-400/10"
        >
          <BookOpen size={16} className="mr-2" />
          Hogyan Működik?
        </Button>
      </div>

      {/* Upload & Export Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="bg-zinc-900/50 border-zinc-800">
          <CardHeader>
            <CardTitle className="text-white flex items-center">
              <Upload className="mr-2 text-green-400" size={20} />
              CSV Feltöltés
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="border-2 border-dashed border-zinc-700 rounded-lg p-8 text-center hover:border-amber-400/50 transition-colors">
              <FileSpreadsheet className="mx-auto mb-4 text-zinc-600" size={48} />
              <p className="text-zinc-400 mb-4">
                Húzd ide a Notion CSV fájlt vagy kattints a feltöltéshez
              </p>
              <Input
                type="file"
                accept=".csv"
                onChange={handleFileUpload}
                disabled={uploading}
                className="hidden"
                id="csv-upload"
              />
              <label htmlFor="csv-upload">
                <Button
                  as="span"
                  disabled={uploading}
                  className="bg-green-500 hover:bg-green-600 text-white cursor-pointer"
                >
                  {uploading ? 'Feltöltés...' : 'Fájl kiválasztása'}
                </Button>
              </label>
            </div>
            <p className="text-xs text-zinc-500 mt-3">
              Formátum: Social File, Retention Hook, Hook Title, Dominance Line, Open Loop, 
              Close, Resolve Script, Views, Swipe Rate, Retention %, Like, Comments, Sub-2/1000 views
            </p>
          </CardContent>
        </Card>

        <Card className="bg-zinc-900/50 border-zinc-800">
          <CardHeader>
            <CardTitle className="text-white flex items-center">
              <Download className="mr-2 text-blue-400" size={20} />
              CSV Export
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <p className="text-zinc-400">
                Exportáld az összes analytics adatodat CSV formátumban
              </p>
              <div className="bg-zinc-800 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-white">
                      {analyticsData.length} sor elérhető
                    </p>
                    <p className="text-xs text-zinc-500">
                      Retention, Swipe Rate, Likes, Views...
                    </p>
                  </div>
                  <Button
                    onClick={handleExport}
                    disabled={analyticsData.length === 0}
                    className="bg-blue-500 hover:bg-blue-600 text-white"
                  >
                    <Download size={16} className="mr-2" />
                    Exportálás
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Insights Section */}
      {insights && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Top Hooks by Swipe Rate */}
          <Card className="bg-gradient-to-br from-purple-400/10 to-purple-600/5 border-purple-400/20">
            <CardHeader>
              <CardTitle className="text-purple-400 text-lg flex items-center">
                <Zap size={18} className="mr-2" />
                Top Hookok (Swipe Rate)
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {insights.hook_effectiveness?.top_hooks_by_swipe_rate?.slice(0, 5).map((hook, idx) => (
                <div key={idx} className="p-3 bg-zinc-900/50 rounded-lg">
                  <p className="text-sm text-white font-medium line-clamp-1">
                    {hook.hook_title}
                  </p>
                  <div className="flex items-center justify-between mt-1">
                    <span className="text-xs text-zinc-500">{hook.retention_hook}</span>
                    <Badge className="bg-purple-400/10 text-purple-400 text-xs">
                      {hook.swipe_rate?.toFixed(1)}% swipe
                    </Badge>
                  </div>
                </div>
              )) || <p className="text-zinc-500 text-sm">Nincs adat</p>}
            </CardContent>
          </Card>

          {/* Top Dominance Lines */}
          <Card className="bg-gradient-to-br from-amber-400/10 to-amber-600/5 border-amber-400/20">
            <CardHeader>
              <CardTitle className="text-amber-400 text-lg flex items-center">
                <TrendingUp size={18} className="mr-2" />
                Top Dominance Lines
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {insights.script_effectiveness?.top_dominance_lines?.slice(0, 5).map((dom, idx) => (
                <div key={idx} className="p-3 bg-zinc-900/50 rounded-lg">
                  <p className="text-sm text-white line-clamp-2">
                    "{dom.dominance_line}"
                  </p>
                  <Badge className="bg-amber-400/10 text-amber-400 text-xs mt-2">
                    {dom.retention_percent?.toFixed(1)}% retention
                  </Badge>
                </div>
              )) || <p className="text-zinc-500 text-sm">Nincs adat</p>}
            </CardContent>
          </Card>

          {/* Top Open Loops */}
          <Card className="bg-gradient-to-br from-blue-400/10 to-blue-600/5 border-blue-400/20">
            <CardHeader>
              <CardTitle className="text-blue-400 text-lg flex items-center">
                <Info size={18} className="mr-2" />
                Top Open Loops
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {insights.script_effectiveness?.top_open_loops?.slice(0, 5).map((loop, idx) => (
                <div key={idx} className="p-3 bg-zinc-900/50 rounded-lg">
                  <p className="text-sm text-white line-clamp-2">
                    "{loop.open_loop}"
                  </p>
                  <Badge className="bg-blue-400/10 text-blue-400 text-xs mt-2">
                    {loop.retention_percent?.toFixed(1)}% retention
                  </Badge>
                </div>
              )) || <p className="text-zinc-500 text-sm">Nincs adat</p>}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Analytics Data Table */}
      {analyticsData.length > 0 && (
        <Card className="bg-zinc-900/50 border-zinc-800">
          <CardHeader>
            <CardTitle className="text-white">Analytics Adatok ({analyticsData.length})</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="border-b border-zinc-800">
                  <tr className="text-left text-zinc-400">
                    <th className="pb-3 font-medium">Video</th>
                    <th className="pb-3 font-medium">Hook</th>
                    <th className="pb-3 font-medium">Views</th>
                    <th className="pb-3 font-medium">Swipe %</th>
                    <th className="pb-3 font-medium">Retention %</th>
                    <th className="pb-3 font-medium">Likes</th>
                    <th className="pb-3 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-800">
                  {analyticsData.map((row) => (
                    <tr key={row.id} className="text-zinc-300">
                      <td className="py-3">{row.social_file}</td>
                      <td className="py-3">
                        <span className="text-xs bg-zinc-800 px-2 py-1 rounded">
                          {row.retention_hook}
                        </span>
                      </td>
                      <td className="py-3">{row.views?.toLocaleString()}</td>
                      <td className="py-3">
                        <Badge className={`${
                          row.swipe_rate >= 70 ? 'bg-green-400/10 text-green-400' : 'bg-red-400/10 text-red-400'
                        }`}>
                          {row.swipe_rate?.toFixed(1)}%
                        </Badge>
                      </td>
                      <td className="py-3">
                        <Badge className={`${
                          row.retention_percent >= 60 ? 'bg-green-400/10 text-green-400' : 'bg-red-400/10 text-red-400'
                        }`}>
                          {row.retention_percent?.toFixed(1)}%
                        </Badge>
                      </td>
                      <td className="py-3">{row.likes}</td>
                      <td className="py-3">
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleDelete(row.id)}
                          className="text-red-400 hover:text-red-300"
                        >
                          <Trash2 size={14} />
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Empty State */}
      {analyticsData.length === 0 && (
        <Card className="bg-zinc-900/50 border-zinc-800">
          <CardContent className="py-12 text-center">
            <FileSpreadsheet className="mx-auto mb-4 text-zinc-600" size={64} />
            <h3 className="text-xl font-semibold text-white mb-2">
              Még nincs analytics adat
            </h3>
            <p className="text-zinc-400 mb-6">
              Töltsd fel a Notion CSV-det a metrikák elemzéséhez
            </p>
          </CardContent>
        </Card>
      )}

      {/* Algorithm Guide Modal */}
      <Dialog open={showGuide} onOpenChange={setShowGuide}>
        <DialogContent className="bg-zinc-900 border-zinc-800 max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-2xl text-amber-400">
              {guideData?.title || 'YouTube Shorts Algoritmus Útmutató'}
            </DialogTitle>
            <DialogDescription className="text-zinc-400">
              Hogyan működik a Hook vs Script, Swipe Rate vs Retention
            </DialogDescription>
          </DialogHeader>
          
          {guideData && (
            <div className="space-y-6 mt-4">
              {guideData.sections?.map((section, idx) => (
                <Card key={idx} className="bg-zinc-800/50 border-zinc-700">
                  <CardHeader>
                    <CardTitle className="text-lg text-white">
                      {section.title}
                    </CardTitle>
                    <p className="text-sm text-amber-400">{section.metric}</p>
                  </CardHeader>
                  <CardContent className="space-y-3 text-sm">
                    <p className="text-zinc-300">{section.description}</p>
                    
                    {section.goal && (
                      <div className="p-3 bg-green-400/10 border border-green-400/20 rounded">
                        <p className="text-green-400 font-medium">Cél: {section.goal}</p>
                      </div>
                    )}

                    {section.benchmarks && (
                      <div className="grid grid-cols-3 gap-2">
                        <div className="p-2 bg-zinc-900 rounded text-center">
                          <p className="text-xs text-zinc-500">Excellent</p>
                          <p className="text-green-400 font-semibold">{section.benchmarks.excellent}</p>
                        </div>
                        <div className="p-2 bg-zinc-900 rounded text-center">
                          <p className="text-xs text-zinc-500">Good</p>
                          <p className="text-blue-400 font-semibold">{section.benchmarks.good}</p>
                        </div>
                        <div className="p-2 bg-zinc-900 rounded text-center">
                          <p className="text-xs text-zinc-500">Poor</p>
                          <p className="text-red-400 font-semibold">{section.benchmarks.poor}</p>
                        </div>
                      </div>
                    )}

                    {section.tips && (
                      <div className="space-y-1">
                        {section.tips.map((tip, tipIdx) => (
                          <p key={tipIdx} className="text-zinc-400 flex items-start">
                            <span className="text-amber-400 mr-2">•</span>
                            {tip}
                          </p>
                        ))}
                      </div>
                    )}

                    {section.examples && (
                      <div className="space-y-1">
                        <p className="text-zinc-500 font-medium">Példák:</p>
                        {section.examples.map((example, exIdx) => (
                          <p key={exIdx} className="text-zinc-400 italic">
                            "{example}"
                          </p>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}

              {/* Key Metrics Explained */}
              {guideData.key_metrics_explained && (
                <Card className="bg-amber-400/5 border-amber-400/20">
                  <CardHeader>
                    <CardTitle className="text-amber-400">Metrikák Magyarázata</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <h4 className="font-semibold text-white mb-1">Swipe Rate</h4>
                      <p className="text-sm text-zinc-400">
                        {guideData.key_metrics_explained.swipe_rate.what}
                      </p>
                      <p className="text-xs text-amber-400 mt-1">
                        Irányítja: {guideData.key_metrics_explained.swipe_rate.controlled_by}
                      </p>
                    </div>
                    <div>
                      <h4 className="font-semibold text-white mb-1">Retention Rate</h4>
                      <p className="text-sm text-zinc-400">
                        {guideData.key_metrics_explained.retention_rate.what}
                      </p>
                      <p className="text-xs text-green-400 mt-1">
                        Irányítja: {guideData.key_metrics_explained.retention_rate.controlled_by}
                      </p>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
