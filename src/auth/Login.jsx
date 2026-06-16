import { useState } from "react";

const Login = () => {
  const [activeTab, setActiveTab] = useState("seeker");
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  return (
    <div className="min-h-screen bg-[#EEF0F8] flex flex-col font-sans">
      {/* Navbar */}
      <nav className="bg-white border-b border-gray-200 px-8 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-purple-600 rounded-xl flex items-center justify-center">
            <svg className="w-5 h-5 text-white" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="10" fill="white" fillOpacity="0.2" />
              <path
                d="M8 12C8 9.79 9.79 8 12 8s4 1.79 4 4-1.79 4-4 4"
                stroke="white"
                strokeWidth="2"
                strokeLinecap="round"
              />
              <circle cx="12" cy="12" r="2" fill="white" />
              <path
                d="M12 6V4M12 20v-2M18 12h2M4 12h2"
                stroke="white"
                strokeWidth="1.5"
                strokeLinecap="round"
              />
            </svg>
          </div>
          <span className="text-base font-semibold text-gray-900">
            Intelligent Job Portal
          </span>
        </div>
        <div className="flex items-center gap-8">
          <a
            href="#"
            className="text-sm text-gray-500 hover:text-gray-800 transition-colors"
          >
            Jobs
          </a>
          <a
            href="#"
            className="text-sm text-gray-500 hover:text-gray-800 transition-colors"
          >
            Companies
          </a>
          <a
            href="#"
            className="text-sm text-gray-500 hover:text-gray-800 transition-colors"
          >
            Salaries
          </a>
          <button className="bg-purple-600 hover:bg-purple-700 text-white text-sm font-medium px-5 py-2 rounded-lg transition-colors">
            Sign Up
          </button>
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-1 flex items-center justify-center p-8">
        <div className="bg-white rounded-2xl flex max-w-4xl w-full overflow-hidden shadow-md">
          {/* Left Panel */}
          <div className="flex-1 p-10 relative overflow-hidden flex flex-col justify-center">
            {/* Decorative blobs */}
            {/* <div className="absolute -bottom-10 -left-6 w-52 h-52 bg-purple-200 rounded-[50%_60%_40%_70%] opacity-70" /> */}
            {/* <div className="absolute -bottom-12 right-6 w-40 h-48 bg-purple-300 rounded-[60%_40%_70%_30%] opacity-60" /> */}

            <span className="inline-block text-xs font-semibold text-purple-600 bg-purple-100 px-3 py-1 rounded-full tracking-widest uppercase mb-5 w-fit">
              New era of hiring
            </span>

            <h1 className="text-4xl font-extrabold text-gray-900 leading-tight mb-4">
              Find your next
              <br />
              <span className="text-purple-600">opportunity</span>
              <br />
              faster.
            </h1>

            <p className="text-sm text-gray-500 leading-relaxed mb-8 max-w-xs">
              Leverage AI-powered matching to connect with top-tier companies
              and roles tailored precisely to your skillset.
            </p>

            <ul className="space-y-3 relative z-10">
              {[
                "Smart Resume Analysis",
                "Instant Recruiter Messaging",
                "Personalized Career Coaching",
              ].map((item) => (
                <li
                  key={item}
                  className="flex items-center gap-3 text-sm text-gray-700"
                >
                  <span className="w-5 h-5 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
                    <svg className="w-3 h-3" viewBox="0 0 12 12" fill="none">
                      <path
                        d="M2 6l3 3 5-5"
                        stroke="#10B981"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                  </span>
                  {item}
                </li>
              ))}
            </ul>
          </div>

          {/* Right Panel */}
          <div className="w-96 p-10 border-l border-gray-100 flex flex-col justify-center">
            <h2 className="text-xl font-bold text-gray-900 mb-1">
              Welcome back
            </h2>
            <p className="text-sm text-gray-400 mb-6">
              Please enter your details to continue your journey.
            </p>

            {/* Tab Toggle */}
            <div className="flex bg-gray-100 rounded-xl p-1 gap-1 mb-6">
              <button
                onClick={() => setActiveTab("seeker")}
                className={`flex-1 flex items-center justify-center gap-2 py-2 rounded-lg text-sm font-medium transition-all ${
                  activeTab === "seeker"
                    ? "bg-white text-gray-900 shadow-sm"
                    : "text-gray-500 hover:text-gray-700"
                }`}
              >
                <svg
                  className="w-4 h-4"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                  <circle cx="12" cy="7" r="4" />
                </svg>
                Job Seeker
              </button>
              <button
                onClick={() => setActiveTab("recruiter")}
                className={`flex-1 flex items-center justify-center gap-2 py-2 rounded-lg text-sm font-medium transition-all ${
                  activeTab === "recruiter"
                    ? "bg-white text-gray-900 shadow-sm"
                    : "text-gray-500 hover:text-gray-700"
                }`}
              >
                <svg
                  className="w-4 h-4"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <rect x="2" y="7" width="20" height="14" rx="2" />
                  <path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2" />
                </svg>
                Recruiter
              </button>
            </div>

            {/* Email Field */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Email Address
              </label>
              <div className="relative">
                <svg
                  className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <rect x="2" y="4" width="20" height="16" rx="2" />
                  <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" />
                </svg>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@company.com"
                  className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-lg text-sm text-gray-800 placeholder-gray-400 outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-100 transition-all"
                />
              </div>
            </div>

            {/* Password Field */}
            <div className="mb-1">
              <div className="flex justify-end mb-1.5">
                <a
                  href="#"
                  className="text-xs text-purple-600 font-medium hover:text-purple-700"
                >
                  Forgot?
                </a>
              </div>
              <div className="relative">
                <svg
                  className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <rect x="3" y="11" width="18" height="11" rx="2" />
                  <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                </svg>
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-10 pr-10 py-2.5 border border-gray-200 rounded-lg text-sm text-gray-800 placeholder-gray-400 outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-100 transition-all"
                />
                <button
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  aria-label="Toggle password visibility"
                >
                  {showPassword ? (
                    <svg
                      className="w-4 h-4"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                    >
                      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94" />
                      <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19" />
                      <line x1="1" y1="1" x2="23" y2="23" />
                    </svg>
                  ) : (
                    <svg
                      className="w-4 h-4"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                    >
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                      <circle cx="12" cy="12" r="3" />
                    </svg>
                  )}
                </button>
              </div>
            </div>

            {/* Remember Me */}
            <label className="flex items-center gap-2 text-sm text-gray-500 cursor-pointer mb-5 mt-3">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                className="accent-purple-600 w-3.5 h-3.5"
              />
              Remember me
            </label>

            {/* Sign In Button */}
            <button className="w-full bg-purple-600 hover:bg-purple-700 text-white font-semibold py-3 rounded-xl text-sm transition-colors mb-5">
              Sign in to your account
            </button>

            {/* Divider */}
            <div className="flex items-center gap-3 mb-4">
              <hr className="flex-1 border-gray-200" />
              <span className="text-xs text-gray-400">Or continue with</span>
              <hr className="flex-1 border-gray-200" />
            </div>

            {/* Google Button */}
            <button className="w-full border border-gray-200 hover:bg-gray-50 text-gray-700 text-sm font-medium py-2.5 rounded-xl flex items-center justify-center gap-2 transition-colors mb-5">
              <svg width="16" height="16" viewBox="0 0 18 18">
                <path
                  fill="#4285F4"
                  d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.258h2.908c1.702-1.567 2.684-3.875 2.684-6.615z"
                />
                <path
                  fill="#34A853"
                  d="M9 18c2.43 0 4.467-.806 5.956-2.18l-2.908-2.259c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332C2.438 15.983 5.482 18 9 18z"
                />
                <path
                  fill="#FBBC05"
                  d="M3.964 10.71c-.18-.54-.282-1.117-.282-1.71s.102-1.17.282-1.71V4.958H.957C.347 6.173 0 7.548 0 9s.348 2.827.957 4.042l3.007-2.332z"
                />
                <path
                  fill="#EA4335"
                  d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0 5.482 0 2.438 2.017.957 4.958L3.964 7.29C4.672 5.163 6.656 3.58 9 3.58z"
                />
              </svg>
              Google account
            </button>

            {/* Sign Up Link */}
            <p className="text-center text-sm text-gray-400">
              Don't have an account?{" "}
              <a
                href="#"
                className="text-purple-600 font-semibold hover:text-purple-700"
              >
                Sign up
              </a>
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="text-center py-4">
        <a href="#" className="text-xs text-gray-400 hover:text-gray-600 mx-3">
          Privacy Policy
        </a>
        <a href="#" className="text-xs text-gray-400 hover:text-gray-600 mx-3">
          Terms of Service
        </a>
        <a href="#" className="text-xs text-gray-400 hover:text-gray-600 mx-3">
          Contact Support
        </a>
      </footer>
    </div>
  );
};

export default Login;
