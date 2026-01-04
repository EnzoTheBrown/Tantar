
import { ReactNode } from "react";
import { PublicHeader } from "./PublicHeader";
import { PublicFooter } from "./PublicFooter";

interface PublicLayoutProps {
  children: ReactNode;
}

export const PublicLayout = ({ children }: PublicLayoutProps) => {
  return (
    <div className="flex flex-col min-h-screen bg-gradient-to-br from-[#000033] to-[#0000cc] text-white">
      <PublicHeader />
      <main className="flex-1 py-16">
        {children}
      </main>
      <PublicFooter />
    </div>
  );
};
