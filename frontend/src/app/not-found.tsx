import Link from "next/link";
import { ArrowLeft, Cpu } from "lucide-react";
import { Button } from "@/components/common/Button";

export default function NotFound() {
  return (
    <div className="min-h-screen bg-surface-base flex flex-col items-center justify-center p-6 text-center">
      <div className="w-12 h-12 rounded-xl bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 flex items-center justify-center mb-6">
        <Cpu className="w-6 h-6" />
      </div>
      <h1 className="text-3xl font-bold text-white mb-2 font-mono">404 - Node Not Found</h1>
      <p className="text-sm text-slate-400 max-w-md mb-8">
        The workflow or destination you requested does not exist in the active execution mesh.
      </p>
      <Link href="/dashboard">
        <Button variant="primary" leftIcon={<ArrowLeft className="w-4 h-4" />}>
          Back to Dashboard
        </Button>
      </Link>
    </div>
  );
}
