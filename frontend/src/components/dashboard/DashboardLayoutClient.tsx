"use client";

import React, { useState } from "react";
import { Sidebar } from "./Sidebar";

export const DashboardLayoutClient: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);

  return (
    <div className="flex min-h-screen bg-surface-base text-slate-100 relative">
      {/* Desktop Sidebar (hidden on mobile) */}
      <Sidebar className="hidden md:flex" />

      {/* Mobile Drawer (visible when open) */}
      {mobileSidebarOpen && (
        <div className="fixed inset-0 z-50 md:hidden flex">
          <div
            className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm"
            onClick={() => setMobileSidebarOpen(false)}
          />
          <div className="relative z-10 w-64 bg-slate-950 h-full shadow-2xl">
            <Sidebar onCloseMobile={() => setMobileSidebarOpen(false)} />
          </div>
        </div>
      )}

      {/* Main Viewport */}
      <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        {React.Children.map(children, (child) => {
          if (React.isValidElement(child)) {
            // pass onOpenMobileMenu down if supported
            return React.cloneElement(child as React.ReactElement<any>, {
              onOpenMobileMenu: () => setMobileSidebarOpen(true),
            });
          }
          return child;
        })}
      </div>
    </div>
  );
};
