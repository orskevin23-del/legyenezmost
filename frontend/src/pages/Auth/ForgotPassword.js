import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { toast } from 'sonner';
import { ArrowLeft, Mail } from 'lucide-react';

export default function ForgotPassword() {
  const { api } = useAuth();
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await api.post('/auth/forgot-password', { email });
      setSent(true);
      toast.success('Jelszó visszaállítási link elküldve!');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Hiba történt');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-zinc-950 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold text-amber-400 mb-2">LEGYENEZ</h1>
          <p className="text-zinc-400 text-sm">Short Video Factory</p>
        </div>

        <Card className="bg-zinc-900 border-zinc-800">
          <CardHeader>
            <CardTitle className="text-white">Elfelejtett jelszó</CardTitle>
          </CardHeader>
          <CardContent>
            {!sent ? (
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <Label className="text-zinc-300">E-mail cím</Label>
                  <Input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="bg-zinc-800 border-zinc-700 text-white mt-1"
                    placeholder="Add meg az e-mail címed"
                    required
                  />
                </div>

                <Button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-amber-400 hover:bg-amber-500 text-zinc-950 font-semibold"
                >
                  {loading ? 'Küldés...' : (
                    <>
                      <Mail size={16} className="mr-2" />
                      Visszaállítási link küldése
                    </>
                  )}
                </Button>

                <Link to="/login">
                  <Button variant="ghost" className="w-full text-zinc-400 hover:text-white">
                    <ArrowLeft size={16} className="mr-2" />
                    Vissza a bejelentkezéshez
                  </Button>
                </Link>
              </form>
            ) : (
              <div className="text-center py-6">
                <div className="w-16 h-16 bg-green-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Mail className="text-green-400" size={32} />
                </div>
                <h3 className="text-white font-semibold mb-2">Link elküldve!</h3>
                <p className="text-zinc-400 text-sm mb-4">
                  Elküldtünk egy jelszó visszaállítási linket a <span className="text-amber-400">{email}</span> címre.
                </p>
                <Link to="/login">
                  <Button className="bg-amber-400 hover:bg-amber-500 text-zinc-950">
                    Vissza a bejelentkezéshez
                  </Button>
                </Link>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}