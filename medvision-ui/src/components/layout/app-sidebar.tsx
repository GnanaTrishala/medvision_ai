"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  FileText,
  History,
  LayoutDashboard,
  LogOut,
  Scan,
  Stethoscope,
} from "lucide-react";
import { cn } from "~/lib/utils";
import { useAuth } from "~/context/auth-context";
import { Button } from "~/components/ui/button";

const links = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/analyze", label: "Analyze X-Ray", icon: Scan },
  { href: "/history", label: "History", icon: History },
];

export function AppSidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  return (
    <aside className="flex h-full w-64 flex-col border-r border-border bg-card/50 backdrop-blur-xl">
      <div className="flex items-center gap-2 border-b border-border px-5 py-5">
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-teal-600 text-white">
          <Stethoscope className="h-5 w-5" />
        </div>
        <div>
          <p className="text-sm font-semibold tracking-tight">MedVision AI</p>
          <p className="text-xs text-muted-foreground">Clinical Intelligence</p>
        </div>
      </div>

      <nav className="flex-1 space-y-1 p-3">
        {links.map(({ href, label, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            className={cn(
              "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
              pathname === href
                ? "bg-teal-600/10 text-teal-700 dark:text-teal-300"
                : "text-muted-foreground hover:bg-muted hover:text-foreground",
            )}
          >
            <Icon className="h-4 w-4" />
            {label}
          </Link>
        ))}
      </nav>

      <div className="border-t border-border p-4">
        <div className="mb-3 flex items-center gap-2 rounded-lg bg-muted/60 px-3 py-2">
          <Activity className="h-4 w-4 text-teal-600" />
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium">{user?.full_name}</p>
            <p className="truncate text-xs text-muted-foreground">{user?.email}</p>
          </div>
        </div>
        <Button variant="outline" className="w-full" onClick={logout}>
          <LogOut className="mr-2 h-4 w-4" />
          Sign out
        </Button>
        <p className="mt-3 flex items-center gap-1 text-[10px] text-muted-foreground">
          <FileText className="h-3 w-3" />
          Research & decision support only
        </p>
      </div>
    </aside>
  );
}
