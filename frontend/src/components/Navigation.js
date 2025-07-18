import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { 
  Box, 
  Tabs, 
  Tab, 
  Paper 
} from '@mui/material';
import { 
  Dashboard as DashboardIcon,
  VideoCall,
  VideoLibrary,
  Quiz,
  RecordVoiceOver
} from '@mui/icons-material';

function Navigation() {
  const navigate = useNavigate();
  const location = useLocation();
  
  const tabs = [
    { label: 'Dashboard', path: '/', icon: <DashboardIcon /> },
    { label: 'Record', path: '/record', icon: <VideoCall /> },
    { label: 'Recordings', path: '/recordings', icon: <VideoLibrary /> },
    { label: 'Questions', path: '/questions', icon: <Quiz /> },
    { label: 'Speech Test', path: '/speech-test', icon: <RecordVoiceOver /> },
  ];
  
  const currentTab = tabs.findIndex(tab => tab.path === location.pathname);
  
  const handleTabChange = (event, newValue) => {
    navigate(tabs[newValue].path);
  };
  
  return (
    <Paper elevation={1} sx={{ borderRadius: 2 }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs 
          value={currentTab >= 0 ? currentTab : 0} 
          onChange={handleTabChange}
          variant="fullWidth"
          sx={{
            '& .MuiTab-root': {
              minHeight: 64,
              textTransform: 'none',
              fontSize: '0.95rem',
              fontWeight: 500,
            },
          }}
        >
          {tabs.map((tab, index) => (
            <Tab
              key={index}
              icon={tab.icon}
              label={tab.label}
              iconPosition="start"
              sx={{ gap: 1 }}
            />
          ))}
        </Tabs>
      </Box>
    </Paper>
  );
}

export default Navigation;
