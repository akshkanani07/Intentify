import Link from "next/link";

export default function NotFound() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-[#070b14] text-slate-100 p-4">
      <h2 className="text-2xl font-bold mb-2">404 — Page Not Found</h2>
      <p className="text-slate-400 mb-6">The requested page does not exist.</p>
      <Link
        href="/"
        className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm transition-colors"
      >
        Return to Platform
      </Link>
    </div>
  );
}
