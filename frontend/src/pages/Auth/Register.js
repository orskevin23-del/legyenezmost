import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { toast } from 'sonner';

export default function Register() {
  const navigate = useNavigate();
  const { register } = useAuth();
  const { t } = useLanguage();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);

    const result = await register(email, password, name);

    if (result.success) {
      toast.success('Sikeres regisztráció!');
      navigate('/dashboard');
    } else {
      toast.error(result.error || 'Regisztráció sikertelen');
    }

    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-zinc-950 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo/Title */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold text-amber-400 mb-2" >
            LEGYENEZ
          </h1>
          <p className="text-zinc-400 text-sm">Short Video Factory</p>
        </div>

        {/* Register Card */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-8 shadow-2xl">
          <h2 className="text-2xl font-semibold text-white mb-6" >
            {t('register_title')}
          </h2>

          <form onSubmit={handleRegister} className="space-y-4">
            <div>
              <Label htmlFor="name" className="text-zinc-300">{t('name')}</Label>
              <Input
                id="name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="bg-zinc-800 border-zinc-700 text-white mt-1"
                required
              />
            </div>

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
              {loading ? 'Betöltés...' : t('register_button')}
            </Button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-zinc-400 text-sm">
              Van már fiókod?{' '}
              <Link to="/login" className="text-amber-400 hover:text-amber-300 font-medium">
                Jelentkezz be
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}