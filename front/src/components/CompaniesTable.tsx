
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { Search, ChevronDown, ChevronUp } from "lucide-react";
import { Button } from "./ui/button";
import { useState } from "react";
import type { Company as ApiCompany } from "../types/api";
import { OrganigramView } from "./OrganigramView";

interface CompaniesTableProps {
  companies: ApiCompany[];
  onCompanyClick?: (companyId: string) => void;
  showHeader?: boolean;
}

export const CompaniesTable = ({ companies, onCompanyClick, showHeader = false }: CompaniesTableProps) => {
  const [expandedCompanyId, setExpandedCompanyId] = useState<string | null>(null);

  const toggleExpand = (companyId: string) => {
    setExpandedCompanyId(expandedCompanyId === companyId ? null : companyId);
  };

  return (
    <div className="bg-white rounded-lg">
      {showHeader && (
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold">Mon portefeuille</h2>
        </div>
      )}
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[50px]"></TableHead>
              <TableHead className="font-medium text-sm w-[30%]">Dénomination</TableHead>
              <TableHead className="font-medium text-sm w-[20%]">SIREN</TableHead>
              <TableHead className="font-medium text-sm w-[40%]">Forme</TableHead>
              <TableHead className="w-[50px]"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {companies.map((company) => (
              <>
                <TableRow key={company.original_id || company.siren} className="text-sm">
                  <TableCell className="py-2 w-[50px]">
                    <Button 
                      variant="ghost" 
                      size="sm"
                      className="h-7 w-7 p-0"
                      onClick={() => toggleExpand(company.original_id || company.siren || '')}
                    >
                      {expandedCompanyId === (company.original_id || company.siren) ? 
                        <ChevronUp className="h-3.5 w-3.5" /> : 
                        <ChevronDown className="h-3.5 w-3.5" />}
                    </Button>
                  </TableCell>
                  <TableCell className="font-medium py-2 w-[30%]">{company.name}</TableCell>
                  <TableCell className="py-2 w-[20%]">{company.siren || 'N/A'}</TableCell>
                  <TableCell className="py-2 w-[40%]">{company.details?.juridic_form}</TableCell>
                  <TableCell className="py-2 w-[50px]">
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      className="h-7 w-7 p-0"
                      onClick={() => onCompanyClick && onCompanyClick(company.original_id || company.siren || '')}
                    >
                      <Search className="h-3.5 w-3.5" />
                    </Button>
                  </TableCell>
                </TableRow>
                {expandedCompanyId === (company.original_id || company.siren) && (
                  <TableRow>
                    <TableCell colSpan={5} className="p-0 border-t-0">
                      <div className="bg-gray-50 p-4 border-t border-gray-100">
                        <OrganigramView company={company} />
                      </div>
                    </TableCell>
                  </TableRow>
                )}
              </>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
};
