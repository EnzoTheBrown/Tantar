
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom'; 
import { Header } from '../components/Header';
import { DashboardContent } from '../components/DashboardContent';
import { Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import * as api from '../api';
import type { Company, File } from '@/types/api';

export const Dashboard = () => {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [recentFiles, setRecentFiles] = useState<File[]>([]);
  const [addedFiles, setAddedFiles] = useState<File[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [companiesRes, filesRes] = await Promise.all([
          api.getCompanies(),
          api.getFiles(undefined, 'watched_at')
        ]);
        
        // Ensure all companies have the required fields in the details object
        const enhancedCompanies: Company[] = companiesRes.map((company: Company) => ({
          ...company,
          details: company.details || {
            siren: company.siren || '',
            name: company.name,
            naf_code: 'N/A',
            activity: 'N/A',
            capital: Math.floor(Math.random() * 100000) + 10000,
            juridic_form: ['SAS', 'SARL', 'SA'][Math.floor(Math.random() * 3)]
          }
        }));
        
        setCompanies(enhancedCompanies);
        
        // Get recently watched files
        const recentWatched = filesRes.filter((f: File) => f.watched_at).slice(0, 5);
        setRecentFiles(recentWatched);
        
        // Get recently added files
        const recentAdded = await api.getFiles(undefined, 'created_at');
        setAddedFiles(recentAdded.slice(0, 5));
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();

    // Setup WebSocket connection
    const token = localStorage.getItem('token');
    if (!token) return;

    const wsUrl = `wss://app.tantar.ai/ws/${token}`;
    const ws = new WebSocket(wsUrl);

    ws.onmessage = async (event) => {
      const data = JSON.parse(event.data);
      console.log('New websocket event:', data);

      if (data.type === 'new_company') {
        toast.success('Nouvelle société ajoutée', {
          description: `${data.company.name} a été ajoutée à votre portefeuille`,
        });
        // Refresh companies list
        fetchData();
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    return () => {
      ws.close();
    };
  }, []);

  const handleCompanyClick = (companyId: string) => {
    navigate(`/timeline/${companyId}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50">
        <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
        <p className="mt-4 text-gray-600">Loading your dashboard...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      <Header />
      <DashboardContent
        companies={companies}
        recentFiles={recentFiles}
        addedFiles={addedFiles}
        onCompanyClick={handleCompanyClick}
        onFilesUpdated={setAddedFiles}
      />
    </div>
  );
};

export default Dashboard;
