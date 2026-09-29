"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function AdminRootPage() {
  const router = useRouter();

  useEffect(() => {
    router.replace("/admin/dashboard");
  }, [router]);

  return (
    <div className="flex items-center justify-center h-64 text-sm font-mono text-[#7c8c9a]">
      <div className="flex items-center gap-2">
        <div className="w-4 h-4 border-2 border-[#00ed64] border-t-transparent rounded-full animate-spin" />
        <span>Loading Administrator Console...</span>
      </div>
    </div>
  );
}
