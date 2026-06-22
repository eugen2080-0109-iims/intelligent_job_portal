import { useState } from "react";

const jobs = [
  {
    id: 1,
    title: "Senior UX Designer",
    company: "Google Inc.",
    location: "Mountain View, CA",
    match: 98,
    salary: "40k - 50k /month",
    bookmarked: false,
    icon: "🚀",
    iconBg: "bg-purple-100",
  },
  {
    id: 2,
    title: "Product Design Lead",
    company: "Airbnb",
    location: "San Francisco, CA",
    match: 92,
    salary: "60k - 800k /month",
    bookmarked: true,
    icon: "⬡",
    iconBg: "bg-purple-100",
  },
  {
    id: 3,
    title: "Principal UX Engineer",
    company: "Amazon",
    location: "Seattle, WA",
    match: 79,
    salary: "80k - 85k /month",
    bookmarked: false,
    icon: "🧍",
    iconBg: "bg-purple-100",
  },
  {
    id: 4,
    title: "Product Design Lead",
    company: "Airbnb",
    location: "San Francisco, CA",
    match: 92,
    salary: "60k - 800k /month",
    bookmarked: true,
    icon: "⬡",
    iconBg: "bg-purple-100",
  },
  {
    id: 5,
    title: "Visual UI Architect",
    company: "Microsoft",
    location: "Remote",
    match: 85,
    salary: "60k - 65k /month",
    bookmarked: false,
    icon: "⊞",
    iconBg: "bg-purple-100",
  },
];

const CompanyIcon = ({ job }) => {
  const icons = {
    "Google Inc.": (
      <svg viewBox="0 0 24 24" className="w-5 h-5" fill="none">
        <path
          d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z"
          fill="#e8eaed"
        />
        <path
          d="M17.6 12.2c0-.4-.03-.8-.1-1.2H12v2.3h3.1c-.1.8-.7 2-1.9 2.6l3 2.3c1.7-1.6 2.7-3.9 2.7-6.3z"
          fill="#7c3aed"
          opacity=".6"
        />
        <path
          d="M12 18c1.6 0 3-.5 4-1.4l-3-2.3c-.5.4-1.2.6-2 .6-1.5 0-2.8-1-3.3-2.4H5.6v2.4C6.8 16.8 9.2 18 12 18z"
          fill="#7c3aed"
          opacity=".4"
        />
      </svg>
    ),
    Airbnb: (
      <svg viewBox="0 0 24 24" className="w-5 h-5" fill="none">
        <path
          d="M12 2L7 7l5 5-5 5 5 5 5-5-5-5 5-5-5-5z"
          fill="#7c3aed"
          opacity=".5"
        />
      </svg>
    ),
    Amazon: (
      <svg viewBox="0 0 24 24" className="w-5 h-5" fill="none">
        <circle cx="12" cy="8" r="4" stroke="#7c3aed" strokeWidth="1.5" />
        <path
          d="M4 20c0-4 3.6-7 8-7s8 3 8 7"
          stroke="#7c3aed"
          strokeWidth="1.5"
          strokeLinecap="round"
        />
      </svg>
    ),
    Microsoft: (
      <svg viewBox="0 0 24 24" className="w-5 h-5" fill="none">
        <rect
          x="3"
          y="3"
          width="8"
          height="8"
          fill="#7c3aed"
          opacity=".5"
          rx="1"
        />
        <rect
          x="13"
          y="3"
          width="8"
          height="8"
          fill="#7c3aed"
          opacity=".5"
          rx="1"
        />
        <rect
          x="3"
          y="13"
          width="8"
          height="8"
          fill="#7c3aed"
          opacity=".5"
          rx="1"
        />
        <rect
          x="13"
          y="13"
          width="8"
          height="8"
          fill="#7c3aed"
          opacity=".5"
          rx="1"
        />
      </svg>
    ),
  };
  return (
    icons[job.company] || (
      <svg viewBox="0 0 24 24" className="w-5 h-5" fill="none">
        <rect
          x="3"
          y="3"
          width="18"
          height="18"
          rx="3"
          stroke="#7c3aed"
          strokeWidth="1.5"
        />
      </svg>
    )
  );
};

const BookmarkIcon = ({ filled }) => (
  <svg
    viewBox="0 0 24 24"
    className="w-5 h-5"
    fill={filled ? "#7c3aed" : "none"}
    stroke={filled ? "#7c3aed" : "#9ca3af"}
    strokeWidth="1.8"
  >
    <path
      d="M5 3h14a1 1 0 011 1v17l-7-4-7 4V4a1 1 0 011-1z"
      strokeLinejoin="round"
    />
  </svg>
);

const JobCard = ({ job }) => {
  const [bookmarked, setBookmarked] = useState(job.bookmarked);

  return (
    <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 flex flex-col gap-4 hover:shadow-md transition-shadow duration-200">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-purple-50 flex items-center justify-center flex-shrink-0">
            <CompanyIcon job={job} />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 text-sm leading-tight">
              {job.title}
            </h3>
            <p className="text-gray-400 text-xs mt-0.5">
              {job.company} • {job.location}
            </p>
          </div>
        </div>
        <button
          onClick={() => setBookmarked(!bookmarked)}
          className="mt-0.5 hover:scale-110 transition-transform"
          aria-label="Bookmark job"
        >
          <BookmarkIcon filled={bookmarked} />
        </button>
      </div>

      {/* AI Match */}
      <div>
        <div className="flex items-center justify-between mb-1.5">
          <span className="text-xs font-semibold text-purple-600 tracking-wide">
            AI MATCH
          </span>
          <span className="text-sm font-bold text-purple-600">
            {job.match}%
          </span>
        </div>
        <div className="w-full bg-purple-100 rounded-full h-1.5">
          <div
            className="bg-purple-600 h-1.5 rounded-full transition-all duration-500"
            style={{ width: `${job.match}%` }}
          />
        </div>
      </div>

      {/* Salary + Apply */}
      <div className="flex items-center justify-between mt-1">
        <span className="text-sm text-gray-500">{job.salary}</span>
        <button className="bg-purple-600 hover:bg-purple-700 text-white text-sm font-medium px-5 py-2 rounded-full transition-colors duration-200">
          Apply Now
        </button>
      </div>
    </div>
  );
};

export default function JobSeekerDashboard() {
  const [activeNav, setActiveNav] = useState("Home");
  const navLinks = ["Home", "Jobs", "Applications", "Saved Jobs", "Profile"];

  return (
    <div className="min-h-screen bg-gray-100 font-sans">
      {/* Outer wrapper */}
      <div className="max-w-6xl mx-auto bg-gray-100 min-h-screen">
        {/* Small label */}
        <p className="text-xs text-gray-500 pt-4 px-6 mb-2">
          Job Seeker Dashboard
        </p>

        {/* Main card */}
        <div className="bg-white mx-0 rounded-2xl shadow-sm overflow-hidden">
          {/* Navbar */}
          <nav className="flex items-center justify-between px-8 py-4 border-b border-gray-100">
            {/* Logo */}
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-purple-600 flex items-center justify-center">
                <svg
                  viewBox="0 0 24 24"
                  className="w-5 h-5 text-white"
                  fill="white"
                >
                  <path d="M12 2L4 7v10l8 5 8-5V7l-8-5z" opacity=".3" />
                  <path d="M12 2l8 5-8 5-8-5 8-5z" />
                </svg>
              </div>
              <span className="font-bold text-gray-900 text-sm">
                Intelligent Job Portal
              </span>
            </div>

            {/* Nav links */}
            <div className="flex items-center gap-7">
              {navLinks.map((link) => (
                <button
                  key={link}
                  onClick={() => setActiveNav(link)}
                  className={`text-sm font-medium transition-colors ${
                    activeNav === link
                      ? "text-purple-600"
                      : "text-gray-500 hover:text-gray-800"
                  }`}
                >
                  {link}
                </button>
              ))}
            </div>

            {/* Right actions */}
            <div className="flex items-center gap-3">
              {/* Search */}
              <div className="flex items-center gap-2 bg-gray-50 rounded-full px-3 py-1.5 border border-gray-200">
                <svg
                  className="w-4 h-4 text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  viewBox="0 0 24 24"
                >
                  <circle cx="11" cy="11" r="8" />
                  <path d="M21 21l-4.35-4.35" strokeLinecap="round" />
                </svg>
                <input
                  type="text"
                  placeholder="Search opportunities..."
                  className="bg-transparent text-xs text-gray-500 outline-none w-32 placeholder-gray-400"
                />
              </div>

              {/* Bell */}
              <button className="relative w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-50">
                <svg
                  className="w-5 h-5 text-gray-500"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  viewBox="0 0 24 24"
                >
                  <path
                    d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"
                    strokeLinecap="round"
                  />
                  <path d="M13.73 21a2 2 0 01-3.46 0" strokeLinecap="round" />
                </svg>
                <span className="absolute top-0.5 right-0.5 w-2 h-2 bg-red-500 rounded-full border border-white" />
              </button>

              {/* Avatar */}
              <div className="w-8 h-8 rounded-full overflow-hidden border-2 border-purple-200">
                <div className="w-full h-full bg-gradient-to-br from-purple-400 to-indigo-500 flex items-center justify-center">
                  <span className="text-white text-xs font-semibold">JD</span>
                </div>
              </div>
            </div>
          </nav>

          {/* Main content */}
          <div className="px-8 py-8">
            {/* Section header */}
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-xl font-bold text-gray-900">
                  Recommended Jobs
                </h2>
                <p className="text-gray-400 text-sm mt-0.5">
                  Based on your skills and preference
                </p>
              </div>
              <div className="flex items-center gap-2">
                <button className="flex items-center gap-1.5 border border-gray-200 rounded-full px-4 py-1.5 text-sm text-gray-600 hover:bg-gray-50 transition-colors">
                  <svg
                    className="w-3.5 h-3.5"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    viewBox="0 0 24 24"
                  >
                    <line x1="4" y1="6" x2="20" y2="6" />
                    <line x1="8" y1="12" x2="20" y2="12" />
                    <line x1="12" y1="18" x2="20" y2="18" />
                  </svg>
                  Filter
                </button>
                <button className="flex items-center gap-1.5 border border-gray-200 rounded-full px-4 py-1.5 text-sm text-gray-600 hover:bg-gray-50 transition-colors">
                  <svg
                    className="w-3.5 h-3.5"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    viewBox="0 0 24 24"
                  >
                    <path d="M3 6l9 6 9-6M3 12l9 6 9-6" strokeLinecap="round" />
                  </svg>
                  Sort
                </button>
              </div>
            </div>

            {/* Job grid */}
            <div className="grid grid-cols-3 gap-5">
              {jobs.map((job) => (
                <JobCard key={job.id} job={job} />
              ))}
            </div>
          </div>

          {/* Footer */}
          <footer className="border-t border-gray-100 px-8 py-5 mt-4">
            <div className="flex justify-end gap-6">
              {["Help Center", "Terms of Service", "Privacy Policy"].map(
                (link) => (
                  <a
                    key={link}
                    href="#"
                    className="text-sm text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    {link}
                  </a>
                ),
              )}
            </div>
          </footer>
        </div>
      </div>
    </div>
  );
}
