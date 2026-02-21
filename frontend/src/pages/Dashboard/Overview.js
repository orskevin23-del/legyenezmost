import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { Button } from '../../components/ui/button';
import { Card, CardContent } from '../../components/ui/card';
import { FileText, Bookmark, TrendingUp, Play, Sparkles, Upload, BarChart, Zap } from 'lucide-react';

export default function DashboardOverview() {
  const { user, api } = useAuth();
  const { t } = useLanguage();
  const [stats, setStats] = useState({
    total_scripts: 0,
    total_hooks: 0,
    avg_retention: 0,
    avg_swipe_rate: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [scriptsRes, hooksRes, analyticsRes, notionAnalyticsRes] = await Promise.all([
        api.get('/scripts?limit=10'),
        api.get('/hooks?limit=10'),
        api.get('/analytics/overview'),
        api.get('/notion-analytics/insights').catch(() => ({ data: { average_stats: null } }))
      ]);

      setStats({
        total_scripts: scriptsRes.data.length,
        total_hooks: hooksRes.data.length,
        avg_retention: analyticsRes.data.avg_retention || 0,
        avg_swipe_rate: notionAnalyticsRes.data?.average_stats?.avg_swipe_rate || 0
      });
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-amber-400 text-lg">{t('loading')}</div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Welcome Section */}
      <div className="text-center space-y-2">
        <h1 className="text-5xl font-bold text-white">
          {t('welcome')}, {user?.name}! 👋
        </h1>
        <p className="text-xl text-zinc-400">
          {t('welcome_message')}
        </p>
      </div>

      {/* Stats Cards - Responsive Grid: Mobile 2 cols, Tablet 2 cols, Desktop 4 cols */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        <Card className="bg-zinc-900/50 border-zinc-800 backdrop-blur">
          <CardContent className="p-4 sm:p-6">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
              <div className="w-full">
                <p className="text-xs sm:text-sm text-zinc-500 mb-1">{t('total_scripts')}</p>
                <p className="text-2xl sm:text-4xl font-bold text-white">{stats.total_scripts}</p>
              </div>
              <div className="p-2 sm:p-3 bg-amber-400/10 rounded-xl">
                <FileText className="text-amber-400" size={20} />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-zinc-900/50 border-zinc-800 backdrop-blur">
          <CardContent className="p-4 sm:p-6">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
              <div className="w-full">
                <p className="text-xs sm:text-sm text-zinc-500 mb-1">{t('total_hooks')}</p>
                <p className="text-2xl sm:text-4xl font-bold text-white">{stats.total_hooks}</p>
              </div>
              <div className="p-2 sm:p-3 bg-blue-400/10 rounded-xl">
                <Bookmark className="text-blue-400" size={20} />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-zinc-900/50 border-zinc-800 backdrop-blur">
          <CardContent className="p-4 sm:p-6">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
              <div className="w-full">
                <p className="text-xs sm:text-sm text-zinc-500 mb-1">{t('avg_retention')}</p>
                <p className="text-2xl sm:text-4xl font-bold text-white">{stats.avg_retention.toFixed(1)}%</p>
              </div>
              <div className="p-2 sm:p-3 bg-green-400/10 rounded-xl">
                <TrendingUp className="text-green-400" size={20} />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-zinc-900/50 border-zinc-800 backdrop-blur">
          <CardContent className="p-4 sm:p-6">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
              <div className="w-full">
                <p className="text-xs sm:text-sm text-zinc-500 mb-1">{t('swipe_rate')}</p>
                <p className="text-2xl sm:text-4xl font-bold text-white">{stats.avg_swipe_rate.toFixed(1)}%</p>
              </div>
              <div className="p-2 sm:p-3 bg-purple-400/10 rounded-xl">
                <Zap className="text-purple-400" size={20} />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions - Mobile Optimized */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
        <Link to="/dashboard/scripts" className="group">
          <Card className="bg-gradient-to-br from-amber-400/10 to-amber-600/5 border-amber-400/20 hover:border-amber-400/50 transition-all cursor-pointer h-full">
            <CardContent className="p-6 flex flex-col items-center text-center space-y-3">
              <div className="p-4 bg-amber-400/10 rounded-full group-hover:scale-110 transition-transform">
                <Sparkles className="text-amber-400" size={32} />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white mb-1">{t('script_generation')}</h3>
                <p className="text-sm text-zinc-400">{t('script_generation_desc')}</p>
              </div>
            </CardContent>
          </Card>
        </Link>

        <Link to="/dashboard/videos" className="group">
          <Card className="bg-gradient-to-br from-blue-400/10 to-blue-600/5 border-blue-400/20 hover:border-blue-400/50 transition-all cursor-pointer h-full">
            <CardContent className="p-6 flex flex-col items-center text-center space-y-3">
              <div className="p-4 bg-blue-400/10 rounded-full group-hover:scale-110 transition-transform">
                <Play className="text-blue-400" size={32} />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white mb-1">{t('video_creation')}</h3>
                <p className="text-sm text-zinc-400">{t('video_creation_desc')}</p>
              </div>
            </CardContent>
          </Card>
        </Link>

        <Link to="/dashboard/notion-analytics" className="group">
          <Card className="bg-gradient-to-br from-green-400/10 to-green-600/5 border-green-400/20 hover:border-green-400/50 transition-all cursor-pointer h-full">
            <CardContent className="p-6 flex flex-col items-center text-center space-y-3">
              <div className="p-4 bg-green-400/10 rounded-full group-hover:scale-110 transition-transform">
                <Upload className="text-green-400" size={32} />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white mb-1">{t('analytics_upload')}</h3>
                <p className="text-sm text-zinc-400">{t('analytics_upload_desc')}</p>
              </div>
            </CardContent>
          </Card>
        </Link>
      </div>

      {/* How to Start - Process Steps */}
      <Card className="bg-zinc-900/30 border-zinc-800">
        <CardContent className="p-8">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-white mb-2">{t('how_to_start')}</h2>
            <p className="text-zinc-400">{t('how_to_start_desc')}</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="text-center space-y-3">
              <div className="w-12 h-12 mx-auto bg-amber-400 rounded-full flex items-center justify-center text-zinc-950 font-bold text-xl">
                1
              </div>
              <h3 className="font-semibold text-white">{t('step_1_title')}</h3>
              <p className="text-sm text-zinc-500">{t('step_1_desc')}</p>
            </div>

            <div className="text-center space-y-3">
              <div className="w-12 h-12 mx-auto bg-blue-400 rounded-full flex items-center justify-center text-zinc-950 font-bold text-xl">
                2
              </div>
              <h3 className="font-semibold text-white">{t('step_2_title')}</h3>
              <p className="text-sm text-zinc-500">{t('step_2_desc')}</p>
            </div>

            <div className="text-center space-y-3">
              <div className="w-12 h-12 mx-auto bg-green-400 rounded-full flex items-center justify-center text-zinc-950 font-bold text-xl">
                3
              </div>
              <h3 className="font-semibold text-white">{t('step_3_title')}</h3>
              <p className="text-sm text-zinc-500">{t('step_3_desc')}</p>
            </div>

            <div className="text-center space-y-3">
              <div className="w-12 h-12 mx-auto bg-purple-400 rounded-full flex items-center justify-center text-zinc-950 font-bold text-xl">
                4
              </div>
              <h3 className="font-semibold text-white">{t('step_4_title')}</h3>
              <p className="text-sm text-zinc-500">{t('step_4_desc')}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
