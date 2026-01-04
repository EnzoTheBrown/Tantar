
import { Users, UserRound } from "lucide-react";
import type { Company } from "../types/api";

interface OrganigramViewProps {
  company: Company;
}

export const OrganigramView = ({ company }: OrganigramViewProps) => {
  // Check if roles or shares are available
  const hasRoles = company.roles && company.roles.length > 0;
  const hasShares = company.shares && company.shares.length > 0;

  // Calculate total shares for percentage calculation
  const totalShares = hasShares 
    ? company.shares!.reduce((sum, share) => sum + (share.shares || 0), 0)
    : 0;

  if (!hasRoles && !hasShares) {
    return (
      <div className="text-center py-4 text-gray-500">
        <Users className="mx-auto h-10 w-10 text-gray-300 mb-2" />
        <p>Aucune information sur l'organisation disponible</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {hasRoles && (
        <div>
          <h3 className="text-sm font-semibold mb-3 flex items-center text-blue-600">
            <Users className="w-4 h-4 mr-2" />
            Rôles et responsabilités
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {company.roles?.map((role, index) => (
              <div 
                key={`${role.name}-${index}`} 
                className="bg-white p-3 rounded-md border border-gray-200 shadow-sm"
              >
                <div className="flex items-start gap-3">
                  <div className="h-8 w-8 rounded-full bg-gray-100 flex items-center justify-center flex-shrink-0">
                    <UserRound className="h-4 w-4 text-gray-500" />
                  </div>
                  <div>
                    <div className="text-xs uppercase text-gray-500 font-medium">{role.name || "UNKNOWN"}</div>
                    <div className="font-medium">{role.person.name}</div>
                    <div className="text-xs mt-1 text-blue-600">
                      {role.person.is_moral ? 'Personne morale' : 'Personne physique'}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {hasShares && (
        <div>
          <h3 className="text-sm font-semibold mb-3 flex items-center text-blue-600">
            <Users className="w-4 h-4 mr-2" />
            Actionnariat
          </h3>
          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <div className="space-y-3">
              {company.shares?.map((share, index) => {
                // Calculate percentage from shares
                const calculatedPercentage = totalShares > 0 && share.shares 
                  ? ((share.shares / totalShares) * 100).toFixed(2) 
                  : null;
                
                return (
                  <div key={`${share.person.name}-${index}`} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="h-6 w-6 rounded-full bg-blue-100 flex items-center justify-center">
                        <UserRound className="h-3 w-3 text-blue-500" />
                      </div>
                      <span className="font-medium">{share.person.name}</span>
                      <span className="text-xs text-gray-500">
                        ({share.person.is_moral ? 'Personne morale' : 'Personne physique'})
                      </span>
                    </div>
                    <div className="font-medium text-blue-600">
                      {share.shares ? `${share.shares} actions` : ''} 
                      {calculatedPercentage ? `(${calculatedPercentage}%)` : ''}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
