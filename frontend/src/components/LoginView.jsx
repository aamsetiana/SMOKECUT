import React, { useState } from 'react';
import { Flame, Mail, Lock, Eye, EyeOff, ArrowRight } from 'lucide-react';

export default function LoginView({ onLogin }) {
  const [username, setUsername] = useState('indra@smokecut.id');
  const [password, setPassword] = useState('password123');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);

  const handleSubmit = (e) => {
    e.preventDefault();
    onLogin({ name: 'Indra Agustiawan', role: 'Tim MPA', email: username });
  };

  return (
    <div
      className="relative min-h-screen w-full flex flex-col md:flex-row select-none overflow-hidden bg-cover bg-center"
      style={{ backgroundImage: "url('/login-bg.jpg')" }}
    >
      {/* Cinematic dark overlay to make text and cards crisp */}
      <div className="absolute inset-0 bg-gradient-to-r from-black/85 via-black/45 to-black/75 pointer-events-none" />

      {/* Left Column: Hero Showcase */}
      <div className="relative z-10 md:w-3/5 min-h-[480px] flex flex-col justify-between p-8 md:p-14">
        {/* Top Brand */}
        <div className="flex items-center gap-3">
          <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-emerald-500 to-green-600 flex items-center justify-center shadow-lg shadow-emerald-500/30">
            <Flame className="w-7 h-7 text-white" />
          </div>
          <div>
            <h1 className="font-extrabold text-xl tracking-wider text-white">SMOKECUT</h1>
            <p className="text-xs text-white/85 font-medium">Smart Drone-Vision untuk Mitigasi Kebakaran Hutan</p>
          </div>
        </div>

        {/* Central Drone & Flame Illustration */}
        <div className="my-auto py-12">
          {/* Drone Silhouette and Vision Grid */}
          <div className="relative max-w-lg mb-8">
            <h2 className="text-3xl md:text-5xl font-black text-white leading-tight">
              Pantau. Deteksi. <br />
              Lindungi{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 via-green-300 to-emerald-200">
                Hutan Kita.
              </span>
            </h2>
            <p className="mt-4 text-sm md:text-base text-white/90 max-w-md leading-relaxed drop-shadow">
              Teknologi AI dan drone untuk deteksi dini kebakaran hutan, analisis risiko, dan rekomendasi sekat bakar optimal.
            </p>
          </div>
        </div>
      </div>

      {/* Right Column: Login Form - same position, transparent glassmorphism */}
      <div className="relative z-10 md:w-2/5 flex items-center justify-center p-6 md:p-12">
        <div className="w-full max-w-md bg-black/45 backdrop-blur-md border border-white/20 rounded-2xl p-8 shadow-2xl">
          <div className="text-center mb-6">
            <h3 className="text-xl font-extrabold text-white">Selamat Datang di SMOKECUT</h3>
            <p className="text-xs text-white/80 mt-1">Masuk untuk melanjutkan ke dashboard</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-white mb-1.5">Email atau Username</label>
              <div className="relative">
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full bg-black/40 border border-white/20 focus:border-emerald-400 focus:ring-1 focus:ring-emerald-400 rounded-xl px-4 py-2.5 pl-10 text-xs text-white placeholder-white/50 outline-none transition"
                  placeholder="name@smokecut.id"
                  required
                />
                <Mail className="w-4 h-4 text-white/70 absolute left-3.5 top-3" />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-white mb-1.5">Password</label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-black/40 border border-white/20 focus:border-emerald-400 focus:ring-1 focus:ring-emerald-400 rounded-xl px-4 py-2.5 pl-10 pr-10 text-xs text-white placeholder-white/50 outline-none transition"
                  placeholder="••••••••"
                  required
                />
                <Lock className="w-4 h-4 text-white/70 absolute left-3.5 top-3" />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3.5 top-3 text-white/70 hover:text-white"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between text-xs">
              <label className="flex items-center gap-2 text-white cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="rounded bg-black/50 border-white/30 text-emerald-500 accent-emerald-500 focus:ring-emerald-400 cursor-pointer"
                />
                <span>Ingat saya</span>
              </label>
              <button type="button" className="text-emerald-400 hover:text-emerald-300 hover:underline transition">
                Lupa password?
              </button>
            </div>

            <button
              type="submit"
              className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-emerald-600 via-emerald-500 to-green-500 hover:from-emerald-500 hover:to-green-400 text-white font-bold text-xs flex items-center justify-center gap-2 shadow-lg shadow-emerald-950/60 transition-all duration-200 mt-2"
            >
              <span>Masuk</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            <div className="relative flex py-2 items-center">
              <div className="flex-grow border-t border-white/20"></div>
              <span className="flex-shrink mx-3 text-[11px] text-white/60 font-medium">atau</span>
              <div className="flex-grow border-t border-white/20"></div>
            </div>

            <button
              type="button"
              onClick={handleSubmit}
              className="w-full py-2.5 px-4 rounded-xl bg-white/10 hover:bg-white/15 border border-white/20 text-white font-semibold text-xs flex items-center justify-center gap-2.5 transition"
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" />
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" />
              </svg>
              <span>Masuk dengan Google</span>
            </button>
          </form>

          <p className="text-center text-xs text-white/80 mt-6">
            Belum punya akun?{' '}
            <button
              onClick={() => onLogin({ name: 'Indra Agustiawan', role: 'Tim MPA' })}
              className="text-emerald-400 hover:text-emerald-300 hover:underline font-semibold"
            >
              Daftar di sini
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}
