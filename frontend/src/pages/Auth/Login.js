import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { toast } from 'sonner';

export default function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const { t } = useLanguage();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);

    const result = await login(email, password);

    if (result.success) {
      toast.success('Sikeres bejelentkezés!');
      navigate('/dashboard');
    } else {
      toast.error(result.error || 'Bejelentkezés sikertelen');
    }

    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-zinc-950 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo/Title */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold text-amber-400 mb-2">
            LEGYENEZ
          </h1>
          <p className="text-zinc-400 text-sm">Short Video Factory</p>
        </div>

        {/* Login Card */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-8 shadow-2xl">
          <h2 className="text-2xl font-semibold text-white mb-6">
            {t('login_title')}
          </h2>

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <Label htmlFor="email" className="text-zinc-300">{t('email')}</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="bg-zinc-800 border-zinc-700 text-white mt-1"
                required
              />
            </div>

            <div>
              <Label htmlFor="password" className="text-zinc-300">{t('password')}</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="bg-zinc-800 border-zinc-700 text-white mt-1"
                required
              />
            </div>

            <Button
              type="submit"
              disabled={loading}
              className="w-full bg-amber-400 hover:bg-amber-500 text-zinc-950 font-semibold"
            >
              {loading ? 'Betöltés...' : t('login_button')}
            </Button>
          </form>

          <div className="mt-6 text-center space-y-3">
            <Link to="/forgot-password" className="block text-amber-400 hover:text-amber-300 text-sm">
              Elfelejtetted a jelszavad?
            </Link>
            <p className="text-zinc-400 text-sm">
              Még nincs fiókod?{' '}
              <Link to="/register" className="text-amber-400 hover:text-amber-300 font-medium">
                Regisztrálj
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}