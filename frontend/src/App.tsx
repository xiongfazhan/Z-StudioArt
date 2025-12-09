/**
 * PopGraph 应用主组件
 * 集成路由和认证状态管理
 * 
 * _Requirements: 9.1, 9.2, 9.3, 9.4_
 */

import { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, useNavigate } from 'react-router-dom';
import './App.css';
import { PosterGeneratorPage } from './components/PosterGeneratorPage';
import { SceneFusionPage } from './components/SceneFusionPage';
import { ProtectedRoute, PublicRoute } from './components/ProtectedRoute';
import { ErrorBoundary } from './components/common/ErrorBoundary';
import { UserInfoBar } from './components/layout/UserInfoBar';
import { BottomNavigation } from './components/layout/BottomNavigation';
import type { PageType } from './components/layout/BottomNavigation';
import { LoginPage, RegisterPage, HistoryPage, SubscriptionPage } from './pages';
import { useAuthStore } from './stores/authStore';
import { apiService } from './services/api';

/**
 * 主页面组件 - 包含海报生成和场景融合功能
 * 使用 UserInfoBar 和 BottomNavigation 组件
 */
function MainPage() {
  const [currentPage, setCurrentPage] = useState<PageType>('poster');
  const navigate = useNavigate();
  const { user, clearAuth, refreshToken } = useAuthStore();

  const handleLogout = async () => {
    try {
      if (refreshToken) {
        await apiService.logout(refreshToken);
      }
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      clearAuth();
      navigate('/login');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800">
      {/* User Info Bar - 使用独立组件 */}
      {user && <UserInfoBar user={user} onLogout={handleLogout} />}

      {/* Bottom Navigation - 使用独立组件 */}
      <BottomNavigation currentPage={currentPage} onPageChange={setCurrentPage} />

      {/* Page Content */}
      {currentPage === 'poster' && <PosterGeneratorPage />}
      {currentPage === 'scene-fusion' && <SceneFusionPage />}
    </div>
  );
}

/**
 * 应用初始化组件 - 处理认证状态恢复
 */
function AppInitializer({ children }: { children: React.ReactNode }) {
  const { refreshToken, setAuth, clearAuth, setInitialized, isInitialized } = useAuthStore();

  useEffect(() => {
    const initAuth = async () => {
      // 如果有 refresh token，尝试恢复会话
      if (refreshToken) {
        try {
          const tokenResponse = await apiService.refreshToken(refreshToken);
          const userResponse = await apiService.getCurrentUser();
          setAuth(userResponse, tokenResponse.access_token, tokenResponse.refresh_token);
        } catch (err) {
          console.error('Session restore failed:', err);
          clearAuth();
        }
      }
      setInitialized();
    };

    if (!isInitialized) {
      initAuth();
    }
  }, [refreshToken, setAuth, clearAuth, setInitialized, isInitialized]);

  // 显示加载状态
  if (!isInitialized) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#0f172a]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-lg shadow-indigo-500/30 animate-pulse">
            <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div className="animate-spin rounded-full h-8 w-8 border-2 border-indigo-500/30 border-t-indigo-500" />
        </div>
      </div>
    );
  }

  return <>{children}</>;
}

/**
 * 应用根组件
 * 使用 ErrorBoundary 包装整个应用以捕获错误
 */
function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <AppInitializer>
          <Routes>
            {/* 公开路由 - 登录页 */}
            <Route
              path="/login"
              element={
                <PublicRoute>
                  <LoginPage />
                </PublicRoute>
              }
            />
            
            {/* 公开路由 - 注册页 */}
            <Route
              path="/register"
              element={
                <PublicRoute>
                  <RegisterPage />
                </PublicRoute>
              }
            />
            
            {/* 受保护路由 - 主页面 */}
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <MainPage />
                </ProtectedRoute>
              }
            />
            
            {/* 受保护路由 - 历史记录页面 */}
            <Route
              path="/history"
              element={
                <ProtectedRoute>
                  <HistoryPage />
                </ProtectedRoute>
              }
            />
            
            {/* 受保护路由 - 订阅页面 */}
            <Route
              path="/subscription"
              element={
                <ProtectedRoute>
                  <SubscriptionPage />
                </ProtectedRoute>
              }
            />
            
            {/* 其他路由重定向到首页 */}
            <Route path="*" element={<ProtectedRoute><MainPage /></ProtectedRoute>} />
          </Routes>
        </AppInitializer>
      </BrowserRouter>
    </ErrorBoundary>
  );
}

export default App;
