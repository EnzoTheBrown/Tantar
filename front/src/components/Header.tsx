
import { BellIcon, LogOutIcon, HelpCircleIcon, Settings2Icon, FileText, Building2, LayoutDashboard } from "lucide-react";
import { Button } from "./ui/button";
import { useAuth } from "@/contexts/AuthContext";
import { Link, useLocation } from "react-router-dom";
import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
  navigationMenuTriggerStyle,
} from "@/components/ui/navigation-menu";
import { cn } from "@/lib/utils";

export const Header = () => {
  const { logout, isAuthenticated } = useAuth();
  const location = useLocation();
  const isPublicPage = ["/", "/about", "/contact", "/legal", "/faq", "/features"].includes(location.pathname);

  // If we're on a public page, we don't want to show the header
  // as it's handled by the PublicLayout component
  if (isPublicPage) {
    return null;
  }

  return (
    <header className="border-b border-gray-200 bg-white py-3 px-6 sticky top-0 z-10 shadow-sm">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-6">
          <Link to="/">
            <h1 className="text-2xl font-bold text-blue-600">Tantar</h1>
          </Link>

          {isAuthenticated && (
            <NavigationMenu>
              <NavigationMenuList>
                <NavigationMenuItem>
                  <Link to="/dashboard">
                    <NavigationMenuLink className={cn(navigationMenuTriggerStyle(), "group flex items-center gap-1")}>
                      <LayoutDashboard className="h-4 w-4" />
                      <span>Tableau de bord</span>
                    </NavigationMenuLink>
                  </Link>
                </NavigationMenuItem>
                <NavigationMenuItem>
                  <Link to="/companies">
                    <NavigationMenuLink className={cn(navigationMenuTriggerStyle(), "group flex items-center gap-1")}>
                      <Building2 className="h-4 w-4" />
                      <span>Sociétés</span>
                    </NavigationMenuLink>
                  </Link>
                </NavigationMenuItem>
                <NavigationMenuItem>
                  <Link to="/files">
                    <NavigationMenuLink className={cn(navigationMenuTriggerStyle(), "group flex items-center gap-1")}>
                      <FileText className="h-4 w-4" />
                      <span>Fichiers</span>
                    </NavigationMenuLink>
                  </Link>
                </NavigationMenuItem>
              </NavigationMenuList>
            </NavigationMenu>
          )}
        </div>
        
        <div className="flex items-center space-x-2">
          {isAuthenticated && (
            <>
              <Button variant="ghost" size="icon" className="rounded-full hover:bg-blue-50">
                <BellIcon className="h-5 w-5 text-gray-600" />
              </Button>
              <Button variant="ghost" size="icon" className="rounded-full hover:bg-blue-50">
                <HelpCircleIcon className="h-5 w-5 text-gray-600" />
              </Button>
              <Button variant="ghost" size="icon" className="rounded-full hover:bg-blue-50">
                <Settings2Icon className="h-5 w-5 text-gray-600" />
              </Button>
              <Button 
                variant="ghost" 
                size="icon" 
                onClick={logout} 
                className="rounded-full hover:bg-red-50"
                title="Se déconnecter"
              >
                <LogOutIcon className="h-5 w-5 text-red-500" />
              </Button>
            </>
          )}
        </div>
      </div>
    </header>
  );
};
